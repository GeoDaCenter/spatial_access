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

from spatial_access.SpatialAccessExceptions import UnrecognizedCategoriesException
from spatial_access.SpatialAccessExceptions import SourceDataNotFoundException
from spatial_access.SpatialAccessExceptions import DestDataNotFoundException
from spatial_access.SpatialAccessExceptions import SourceDataNotParsableException
from spatial_access.SpatialAccessExceptions import DestDataNotParsableException
from spatial_access.SpatialAccessExceptions import PrimaryDataNotFoundException
from spatial_access.SpatialAccessExceptions import SecondaryDataNotFoundException
from spatial_access.SpatialAccessExceptions import ShapefileNotFoundException
from spatial_access.SpatialAccessExceptions import ModelNotAggregatedException
from spatial_access.SpatialAccessExceptions import ModelNotCalculatedException
from spatial_access.SpatialAccessExceptions import ModelNotAggregatableException
from spatial_access.SpatialAccessExceptions import SpatialIndexNotMatchedException
from spatial_access.SpatialAccessExceptions import TooManyCategoriesToPlotException
from spatial_access.SpatialAccessExceptions import UnexpectedPlotColumnException
from spatial_access.SpatialAccessExceptions import AggregateOutputTypeNotExpectedException
from spatial_access.SpatialAccessExceptions import UnexpectedAggregationTypeException


import os.path
import logging


