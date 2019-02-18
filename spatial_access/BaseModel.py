# Logan Noel (github.com/lmnoel)
#
# ©2017-2019, Center for Spatial Data Science

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point
import matplotlib as mpl
import matplotlib.patches as mpatches
import matplotlib.pyplot
import json
from spatial_access.p2p import TransitMatrix

from spatial_access.SpatialAccessExceptions import SourceDataNotFoundException
from spatial_access.SpatialAccessExceptions import DestDataNotFoundException
from spatial_access.SpatialAccessExceptions import SourceDataNotParsableException
from spatial_access.SpatialAccessExceptions import DestDataNotParsableException
from spatial_access.SpatialAccessExceptions import PrimaryDataNotFoundException
from spatial_access.SpatialAccessExceptions import SecondaryDataNotFoundException
from spatial_access.SpatialAccessExceptions import ShapefileNotFoundException
from spatial_access.SpatialAccessExceptions import SpatialIndexNotMatchedException
from spatial_access.SpatialAccessExceptions import TooManyCategoriesToPlotException
from spatial_access.SpatialAccessExceptions import UnexpectedPlotColumnException
from spatial_access.SpatialAccessExceptions import AggregateOutputTypeNotExpectedException


import os.path
import logging


class ModelData(object):
    """
    A parent class to hold/process data for more advanced geospatial
    models like HSSAModel and PCSpendModel. The 'upper' argument in
    the __init__ is the time (in seconds), above which a source and dest
    are considered to be out of range of each other.
    """

    def __init__(self, network_type, sources_filename,
                 destinations_filename,
                 source_column_names=None, dest_column_names=None,
                 debug=False):
        self.network_type = network_type
        self._sp_matrix = None
        self.dests = None
        self.sources = None

        self.sources_filename = sources_filename
        self.destinations_filename = destinations_filename

        # column_names and file_hints are similar, both map intended_name->actual_data_name
        # the difference is column names should be complete/contain all needed fields
        self.source_column_names = source_column_names
        self.dest_column_names = dest_column_names

        # hints are partial/potentially incomplete, and supplied
        # by p2p.TransitMatrix
        self._source_file_hints = None
        self._dest_file_hints = None

        self.sources_in_range = {}
        self.dests_in_range = {}

        # initialize logger
        self.logger = None
        if debug:
            self.set_logging('info')
        else:
            self.set_logging('debug')

    def write_shortest_path_matrix_to_csv(self, filename=None):
        """
        Write sp matrix to csv.
        """
        self._sp_matrix.write_csv(filename)

    def write_shortest_path_matrix_to_h5(self, filename=None):
        """
        Write sp matrix to h5.
        """
        self._sp_matrix.write_h5(filename)

    @staticmethod
    def get_output_filename(keyword, extension='csv', file_path='data/'):
        """
        Given a keyword, find an unused filename.
        """
        if file_path is None:
            file_path = "data/"
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        filename = os.path.join(file_path, '{}_0.{}'.format(keyword, extension))
        counter = 1
        while os.path.isfile(filename):
            filename = os.path.join(file_path, '{}_{}.{}'.format(keyword, counter, extension))
            counter += 1

        return filename

    def get_time(self, source, dest):
        """
        Return the time, in seconds, from source to dest.
        """
        time = self._sp_matrix.get(source, dest)

        return time

    def get_population(self, source_id):
        """
        Return the population at a source point.
        """
        return self.sources.loc[source_id, 'population']

    def get_capacity(self, dest_id):
        """
        Return the capacity value at a dest point.
        """
        return self.dests.loc[dest_id, 'capacity']

    def get_category(self, dest_id):
        """
        Return the category value at a dest point.
        """
        return self.dests.loc[dest_id, 'category']

    def get_all_categories(self):
        """
        Return a list of all categories in the dest dataset.
        """
        return set(self.dests['category'])

    def get_all_dest_ids(self):
        """
        Return all ids of destination data frame.
        """
        return list(self.dests.index)

    def get_all_source_ids(self):
        """
        Return all ids of source data frame.
        """
        return list(self.sources.index)

    def get_ids_for_category(self, category='all_categories'):
        """
        Given category, return an array of all indeces
        which match. If category is all_categories, return all indeces.
        """
        if category == 'all_categories':
            return list(self.dests.index)
        return list(self.dests[self.dests['category'] == category].index)

    def set_logging(self, level=None):
        """
        Set the logging level to debug or info
        """
        if not level:
            return

        if level == 'debug':
            logging.basicConfig(level=logging.DEBUG)
        elif level == 'info':
            logging.basicConfig(level=logging.INFO)
        else:
            return
        self.logger = logging.getLogger(__name__)

    def load_sp_matrix(self, filename=None):
        """
        Load the shortest path matrix; if a filename is supplied,
        ModelData will attempt to load from file.
        If filename is not supplied, ModelData will generate
        a shortest path matrix using p2p (must be installed).
        """

        if filename:
            self._sp_matrix = TransitMatrix(self.network_type,
                                            read_from_h5=filename)

        else:

            self._sp_matrix = TransitMatrix(self.network_type,
                                            primary_input=self.sources_filename,
                                            secondary_input=self.destinations_filename,
                                            primary_hints=self.source_column_names,
                                            secondary_hints=self.dest_column_names)
            try:
                self._sp_matrix.process()
            except PrimaryDataNotFoundException:
                raise SourceDataNotFoundException()
            except SecondaryDataNotFoundException:
                raise DestDataNotFoundException()

            # borrow hints for use in load_sources() and load_dests() if not user supplied
            if self._source_file_hints is None:
                self._source_file_hints = self._sp_matrix.primary_hints
            if self._dest_file_hints is None:
                self._dest_file_hints = self._sp_matrix.secondary_hints

        self.reload_sources()
        self.reload_dests()

    def reload_sources(self, filename=None):
        """
        Load the source points for the model (from csv).
        For each point, the table should contain:
            -unique identifier (integer or string)
            -population (integer)
        The field_mapping argument will be present if code is being called by the web app.
        Otherwise the field_mapping default value of None will be passed in, and command
        line prompts for user input will be executed.
        """

        if filename:
            self.sources_filename = filename
        try:
            self.sources = pd.read_csv(self.sources_filename)
        except FileNotFoundError:
            raise SourceDataNotFoundException()

        if self.source_column_names is None:
            # extract the column names from the table
            population = ''
            idx = ''
            lat = ''
            lon = ''

            if self._source_file_hints is not None:
                if 'idx' in self._source_file_hints:
                    idx = self._source_file_hints['idx']
                if 'population' in self._source_file_hints:
                    population = self._source_file_hints['population']
                if 'lat' in self._source_file_hints:
                    lat = self._source_file_hints['lat']
                if 'lon' in self._source_file_hints:
                    lon = self._source_file_hints['lon']

            # extract the column names from the table for whichever fields
            # were not gleaned from self.source_file_hints
            source_data_columns = self.sources.columns.values
            print('The variables in your data set are:')
            for var in source_data_columns:
                print('> ', var)
            while idx not in source_data_columns:
                idx = input('Enter the unique index variable: ')
            print('If you have no population variable, write "skip" (no quotations)')
            while population not in source_data_columns and population != 'skip':
                population = input('Enter the population variable: ')
            while lat not in source_data_columns:
                lat = input('Enter the latitude variable: ')
            while lon not in source_data_columns:
                lon = input('Enter the longitude variable: ')

            # store the col names for later use
            self.source_column_names = {'lat': lat, 'lon': lon, 'idx': idx,
                                        'population': population}

        try:
            # insert filler values for the population column if
            # user does not want to include it. need it for coverage
            if self.source_column_names['population'] == 'skip':
                self.sources['population'] = 1

            # rename columns, clean the data frame
            rename_cols = {self.source_column_names['population']: 'population',
                           self.source_column_names['lat']: 'lat',
                           self.source_column_names['lon']: 'lon'}
            self.sources.set_index(self.source_column_names['idx'], inplace=True)
            self.sources.rename(columns=rename_cols, inplace=True)
        except KeyError:
            raise SourceDataNotParsableException()

        # drop unused columns
        columns_to_keep = list(rename_cols.values())
        self.sources = self.sources[columns_to_keep]


    def reload_dests(self, filename=None):
        """
        Load the destination points for the model (from csv).
        For each point, the table should contain:
            -unique identifier (integer or string)
            -capacity value (integer or float)
            -category (string)
        The field_mapping argument will be present if code is being called by the web app.
        Otherwise the field_mapping default value of None will be passed in, and command
        line prompts for user input will be executed.
        """

        if filename:
            self.destinations_filename = filename

        try:
            self.dests = pd.read_csv(self.destinations_filename)
        except FileNotFoundError:
            raise DestDataNotFoundException()

        if self.dest_column_names is None:
            # extract the column names from the table
            category = ''
            capacity = ''
            idx = ''
            lat = ''
            lon = ''

            if self._dest_file_hints is not None:
                if 'idx' in self._dest_file_hints:
                    idx = self._dest_file_hints['idx']
                if 'category' in self._dest_file_hints:
                    category = self._dest_file_hints['category']
                if 'capacity' in self._dest_file_hints:
                    capacity = self._dest_file_hints['capacity']
                if 'lat' in self._dest_file_hints:
                    lat = self._dest_file_hints['lat']
                if 'lon' in self._dest_file_hints:
                    lon = self._dest_file_hints['lon']

            # extract the column names from the table for whichever fields
            # were not gleaned from self.dest_file_hints
            dest_data_columns = self.dests.columns.values
            print('The variables in your data set are:')
            for var in dest_data_columns:
                print('> ', var)
            while idx not in dest_data_columns:
                idx = input('Enter the unique index variable: ')
            print('If you have no capacity variable, write "skip" (no quotations)')
            while capacity not in dest_data_columns and capacity != 'skip':
                capacity = input('Enter the capacity variable: ')
            print('If you have no category variable, write "skip" (no quotations)')
            while category not in dest_data_columns and category != 'skip':
                category = input('Enter the category variable: ')
            while lat not in dest_data_columns:
                lat = input('Enter the latitude variable: ')
            while lon not in dest_data_columns:
                lon = input('Enter the longitude variable: ')
            self.dest_column_names = {'lat': lat, 'lon': lon, 'idx': idx,
                                      'category': category, 'capacity': capacity}

        try:
            # insert filler values for the capacity column if
            # user does not want to include it.
            if self.dest_column_names['capacity'] == 'skip':
                self.dests['capacity'] = 1

            # insert filler values for the category column if
            # user does not want to include it.
            if self.dest_column_names['category'] == 'skip':
                self.dests['category'] = 1

            # rename columns, clean the data frame
            rename_cols = {self.dest_column_names['lat']: 'lat', self.dest_column_names['lon']: 'lon'}
            if self.dest_column_names['capacity'] != 'skip':
                rename_cols[self.dest_column_names['capacity']] = 'capacity'
            if self.dest_column_names['category'] != 'skip':
                rename_cols[self.dest_column_names['category']] = 'category'

            self.dests.set_index(self.dest_column_names['idx'], inplace=True)
            self.dests.rename(columns=rename_cols, inplace=True)

        except KeyError:
            raise DestDataNotParsableException()

        # drop unused columns
        columns_to_keep = list(rename_cols.values())
        self.dests = self.dests[columns_to_keep]


    def get_dests_in_range_of_source(self, source_id):
        """
        Return a list of dest ids in range of the source
        """
        return self.dests_in_range[source_id]

    def get_sources_in_range_of_dest(self, dest_id):
        """
        Return a list of source ids in range of the dest
        """
        return self.sources_in_range[dest_id]

    def calculate_dests_in_range(self, upper_threshold):
        """
        Return a dictionary of lists
        """
        self.dests_in_range = self._sp_matrix.matrix_interface.get_dests_in_range(upper_threshold)

    def calculate_sources_in_range(self, upper_threshold):
        """
        Return a dictionary of lists
        """
        self.sources_in_range = self._sp_matrix.matrix_interface.get_sources_in_range(upper_threshold)

    def get_values_by_source(self, source_id, sort=False):
        """
        Get a list of (dest_id, value) pairs, with the option
        to sort in increasing order by value.
        """
        return self._sp_matrix.matrix_interface.get_values_by_source(source_id, sort)

    def get_values_by_dest(self, dest_id, sort=False):
        """
        Get a list of (source_id, value) pairs, with the option
        to sort in increasing order by value.
        """
        return self._sp_matrix.matrix_interface.get_values_by_dest(dest_id, sort)

    def get_population_in_range(self, dest_id):
        """
         Return the population within the capacity range for the given
         destination id.
        """
        cumulative_population = 0
        for source_id in self.get_sources_in_range_of_dest(dest_id):
            source_population = self.get_population(source_id)
            if source_population > 0:
                cumulative_population += source_population

        return cumulative_population

    def map_categories_to_sp_matrix(self):
        """
        Map all categories-> associated dest_ids
        """
        for dest_id in self.get_all_dest_ids():
            associated_category = self.get_category(dest_id)
            self._add_to_category_map(dest_id, associated_category)

    def _add_to_category_map(self, dest_id, category):
        """
        Map the dest_id to the category in the
        transit matrix.
        """
        self._sp_matrix.matrix_interface.add_to_category_map(dest_id, category)

    def time_to_nearest_dest(self, source_id, category):
        """
        Return the time to nearest destination for source_id
        of type category. If category is 'all_categories', return
        the time to nearest destination of any type.
        """
        if category == 'all_categories':
            return self._sp_matrix.matrix_interface.time_to_nearest_dest(source_id, None)
        else:
            return self._sp_matrix.matrix_interface.time_to_nearest_dest(source_id, category)

    def count_dests_in_range_by_categories(self, source_id, category, upper_threshold):
        """
        Return the count of destinations in range
        of the source id per category
        """
        if category == 'all_categories':
            return self._sp_matrix.matrix_interface.count_dests_in_range(source_id,
                                                                         upper_threshold,
                                                                         None)
        else:
            return self._sp_matrix.matrix_interface.count_dests_in_range(source_id,
                                                                         upper_threshold,
                                                                         category)

        # TODO: optimize this method
    def count_sum_in_range_by_categories(self, source_id, category):
        """
        Return the count of destinations in range
        of the source id per category
        """
        running_sum = 0
        for dest_id in self.get_dests_in_range_of_source(source_id):
            if self.get_category(dest_id) == category or category == 'all_categories':
                running_sum += self.get_capacity(dest_id)
        return running_sum

    def _print_data_frame(self):
        """
        Print the transit matrix.
        """
        self._sp_matrix.matrix_interface.print_data_frame()



    def _spatial_join_community_index(self, dataframe, shapefile='data/chicago_boundaries/chicago_boundaries.shp',
                                      spatial_index='community',  projection='epsg:4326'):
        """
        Return a dataframe with community area data
        """
        geometry = [Point(xy) for xy in zip(dataframe['lon'], dataframe['lat'])]
        crs = {'init': projection}
        geo_original = gpd.GeoDataFrame(dataframe, crs=crs, geometry=geometry)
        try:
            boundaries_gdf = gpd.read_file(shapefile)
        except FileNotFoundError:
            raise ShapefileNotFoundException('shapefile not found: {}'.format(shapefile))

        geo_result = gpd.sjoin(boundaries_gdf, geo_original, how='right',
                               op='intersects')

        dataframe_columns = list(dataframe.columns)

        geo_result.rename(columns={spatial_index: 'spatial_index'}, inplace=True)
        dataframe_columns.append('spatial_index')
        dataframe_columns.append('geometry')
        try:
            geo_result = geo_result[dataframe_columns]
        except KeyError:
            raise SpatialIndexNotMatchedException('Unable to match spatial_index:{}'.format(spatial_index))
        if len(geo_result) != len(dataframe):
            self.logger.warning('Length of joined dataframe ({}) != length of input dataframe ({})'
                                .format(len(geo_result), len(dataframe)))
        return geo_result

    def rejoin_results_with_coordinates(self, model_results, is_source):
        """
        Rejoin model results with coordinates.
        """
        model_results_copy = model_results.copy(deep=True)
        if is_source:
            model_results_copy['lat'] = self.sources['lat']
            model_results_copy['lon'] = self.sources['lon']
        else:
            model_results_copy['lat'] = self.dests['lat']
            model_results_copy['lon'] = self.dests['lon']
        return model_results_copy

    def build_aggregate(self, model_results, is_source, aggregation_args,
                        shapefile='data/chicago_boundaries/chicago_boundaries.shp',
                        spatial_index='community',  projection='epsg:4326',
                        rejoin_coordinates=True):
        """
        Aggregate model results.
        """
        if rejoin_coordinates:
            model_results = self.rejoin_results_with_coordinates(model_results, is_source)

        spatial_joined_results = self._spatial_join_community_index(dataframe=model_results,
                                                                    shapefile=shapefile,
                                                                    spatial_index=spatial_index,
                                                                    projection=projection)

        aggregated_results = spatial_joined_results.groupby('spatial_index').agg(aggregation_args)
        return aggregated_results

    def write_aggregated_results(self, aggregated_results, output_type='csv', output_filename=None):
        if output_filename is not None:
            output_type = output_filename.split('.')[1]
        else:
            output_filename = self.get_output_filename(keyword='aggregate',
                                                       extension=output_type,
                                                       file_path='data/')
        if output_type == 'csv':
            aggregated_results.to_csv(output_filename)
        elif output_type == 'json':
            output = {}
            for row in aggregated_results.itertuples():
                output[row[0]] = {}
                for i, column in enumerate(aggregated_results.columns):
                    output[row[0]][column] = row[i + 1]
            with open(output_filename, 'w') as file:
                json.dump(output, file)
        else:
            raise AggregateOutputTypeNotExpectedException(output_type)

    @staticmethod
    def _join_aggregated_data_with_boundaries(aggregated_results, spatial_index,
                                              shapefile='data/chicago_boundaries/chicago_boundaries.shp'):
        """
        Join aggregated results with boundary geometry.
        """
        try:
            boundaries_gdf = gpd.read_file(shapefile)
        except FileNotFoundError:
            raise ShapefileNotFoundException('shapefile not found: {}'.format(shapefile))
        columns_to_keep = list(aggregated_results.columns)
        columns_to_keep.append('geometry')
        columns_to_keep.append(spatial_index)

        results = boundaries_gdf.merge(aggregated_results, left_on=spatial_index,
                                       right_on='spatial_index', how='outer')
        results.fillna(value=0, inplace=True)
        return results[columns_to_keep]

    def plot_cdf(self, model_results, plot_type, xlabel, ylabel, title,
                 is_source, bins=100, is_density=False):
        """
        Plot a cdf of the model results
        """
        if is_source:
            cdf_eligible = model_results[self.sources['population'] > 0]
        else:
            cdf_eligible = model_results

        # initialize block parameters
        mpl.pyplot.close()
        mpl.pyplot.rcParams['axes.facecolor'] = '#cfcfd1'
        fig, ax = mpl.pyplot.subplots(figsize=(8, 4))
        ax.grid(zorder=0)

        available_colors = ['black', 'magenta', 'lime', 'red', 'black', 'orange', 'grey', 'yellow', 'brown', 'teal']
        color_keys = []
        for column in cdf_eligible.columns:
            if plot_type not in column:
                continue
            x = cdf_eligible[column]
            try:
                color = available_colors.pop(0)
            except IndexError:
                raise TooManyCategoriesToPlotException()
            patch = mpatches.Patch(color=color, label=column)
            color_keys.append(patch)
            n, bins, blah = ax.hist(x, bins, density=is_density, histtype='step',
                                    cumulative=True, label=column, color=color, zorder=3)
        ax.legend(loc='right', handles=color_keys)

        ax.set_title(title)
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        fig_name = self.get_output_filename(keyword='figure', extension='png',
                                            file_path='figures/')
        mpl.pyplot.savefig(fig_name, dpi=400)
        self.logger.info('Plot was saved to: {}'.format(fig_name))

    def plot_choropleth(self, aggregate_results, column, title, color_map,
                        shapefile, spatial_index,
                        categories=None):
        """
        Plot a chloropleth of the aggregated results.
        """

        results_with_geometry = self._join_aggregated_data_with_boundaries(aggregated_results=aggregate_results,
                                                                           spatial_index=spatial_index,
                                                                           shapefile=shapefile)
        if column not in results_with_geometry.columns:
            raise UnexpectedPlotColumnException('Did not expect column argument: {}'.format(column))

        mpl.pyplot.close()

        mpl.pyplot.rcParams['axes.facecolor'] = '#cfcfd1'

        results_with_geometry.plot(column=column, cmap=color_map, edgecolor='black', linewidth=0.1)

        # add a scatter plot of the vendors over the chloropleth
        if categories is not None:
            available_colors = ['magenta', 'lime', 'red', 'black', 'orange', 'grey', 'yellow', 'brown', 'teal']
            # if we have too many categories of vendors, limit to using black dots
            if len(categories) > len(available_colors):
                monochrome = True
            else:
                monochrome = False
            color_keys = []
            max_dest_capacity = max(self.dests['capacity'])
            for category in categories:
                if monochrome:
                    color = 'black'
                else:
                    color = available_colors.pop(0)
                    patch = mpatches.Patch(color=color, label=category)
                    color_keys.append(patch)
                dest_subset = self.dests.loc[self.dests['category'] == category]
                mpl.pyplot.scatter(y=dest_subset['lat'], x=dest_subset['lon'], color=color, marker='o',
                                   s=50 * (dest_subset['capacity'] / max_dest_capacity), label=category)
                if not monochrome:
                    mpl.pyplot.legend(loc='best', handles=color_keys)

        mpl.pyplot.title(title)
        fig_name = self.get_output_filename(keyword='figure', extension='png',
                                            file_path='figures/')
        mpl.pyplot.savefig(fig_name, dpi=400)

        self.logger.info('Figure was saved to: {}'.format(fig_name))
        return
