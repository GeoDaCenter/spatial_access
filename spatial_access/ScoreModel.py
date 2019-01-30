import pandas as pd
from spatial_access.p2p import TransitMatrix

from spatial_access.SpatialAccessExceptions import SourceDataNotFoundException
from spatial_access.SpatialAccessExceptions import DestDataNotFoundException
from spatial_access.SpatialAccessExceptions import SourceDataNotParsableException
from spatial_access.SpatialAccessExceptions import DestDataNotParsableException
from spatial_access.SpatialAccessExceptions import PrimaryDataNotFoundException
from spatial_access.SpatialAccessExceptions import SecondaryDataNotFoundException

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

        # column_names and file_hints are similar, both map indended_name->actual_data_name
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

    def get_target(self, dest_id):
        """
        Return the target value at a dest point.
        """
        return self.dests.loc[dest_id, 'target']

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
                                            read_from_file=filename)

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
        except:
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
        except:
            raise SourceDataNotParsableException()

        # drop unused columns
        columns_to_keep = list(rename_cols.values())
        self.sources = self.sources[columns_to_keep]

        # remap to numeric id if original data used string ids
        remapped_ids = self.get_remapped_source_ids()
        if isinstance(remapped_ids, dict):
            self.sources.index = self.sources.index.map(remapped_ids)

    def reload_dests(self, filename=None):
        """
        Load the destination points for the model (from csv).
        For each point, the table should contain:
            -unique identifier (integer or string)
            -target value (integer or float)
            -category (string)
        The field_mapping argument will be present if code is being called by the web app.
        Otherwise the field_mapping default value of None will be passed in, and command
        line prompts for user input will be executed.
        """

        if filename:
            self.destinations_filename = filename

        try:
            self.dests = pd.read_csv(self.destinations_filename)
        except:
            raise DestDataNotFoundException()

        if self.dest_column_names is None:
            # extract the column names from the table
            category = ''
            target = ''
            idx = ''
            lat = ''
            lon = ''

            if self._dest_file_hints is not None:
                if 'idx' in self._dest_file_hints:
                    idx = self._dest_file_hints['idx']
                if 'category' in self._dest_file_hints:
                    category = self._dest_file_hints['category']
                if 'target' in self._dest_file_hints:
                    target = self._dest_file_hints['target']
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
            print('If you have no target variable, write "skip" (no quotations)')
            while target not in dest_data_columns and target != 'skip':
                target = input('Enter the target variable: ')
            print('If you have no category variable, write "skip" (no quotations)')
            while category not in dest_data_columns and category != 'skip':
                category = input('Enter the category variable: ')
            while lat not in dest_data_columns:
                lat = input('Enter the latitude variable: ')
            while lon not in dest_data_columns:
                lon = input('Enter the longitude variable: ')
            self.dest_column_names = {'lat': lat, 'lon': lon, 'idx': idx,
                                      'category': category, 'target': target}

        try:
            # insert filler values for the target column if
            # user does not want to include it.
            if self.dest_column_names['target'] == 'skip':
                self.dests['target'] = 1

            # insert filler values for the category column if
            # user does not want to include it.
            if self.dest_column_names['category'] == 'skip':
                self.dests['category'] = 1

            # rename columns, clean the data frame
            rename_cols = {self.dest_column_names['lat']: 'lat', self.dest_column_names['lon']: 'lon'}
            if self.dest_column_names['target'] != 'skip':
                rename_cols[self.dest_column_names['target']] = 'target'
            if self.dest_column_names['category'] != 'skip':
                rename_cols[self.dest_column_names['category']] = 'category'

            self.dests.set_index(self.dest_column_names['idx'], inplace=True)
            self.dests.rename(columns=rename_cols, inplace=True)

        except:
            raise DestDataNotParsableException()

        # drop unused columns
        columns_to_keep = list(rename_cols.values())
        self.dests = self.dests[columns_to_keep]

        # remap to numeric id if original data used string ids
        remapped_ids = self.get_remapped_dest_ids()
        if isinstance(remapped_ids, dict):
            self.dests.index = self.dests.index.map(remapped_ids)

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
        self.dests_in_range =  self._sp_matrix.matrix_interface.get_dests_in_range(upper_threshold)

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

    def get_population_in_range(self, dest_id, upper_threshold):
        """
         Return the population within the target range for the given
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

    def count_dests_in_range_by_categories(self, source_id, upper_threshold, category):
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

    def _print_data_frame(self):
        """
        Print the transit matrix.
        """
        self._sp_matrix.matrix_interface.print_data_frame()

    def get_remapped_source_ids(self):
        """
        Return a dictionary of the mapping from
        new (integer) source ids to original (string) source ids.
        """
        return self._sp_matrix.matrix_interface.get_source_id_remap()

    def get_remapped_dest_ids(self):
        """
        Return a dictionary of the mapping from
        new (integer) dest ids to original (string) dest ids.
        """
        return self._sp_matrix.matrix_interface.get_dest_id_remap()

    # TODO
    def build_aggregate(self, model_results, aggregation_type):
        """
        Aggregate model results.
        """
        pass

    # TODO
    def plot_cdf(self, model_results):
        """
        Plot a cdf of the model results
        """
        pass

    # TODO
    def write_results(self, model_results):
        """
        Write results to csv
        """
        pass

    # TODO
    def write_aggregated_results(self, model_results):
        """
        Write aggregated results to csv
        """
        pass