class ModelData:
    """
    Common resources for spatial_access.Models.
    """
    def __init__(self, network_type, sources_filename,
                 destinations_filename,
                 source_column_names=None, dest_column_names=None,
                 walk_speed=None, bike_speed=None, debug=False):
        """
        Args:
            network_type: string, one of {'walk', 'bike', 'drive', 'otp'}.
            sources_filename: string, csv filename.
            destinations_filename: string, csv filename.
            source_column_names: dictionary, map column names to expected values.
            dest_column_names: dictionary, map column names to expected values.
            walk_speed: numeric, override default walking speed (km/hr).
            bike_speed: numeric, override default walking speed (km/hr).
            debug: boolean, enable to see more detailed logging output.
        """
        self.network_type = network_type
        self.transit_matrix = None
        self.dests = None
        self.sources = None
        self.model_results = None
        self.aggregated_results = None
        self.all_categories = {}
        self.focus_categories = {}

        self.walk_speed = walk_speed
        self.bike_speed = bike_speed

        self._aggregation_args = {}
        self._is_source = True
        self._is_aggregatable = True
        self._requires_user_aggregation_type = False
        self._result_column_names = None

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
        self.debug = debug
        self.logger = None
        self.set_logging(debug)

    def write_transit_matrix_to_csv(self, filename=None):
        """
        Args:
            filename: string (or none, in which case a filename will
            be automatically generated).
        Write transit matrix to csv.
        """
        self.transit_matrix.write_csv(filename)

    def write_transit_matrix_to_tmx(self, filename=None):
        """
        Args:
            filename: string (or none, in which case a filename will
            be automatically generated)
        Write transit matrix to tmx.
        """
        self.transit_matrix.write_tmx(filename)

    @staticmethod
    def _get_output_filename(keyword, extension='csv', file_path='data/'):
        """
        Args:
            keyword: string such as "model_results" or "aggregated_results"
                to build the filename.
            extension: file type extension (no ".")
            file_path: subdirectory.
        Returns: string of unused filename.
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

    def get_population(self, source_id):
        """
        Args:
            source_id: string/int
        Returns: the population at a source point.
        """
        return self.sources.loc[source_id, 'population']

    def get_capacity(self, dest_id):
        """
        Args:
            dest_id: string/int
        Returns: the capacity value at a dest point.
        """
        return self.dests.loc[dest_id, 'capacity']

    def get_category(self, dest_id):
        """
        Args:
            dest_id: string/int
        Returns: the category value at a dest point.
        """
        return self.dests.loc[dest_id, 'category']

    def get_all_dest_ids(self):
        """
        Returns: all ids of destination data frame.
        """
        return list(self.dests.index)

    def get_all_source_ids(self):
        """
        Returns: all ids of source data frame.
        """
        return list(self.sources.index)

    def get_ids_for_category(self, category):
        """
        Given category, return an array of all indeces
        which match. If category is all_categories, return all indeces.
        """
        return list(self.dests[self.dests['category'] == category].index)

    def set_logging(self, debug):
        """
        Args:
            debug: set to true for more detailed logging
                output.
        """

        if debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def load_transit_matrix(self, read_from_file=None):
        """
        Load the transit matrix (and sources/dests).
        Args:
            read_from_file: filename of a tmx or csv file to load.
                This allows the user to bypass computing the
                transit matrix from scratch. If read_from_file is
                None, the user will be directed to compute the
                transit matrix from given source/dest data.
        Raises:
            SourceDataNotFoundException: Cannot find source data.
            DestDataNotFoundException: Cannot find dest data.
        """
        if read_from_file:
            self.transit_matrix = TransitMatrix(self.network_type,
                                                read_from_file=read_from_file,
                                                debug=self.debug)
        else:
            self.transit_matrix = TransitMatrix(self.network_type,
                                                primary_input=self.sources_filename,
                                                secondary_input=self.destinations_filename,
                                                primary_hints=self.source_column_names,
                                                secondary_hints=self.dest_column_names,
                                                walk_speed=self.walk_speed,
                                                bike_speed=self.bike_speed,
                                                debug=self.debug)
            try:
                self.transit_matrix.process()
            except PrimaryDataNotFoundException:
                raise SourceDataNotFoundException()
            except SecondaryDataNotFoundException:
                raise DestDataNotFoundException()

            # borrow hints for use in load_sources() and load_dests() if not user supplied
            if self._source_file_hints is None:
                self._source_file_hints = self.transit_matrix.primary_hints
            if self._dest_file_hints is None:
                self._dest_file_hints = self.transit_matrix.secondary_hints

        self.reload_sources()
        self.reload_dests()

    def reload_sources(self, filename=None):
        """
        Load the source points for the model (from csv).
        For each point, the table should contain:
        -unique identifier (integer or string)
        -latitude & longitude
        -population (integer) [only for some models]

        Args:
            filename: string
        Raises:
            SourceDataNotFoundException: Cannot find source
                data.
            SourceDataNotParsableException: Provided source_column_names
                do not correspond to column names.
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
        Load the dest points for the model (from csv).
        For each point, the table should contain:
        -unique identifier (integer or string)
        -latitude & longitude
        -category (string/int) [only for some models]
        -capacity (numeric) [only for some models]

        Args:
            filename: string
        Raises:
            DestDataNotFoundException: Cannot find dest
                data.
            DestDataNotParsableException: Provided dest_column_names
                do not correspond to column names.
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
        self.all_categories = set(self.dests['category'])

    def get_dests_in_range_of_source(self, source_id):
        """
        Args:
            source_id: string/int
        Returns: a list of dest ids in range of the source.
        """
        return self.dests_in_range[source_id]

    def get_sources_in_range_of_dest(self, dest_id):
        """
        Args:
            dest_id: string/int
        Returns: a list of source ids in range of the dest.
        """
        return self.sources_in_range[dest_id]

    def calculate_dests_in_range(self, upper_threshold):
        """
        Args:
            upper_threshold: numeric, upper threshold of what
                points are considered to be in range.
        """
        self.dests_in_range = self.transit_matrix.matrix_interface.get_dests_in_range(upper_threshold)

    def calculate_sources_in_range(self, upper_threshold):
        """
        Args:
            upper_threshold: numeric, upper threshold of what
                points are considered to be in range.
        """
        self.sources_in_range = self.transit_matrix.matrix_interface.get_sources_in_range(upper_threshold)

    def get_values_by_source(self, source_id, sort=False):
        """
        Args:
            source_id: string/int
            sort: boolean, set to true for return value
                to be sorted in nondecreasing order.
        Returns: list of (dest_id, value) pairs, with the option
            to sort in increasing order by value.
        """
        return self.transit_matrix.matrix_interface.get_values_by_source(source_id, sort)

    def get_values_by_dest(self, dest_id, sort=False):
        """
        Args:
            dest_id: string/int
            sort: boolean, set to true for return value
                to be sorted in nondecreasing order.
        Returns: a list of (source_id, value) pairs, with the option
            to sort in increasing order by value.
        """
        return self.transit_matrix.matrix_interface.get_values_by_dest(dest_id, sort)

    def get_population_in_range(self, dest_id):
        """
        Args:
            dest_id: string/int
        Returns: the population within the capacity range for the given
            destination id.
        """
        cumulative_population = 0
        for source_id in self.get_sources_in_range_of_dest(dest_id):
            source_population = self.get_population(source_id)
            if source_population > 0:
                cumulative_population += source_population

        return cumulative_population

    def _map_categories_to_sp_matrix(self):
        """
        Map all categories-> associated dest_ids.
        """
        for dest_id in self.get_all_dest_ids():
            associated_category = self.get_category(dest_id)
            self._add_to_category_map(dest_id, associated_category)

    def _add_to_category_map(self, dest_id, category):
        """
        Args:
            dest_id: string/int
            category: string
        Map the dest_id to the category in the
            transit matrix.
        """
        self.transit_matrix.matrix_interface.add_to_category_map(dest_id, category)

    def time_to_nearest_dest(self, source_id, category):
        """
        Args:
            source_id: string/int
            category: string
        Returns: the time to nearest destination for source_id
            of type category. If category is 'all_categories', return
            the time to nearest destination of any type.
        """
        if category == 'all_categories':
            return self.transit_matrix.matrix_interface.time_to_nearest_dest(source_id, None)
        else:
            return self.transit_matrix.matrix_interface.time_to_nearest_dest(source_id, category)

    def count_dests_in_range_by_categories(self, source_id, category, upper_threshold):
        """
        Args:
            source_id: int/string
            category: string
            upper_threshold: numeric, upper limit of what is
                considered to be 'in range'.
        Returns: the count of destinations in range
            of the source id per category
        """
        if category == 'all_categories':
            return self.transit_matrix.matrix_interface.count_dests_in_range(source_id,
                                                                             upper_threshold,
                                                                             None)
        else:
            return self.transit_matrix.matrix_interface.count_dests_in_range(source_id,
                                                                             upper_threshold,
                                                                             category)

        # TODO: optimize this method
    def count_sum_in_range_by_categories(self, source_id, category):
        """
        Args:
            source_id: int/string
            category: string
        Returns: the count of destinations in range
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
        Don't call this for anything other
        than trivially small matrices.
        """
        self.transit_matrix.matrix_interface.print_data_frame()

    def _spatial_join_community_index(self, dataframe, shapefile='data/chicago_boundaries/chicago_boundaries.shp',
                                      spatial_index='community',  projection='epsg:4326'):
        """
        Join the dataframe with location data from shapefile.
        Args:
            dataframe: pandas dataframe with unique id.
            shapefile: shapefile containing geometry.
            spatial_index: column names of aggregation area in shapefile.
            projection: defaults to 'epsg:4326'
        Returns: dataframe.
        Raises:
            ShapefileNotFoundException: Shapefile not found.
            SpatialIndexNotMatchedException: spatial_index not found in shapefile.
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

    def _rejoin_results_with_coordinates(self, model_results, is_source):
        """
        Args:
            model_results: dataframe
            is_source: boolean (tells where to draw lat/long data from)
        Returns: deep copty of dataframe with lat/long data.
        """
        model_results = model_results.copy(deep=True)
        if is_source:
            model_results['lat'] = self.sources['lat']
            model_results['lon'] = self.sources['lon']
        else:
            model_results['lat'] = self.dests['lat']
            model_results['lon'] = self.dests['lon']
        return model_results

    def _build_aggregate(self, data_frame, aggregation_args, shapefile, spatial_index, projection):
        """
        Private method invoked to aggregate dataframe on spatial area.
        Args:
            data_frame: dataframe
            aggregation_args: dictionary mapping each column name to the method by which that
                column should be aggregated, e.g. mean, sum, etc...
            shapefile: filename of shapefile
            spatial_index: index of geospatial area in shapefile
            projection: defaults to 'epsg:4326'

        Returns: aggregated data frame.

        """
        if 'lat' not in data_frame.columns or 'lon' not in data_frame.columns or 'spatial_index' not in data_frame.columns:
            data_frame = self._spatial_join_community_index(dataframe=data_frame,
                                                                    shapefile=shapefile,
                                                                    spatial_index=spatial_index,
                                                                    projection=projection)
        aggregated_data_frame = data_frame.groupby('spatial_index').agg(aggregation_args)
        return aggregated_data_frame

    def set_focus_categories(self, categories):
        """
        Set the categories that the model should perform computations for.
        Args:
            categories: list of categories.
        Raises:
            UnrecognizedCategoriesException: User passes categories not
                found in the dest data.
        """
        if categories is None:
            self.focus_categories = self.all_categories
        else:
            self.focus_categories = categories
            unrecognized_categories = set(categories) - self.all_categories
            if len(unrecognized_categories) > 0:
                raise UnrecognizedCategoriesException(','.join([category for category in unrecognized_categories]))


    def aggregate(self, aggregation_type=None, shapefile='data/chicago_boundaries/chicago_boundaries.shp',
                        spatial_index='community',  projection='epsg:4326'):
        """

        Args:
            aggregation_type: string, required for models with multiple possiblities
                for aggregating.
            shapefile: filename of shapefile
            spatial_index: index of geospatial area in shapefile
            projection: defaults to 'epsg:4326'

        Returns: aggregated data frame.

        Raises:
            ModelNotCalculatedException: If the model has not yet been
                calculated.
            UnexpectedAggregationTypeException: If the user passes an
                unexpected aggregation type, or no aggregation type
                when one is expected, or an aggregation type when none
                is expected.
        """
        if self.model_results is None:
            raise ModelNotCalculatedException()
        if not self._is_aggregatable:
            raise ModelNotAggregatableException()
        if self._requires_user_aggregation_type:
            if aggregation_type is None:
                raise UnexpectedAggregationTypeException(aggregation_type)
            else:
                if aggregation_type not in {'min', 'max', 'mean'}:
                    raise UnexpectedAggregationTypeException(aggregation_type)
                else:
                    self._aggregation_args = {}
                    for column in self.model_results.columns:
                        self._aggregation_args[column] = aggregation_type

        else:
            if aggregation_type is not None:
                raise UnexpectedAggregationTypeException(aggregation_type)

        results_with_coordinates = self._rejoin_results_with_coordinates(self.model_results, self._is_source)

        self.aggregated_results = self._build_aggregate(data_frame=results_with_coordinates,
                                                        aggregation_args=self._aggregation_args,
                                                        shapefile=shapefile,
                                                        spatial_index=spatial_index,
                                                        projection=projection)
        return self.aggregated_results

    def write_aggregated_results(self, filename=None, output_type='csv'):
        """
        Args:
            filename: file to write results. If none is given, a valid
                filename will be automatically generated.
            output_type: 'csv' or 'json'.

        Raises:
            AggregateOutputTypeNotExpectedException:

        """
        if filename is not None:
            output_type = filename.split('.')[1]
        else:
            filename = self._get_output_filename(keyword='aggregate',
                                                       extension=output_type,
                                                       file_path='data/')

        if self.aggregated_results is None:
            raise ModelNotAggregatedException()

        if output_type == 'csv':
            self.aggregated_results.to_csv(filename)
        elif output_type == 'json':
            output = {}
            for row in self.aggregated_results.itertuples():
                output[row[0]] = {}
                for i, column in enumerate(self.aggregated_results.columns):
                    output[row[0]][column] = row[i + 1]
            with open(filename, 'w') as file:
                json.dump(output, file)
        else:
            raise AggregateOutputTypeNotExpectedException(output_type)

    def write_results(self, filename=None):
        """
        Write results to csv.
        Args:
            filename: file to write results. If none is given, a valid
            filename will be automatically generated.
        Raises:
            ModelNotCalculatedException: if model has not been calculated.
        """ 
        if self.model_results is None:
            raise ModelNotCalculatedException()
        if filename is None:
            filename = self._get_output_filename(keyword='model',
                                                extension='csv',
                                                file_path='data/')
        self.model_results.to_csv(filename)


    @staticmethod
    def _join_aggregated_data_with_boundaries(aggregated_results, spatial_index,
                                              shapefile='data/chicago_boundaries/chicago_boundaries.shp'):
        """
        Args:
            aggregated_results: dataframe
            shapefile: filename of shapefile
            spatial_index: index of geospatial area in shapefile

        Returns: dataframe.

        Raises:
            ShapefileNotFoundException: shapefile not found.
        """
        try:
            boundaries_gdf = gpd.read_file(shapefile)
        except FileNotFoundError:
            raise ShapefileNotFoundException('shapefile not found: {}'.format(shapefile))
        columns_to_keep = list(aggregated_results.columns)
        columns_to_keep.append('geometry')
        columns_to_keep.append(spatial_index)

        results = boundaries_gdf.merge(aggregated_results, left_on=spatial_index,
                                       right_index=True, how='outer')
        results.fillna(value=0, inplace=True)
        return results[columns_to_keep]

    def plot_cdf(self, plot_type=None, xlabel="xlabel", ylabel="ylabel", title="title",
                 bins=100, is_density=False, filename=None):
        """
        Args:
            plot_type: If the model has multiple possibilities to plot, specify which
                one.
            xlabel: xlabel for figure.
            ylabel: ylabel for figure.
            title: title for figure.
            bins: integer, number of bins.
            is_density: boolean, true for density plot.
            filename: filename to write to.

        Raises:
            ModelNotAggregatedException: Model is not aggregated.
            UnexpectedPlotColumnException: User passes unexpected plot type.
            TooManyCategoriesToPlotException: Too many categories to plot.
        """
        if self.aggregated_results is None:
            raise ModelNotAggregatedException()

        if self._is_source:
            cdf_eligible = self.model_results[self.sources['population'] > 0]
        else:
            cdf_eligible = self.model_results

        if isinstance(self._result_column_names, str):
            if plot_type is not None:
                raise UnexpectedPlotColumnException(plot_type)
            plot_type = self._result_column_names
        else:
            if plot_type is None:
                raise UnexpectedPlotColumnException(plot_type)

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
        if filename is None:
            filename = self._get_output_filename(keyword='figure', extension='png',
                                                file_path='figures/')
        mpl.pyplot.savefig(filename, dpi=400)
        self.logger.info('Plot was saved to: {}'.format(filename))

    def plot_choropleth(self, column, include_destinations=True, title='Title', color_map='Greens',
                        shapefile='data/chicago_boundaries/chicago_boundaries.shp', spatial_index='community',
                        filename=None):
        """
        Args:
            column: Which column to plot.
            include_destinations: boolean, will plot circles for destinations if true.
            title: Figure title.
            color_map: See https://matplotlib.org/tutorials/colors/colormaps.html
            shapefile: filename of shapefile
            spatial_index: index of geospatial area in shapefile
            filename: file to write figure to.

        Raises:
            ModelNotAggregatedException: Model is not aggregated.
            UnexpectedPlotColumnException: User passes unexpected column.
        """
        if self.aggregated_results is None:
            raise ModelNotAggregatedException()
        if include_destinations:
            categories = self.focus_categories
        else:
            categories = None
        results_with_geometry = self._join_aggregated_data_with_boundaries(aggregated_results=self.aggregated_results,
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
        if filename is None:
            filename = self._get_output_filename(keyword='figure', extension='png',
                                            file_path='figures/')
        mpl.pyplot.savefig(filename, dpi=400)

        self.logger.info('Figure was saved to: {}'.format(filename))

