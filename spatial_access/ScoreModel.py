import pandas as pd
from spatial_access.p2p import TransitMatrix
import os.path
import logging
import time


class ModelData(object):
    '''
    A parent class to hold/process data for more advanced geospatial
    models like HSSAModel and PCSpendModel. The 'upper' argument in
    the __init__ is the time (in seconds), above which a source and dest
    are considered to be out of range of each other.
    '''

    def __init__(self, network_type, sources_filename, 
                 destinations_filename, upper_threshold,
                 source_file_hints=None, dest_file_hints=None,
                 debug=False):
        self.network_type = network_type
        self.sp_matrix = None
        self.dests = None
        self.sources = None

        self.sources_filename = sources_filename
        self.destinations_filename = destinations_filename

        self.source_file_hints = None
        self.dest_file_hints = None
        
        self.upper_threshold = upper_threshold 
        self.valid_population = True
        self.valid_target = True
        self.valid_category = True

        self.desinations_to_category = {}
        
        if debug:
            self.set_logging('info')
        else:
            self.set_logging('debug')

    @staticmethod
    def get_output_filename(keyword, extension='csv', file_path='data/'):
        '''
        Given a keyword, find an unused filename.
        '''
        if file_path is None:
            file_path = "data/"
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        filename = os.path.join(file_path, '{}_0.{}'.format(keyword, extension))
        counter = 1
        while os.path.isfile(filename):
            filename = os.path.join(file_path, '{}_{}.{}'.format(keyword, counter, extension))
            counter += 1
        self.output_filename = filename

        return filename
    
    def get_time(self, source, dest):
        '''
        Return the time, in seconds, from source to dest.
        '''
        assert self.sp_matrix is not None, 'load shortest path matrix before this step'

        time = self.sp_matrix.get(source, dest)

        return time


    def get_population(self, source_id):
        '''
        Return the population at a source point.
        '''
        assert self.sources is not None, 'load sources before this step'

        return self.sources.loc[source_id, 'population']


    def get_target(self, dest_id):
        '''
        Return the target value at a dest point.
        '''
        assert self.dests is not None, 'load dests before this step'

        return self.dests.loc[dest_id, 'target']


    def get_category(self, dest_id):
        '''
        Return the category of a dest point.
        '''
        assert self.dests is not None, 'load dests before this step'

        return str(self.dest2cats[int(dest_id)])


    def process(self):
        '''
        Generate mappings for the model to use.
        '''

        #need to make sure we've loaded these data first
        assert self.sp_matrix is not None, 'load shortest path matrix before this step'
        assert self.sources is not None, 'load sources before this step'
        assert self.dests is not None, 'load destinations before this step'        
        start_time = time.time()

        self.sp_matrix._matrix_interface_get_sources_in_range(self.upper)
        self.sp_matrix._matrix_interface_get_dests_in_range(self.upper)

        self.logger.info('Finished processing ModelData in {:,.2f} seconds'.format(time.time() - start_time))
    
    
    def set_logging(self, level=None):
        '''
        Set the logging level to debug or info
        '''
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
        '''
        Load the shortest path matrix; if a filename is supplied,
        ModelData will attempt to load from file.
        If filename is not supplied, ModelData will generate
        a shortest path matrix using p2p (must be installed).
        '''
        if filename:
            try:
                self.sp_matrix = TransitMatrix(self.network_type,
                                               read_from_file=filename)
            except:
                if self.logger:
                    self.logger.error('Unable to load sp_matrix from file')
                    return
        
        else:
            self.sp_matrix = TransitMatrix(self.network_type,
                                       primary_input=self.sources_filename,
                                       secondary_input=self.destinations_filename,
                                       primary_hints=self.source_file_hints,
                                       secondary_hints=self.dest_file_hints)
            self.sp_matrix.process()
            
            #borrow hints for use in load_sources() and load_dests()
            self.source_file_hints = self.sp_matrix.primary_hints
            self.dest_file_hints = self.sp_matrix.secondary_hints
        
        self.reload_sources()
        self.reload_dests()


    def reload_sources(self, filename=None):
        '''
        Load the source points for the model (from csv).
        For each point, the table should contain:
            -unique identifier (integer or string)
            -population (integer)
        The field_mapping argument will be present if code is being called by the web app.
        Otherwise the field_mapping default value of None will be passed in, and command
        line prompts for user input will be executed.
        '''
        
        if filename:
            self.sources_filename = filename

        try:
            self.sources = pd.read_csv(self.sources_filename)
        except:
            self.logger.error('Unable to load sources file: {}'.format(self.sources_filename))
            return
        
        #extract the column names from the table
        population = ''
        idx = ''
        lat = ''
        lon = ''

        if self.source_file_hints is not None:
            try:
                idx = self.source_file_hints['idx']
                population = self.source_file_hints['population']
                lat = self.source_file_hints['lat']
                lon = self.source_file_hints['lon']

                self.sources.set_index(idx, inplace=True)
                self.sources.rename(columns=rename_cols,inplace=True)
            except:
                self.logger.error('Unable to use source_file_hints to read sources')
                #set sources to none and return right away so the
                #user knows there is a problem
                self.sources = None
                return
        else:
            
            #extract the column names from the table
            source_data_columns = self.sources.columns.values
            print('The variables in your data set are:')
            for var in source_data_columns:
                print('> ',var)
            while idx not in source_data_columns:
                idx = input('Enter the unique index variable: ')
            print('If you have no population variable, write "skip" (no quotations)')
            while population not in source_data_columns and population != 'skip':
                population = input('Enter the population variable: ')
            while lat not in source_data_columns:
                lat = input('Enter the latitude variable: ')
            while lon not in source_data_columns:
                lon = input('Enter the longitude variable: ')

        #insert filler values for the population column if 
        #user does not want to include it. need it for coverage
        if population == 'skip':
            self.sources['population'] = 1
            self.valid_population = False

        #store the col names for later use
        self.source_file_hints = {'xcol':lat, 'ycol':lon,'idx':idx, 
                                  'population':population}

        #rename columns, clean the data frame
        if population == 'skip':
            rename_cols = {lat:'lat', lon:'lon'}
        else:
            rename_cols = {population:'population', lat:'lat', lon:'lon'}
        self.sources.set_index(idx, inplace=True)
        self.sources.rename(columns=rename_cols,inplace=True)

        #drop unused columns
        columns_to_keep = [value for value in rename_cols.values()]
        self.sources = self.source[[columns_to_keep]]


    def reload_dests(self, filename=None):
        '''
        Load the destination points for the model (from csv).
        For each point, the table should contain:
            -unique identifier (integer or string)
            -target value (integer or float)
            -category (string)
        The field_mapping argument will be present if code is being called by the web app.
        Otherwise the field_mapping default value of None will be passed in, and command
        line prompts for user input will be executed.
        '''

        if filename:
            self.destinations_filename = filename

        try:
            self.dests = pd.read_csv(self.destinations_filename)
        except:
            self.logger.error('Unable to load dests file: {}'.format(self.destinations_filename))
            return
        
        #extract the column names from the table
        category = ''
        target = ''
        idx = ''
        lat = ''
        lon = ''

        if self.dest_file_hints is not None:
            try:
                idx = self.dest_file_hints['idx']
                category = self.dest_file_hints['category']
                target = self.dest_file_hints['target']
                lat = self.dest_file_hints['lat']
                lon = self.dest_file_hints['lon']

                self.dests.set_index(idx, inplace=True)
                self.dests.rename(columns=rename_cols,inplace=True)
            except:
                self.logger.error('Unable to use dest_file_hints to read dests')
                #set dests to none and return right away so the
                #user knows there is a problem
                self.dests = None
                return
        else:
            
            #extract the column names from the table
            dest_data_columns = self.dests.columns.values
            print('The variables in your data set are:')
            for var in dest_data_columns:
                print('> ',var)
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

        #insert filler values for the target column if 
        #user does not want to include it.
        if target == 'skip':
            self.dests['target'] = 1
            self.valid_target = False

        #insert filler values for the category column if 
        #user does not want to include it.
        if category == 'skip':
            self.dests['category'] = 1
            self.valid_category = False

        #store the col names for later use
        self.dest_file_hints = {'xcol':lat, 'ycol':lon,'idx':idx,
                                'category':category, 'target':target}

        #rename columns, clean the data frame
        
        rename_cols = {lat:'lat', lon:'lon'}
        if target != 'skip':
            rename_cols[target] = 'target'
        if category != 'skip':
            rename_cols[category] = 'category'
        
        self.dests.set_index(idx, inplace=True)
        self.dests.rename(columns=rename_cols,inplace=True)

        #drop unused columns
        columns_to_keep = [value for value in rename_cols.values()]
        self.dests = self.dests[[columns_to_keep]]