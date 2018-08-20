import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import matplotlib.patches as mpatches
from matplotlib import mlab
import matplotlib as mpl
from p2p import TransitMatrix
import os.path, csv, math, sys, logging, json, time
import copy
from operator import itemgetter
import timeit

class ModelData(object):
    '''
    A parent class to hold/process data for more advanced geospatial
    models like HSSAModel and PCSpendModel. The 'upper' argument in
    the __init__ is the time (in minutes), above which a source and dest
    are considered to be out of range of each other.
    '''

    def __init__(self, network_type, upper):
        self.network_type = network_type
        self.sp_matrix = None
        self.dests = None
        self.sources = None
        self.category_set = None
        self.source2dest = {}
        self.dest2source = {}
        self.dest2cats = {}
        self.cat2dests = {}
        self.near_nbr = {}
        self.n_dests_in_range = {}
        self.time = {}
        self.time_val2 = {}
        self.use_n_nearest = 10

        self.sources_nn = {}
        self.idx_2_col = {}

        self.source_id_list = []
        self.dest_id_list = []

        self.sp_matrix_good = False
        self.dests_good = False
        self.sources_good = False
        self.processed_good = False

        self.primary_hints = None
        self.secondary_hints = None

        assert network_type in ['drive', 'walk', 'bike'], 'gave invalid mode of transit. Must be one of: drive, walk, bike'
        self.upper = upper * 60 #convert minutes from input to seconds

        self.set_logging('info')


        self.valid_population = True
        self.valid_target = True
        self.valid_category = True
        self.valid_lower_areal_unit = True


    def get_time(self, source, dest):
        '''
        Return the time, in seconds, from source to dest.
        '''
        assert self.sp_matrix_good, 'load shortest path matrix before this step'

        timee = self.sp_matrix.get(source, dest)

        return timee


    def get_population(self, source_id):
        '''
        Return the population at a source point.
        '''
        assert self.sources_good, 'load sources before this step'

        return self.sources.loc[source_id, 'population']

    def get_target(self, dest_id):
        '''
        Return the target value at a dest point.
        '''
        assert self.dests_good, 'load dests before this step'

        return self.dests.loc[dest_id, 'target']


    def get_category(self, dest_id):
        '''
        Return the category of a dest point.
        '''
        assert self.dests_good, 'load dests before this step'

        return str(self.dest2cats[int(dest_id)])


    def figure_name(self):
        '''
        Return a unique figure name.
        '''
        i = 0
        if not os.path.exists("data/figures/"):
            os.makedirs("data/figures/")
        fig_name = 'data/figures/fig_0.png'
        while (os.path.isfile(fig_name)):
            i += 1
            fig_name = 'data/figures/fig_{}.png'.format(i)

        return fig_name



    def process(self):
        '''
        Generate mappings for the model to use.
        '''

        #need to make sure we've loaded these data first
        assert self.sp_matrix_good, 'load shortest path matrix before this step'
        assert self.sources_good, 'load sources before this step'
        assert self.dests_good, 'load destinations before this step'
        self.logger.info('Processing... This could take a while')
        

        #Calculate time to nearest neighbor (near_nbr) and number of destinations within buffer (n_dests_in_range) metrics.
        #pre map dest->category
        
        start_time = time.time()

        
        CAT = self.dests.columns.get_loc('category') + 1
        ID = 0
        rv = {}
        included_cats = set()
        nearest_cat_template = {}
        n_dests_in_range_template = {}
        for data in self.dests.itertuples():
            self.dest2cats[data[ID]] = str(data[CAT])
            if str(data[CAT]) in included_cats:
                self.cat2dests[data[CAT]].append(data[ID])
            else:
                self.cat2dests[str(data[CAT])] = [data[ID]]
                included_cats.add(data[CAT])
                nearest_cat_template[data[CAT]] = None
                n_dests_in_range_template[data[CAT]] = 0

              
        #creating source to dest dictionary for times within self.upper using sorting and binary search
        self.source2dest = {}
        self.neg_val = {}
        self.no_dest_in_range = {} #stores no of destinations within self.upper
        for source in self.source_2:
            pairs = [(k,v) for k,v in self.dicto[source].items()]
            pairs.sort(key=itemgetter(1))
            lo, hi = 0, len(pairs) - 1
            while lo <= hi:
                mid =  (lo + hi) / 2
                mid = int(mid)
                if pairs[mid][1] <= self.upper:
                    lo = mid + 1
                elif pairs[mid][1] > self.upper:
                    hi = mid - 1
            key = lo
            lo, hi = 0, len(pairs) - 1
            while lo <= hi:
                mid =  (lo + hi) / 2
                mid = int(mid)
                if pairs[mid][1] <= -1:
                    lo = mid + 1
                elif pairs[mid][1] > -1:
                    hi = mid - 1
            key_min = lo


            self.dicto[source] = pairs

            dummy =[]
            #key_min is the position of the first index which is non-negative.
            if key_min>0:
                dummy = pairs[0:key_min]

            #Checking if every destination has negatives. Only then, will we designate NAs for the sources.
            #neg val dictionary contains all sources that should be NAs.
            if len(dummy) == len(pairs):
                self.neg_val[int(float(source))] = pairs[0:key_min]

            self.source2dest[int(float(source))] = pairs[key_min:key]


            self.no_dest_in_range[int(float(source))] = len(self.source2dest[int(float(source))])

        #creating the same dictionary with destination as keys
        self.dest2source = {}
        for i in self.dest_2:
            if(i!=''):
                self.dest2source[int(float(i))] = []
        for key,value in self.source2dest.items():
            for dest,timee in value:
                self.dest2source[int(float(dest))].append((key,timee))

    
        self.processed_good = True
        self.logger.info('Finished processing ModelData in {:,.2f} seconds'.format(time.time() - start_time))

    def get_output_filename (self, keyword, extension='csv', file_path='data/'):
        '''
        Given a keyword, find an unused filename.
        '''
        
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        filename = file_path + '{}_0.{}'.format(keyword, extension)
        counter = 1
        while os.path.isfile(filename):
            filename = file_path + '{}_{}.{}'.format(keyword, counter, extension)
            counter += 1

        return filename
    
    def get_output_filename_access (self, keyword, extension='csv', file_path='data/access_metrics/'):
        '''
        Given a keyword, find an unused filename.
        '''
        
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        filename = file_path + '{}_0.{}'.format(keyword, extension)
        counter = 1
        while os.path.isfile(filename):
            filename = file_path + '{}_{}.{}'.format(keyword, counter, extension)
            counter += 1

        return filename
    
    def get_output_filename_cov (self, keyword, extension='csv', file_path='data/coverage_metrics/'):
        '''
        Given a keyword, find an unused filename.
        '''
        
        if not os.path.exists(file_path):
            os.makedirs(file_path)
        filename = file_path + '{}_0.{}'.format(keyword, extension)
        counter = 1
        while os.path.isfile(filename):
            filename = file_path + '{}_{}.{}'.format(keyword, counter, extension)
            counter += 1

        return filename
    
    
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

        #try to load from file if given
        if filename:
            start_time=time.time()
            self.dicto = {}  #Dictionary storing matrix travel times from each source to each dest
            
            
            self.source_2 = [] #source id list
            
            
            with open(filename, 'r') as File:
                reader = csv.reader(File)
                self.dest_2 = next(reader)
                #convert csv into our useful matrix dictionary
                for row in reader:
                    self.dicto[row[0]] = {}
                    self.source_2.append(row[0])
                    self.no_dest = len(row)
                    for i in range(1, len(row)):
                        self.dicto[row[0]][int(float(self.dest_2[i]))] = int(float(row[i]))     
            end_time=time.time()

            self.logger.info('Loaded sp matrix from file: {}'.format(filename))
            self.logger.info('Finished loading sp_matrix in {:,.2f} seconds'.format(end_time - start_time))
        else:
            assert self.sources_good, 'load sources before this step'
            assert self.dests_good, 'load destinations before this step'
            
            self.sp_matrix = TransitMatrix(network_type=self.network_type,
                primary_input=self.source_filename,
                secondary_input=self.dest_filename,
                write_to_file=True, load_to_mem=True, 
                primary_hints=self.primary_hints, 
                secondary_hints=self.secondary_hints)

            sl_file = None

            #need to load up speed limit table
            if self.network_type == 'drive':
                sl_file = 'BAH'
                while not os.path.isfile(sl_file):
                    sl_file = input('Please enter the filename of the speed limit table: ')
            self.sp_matrix.process(speed_limit_filename=sl_file)

            self.logger.info('Generated sp matrix to file: {}'.format(self.sp_matrix.output_filename))

        self.sp_matrix_good = True


    def load_sources_nn(self, use_n_nearest=10 ,filename='data/sources_nn_0.json'):
        '''
        This method will probably be deleted
        '''
    
        start = time.time()
        self.use_n_nearest = use_n_nearest
        if filename:
            self.sources_nn = json.load(open(filename))
            self.logger.info('loaded source nn data from file')
        else:
            assert self.sources_good, 'Load sources first'
            output_filename = self.get_output_filename('sources_nn', 'json')
            if self.network_type == 'drive':
                sl_file = 'BAH'
                while not os.path.isfile(sl_file):
                    sl_file = input('Please enter the filename of the speed limit table: ')
            else:
                sl_file = None

            tm = TransitMatrix(network_type=self.network_type, 
                primary_input=self.source_filename, 
                secondary_input=self.source_filename, output_type='json', 
                n_best_matches=use_n_nearest, epsilon=0.05)
            tm.process(speed_limit_filename=sl_file, output_filename=output_filename)

            self.sources_nn = json.load(open(output_filename))
            self.logger.info('Generated source relational data to file {}'.format(output_filename))


    def load_sources(self, filename=None, 
                     shapefile='resources/chi_comm_boundaries', field_mapping=None):
        '''
        Load the source points for the model (from csv).
        For each point, the table should contain:
            -unique identifier (integer or string)
            -population (integer)
        The field_mapping argument will be present if code is being called by the web app.
        Otherwise the field_mapping default value of None will be passed in, and command
        line prompts for user input will be executed.
        '''
        #try to load the source table
        try:
            self.sources = pd.read_csv(filename)
        except:
            self.logger.error('Unable to load sources file: {}'.format(filename))
            sys.exit(0)
        
        #extract the column names from the table
        population = 'skip'
        lower_areal_unit = 'skip'
        idx = 'ID'
        lat = 'lat'
        lon = 'lon'

        '''
        #if the command line is being used to call the code...
        if field_mapping is None:
            
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
            print('If you have no lower areal unit variable, write "skip" (no quotations)')
            while lower_areal_unit not in source_data_columns and lower_areal_unit != 'skip':
                lower_areal_unit = input('Enter the lower areal unit variable: ')
            while lat not in source_data_columns:
                lat = input('Enter the latitude variable: ')
            while lon not in source_data_columns:
                lon = input('Enter the longitude variable: ')

            #insert filler values for the lower_areal_unit column if 
            #user lower_areal_unit not want to include it in GUI
            if lower_areal_unit == 'skip':
                self.sources['lower_areal_unit'] = 1
                self.valid_lower_areal_unit = False

        '''

            
        
        #otherwise, if the web app is being used to call the code...
        else:

            idx = field_mapping['idx']
            population = field_mapping['population']
            lower_areal_unit = 'skip'
            lat = field_mapping['lat']
            lon = field_mapping['lon']

        #insert filler values for the population column if 
        #user does not want to include it. need it for coverage
        if population == 'skip':
            self.sources['population'] = 1
            self.valid_population = False

        #store the col names for later use
        self.primary_hints = {'xcol':lat, 'ycol':lon,'idx':idx}

        #rename columns, clean the data frame
        if population == 'skip':
            rename_cols = {lat:'lat', lon:'lon'}
        else:
            rename_cols = {population:'population', lat:'lat', lon:'lon', lower_areal_unit:'lower_areal_unit'}
  
        self.sources = pd.read_csv(filename)
        self.sources.set_index(idx, inplace=True)
        self.sources.rename(columns=rename_cols,inplace=True)
        self.sources = self.sources.reindex(columns=['lat','lon','population', 'lower_areal_unit'])

        #Disregard shapefile input to avoid spatial joins and potential calculation errors.
        #join source table with shapefile
        #copy = self.sources.copy(deep=True)
        #geometry = [Point(xy) for xy in zip(copy['lon'], copy['lat'])]
        #crs = {'init':'epsg:4326'}
        #copy = self.sources.copy(deep=True)
        #geo_sources = gpd.GeoDataFrame(copy, crs=crs, geometry=geometry)
        #boundaries_gdf = gpd.read_file(shapefile)
        #geo_sources = gpd.sjoin(boundaries_gdf, geo_sources, how='inner', 
        #                            op='intersects')
        #geo_sources.set_index('index_right', inplace=True)
        #self.sources = geo_sources[['community','population','lat','lon','geometry']]
        
        self.source_id_list = self.sources.index
        self.sources_good = True
        self.source_filename = filename


    def load_dests(self, filename=None, 
        shapefile='resources/chi_comm_boundaries', subset=None, field_mapping=None):
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

        #try to load dest file
        try:
            self.dests = pd.read_csv(filename)
        except:
            self.logger.error('Unable to load dest file: {}'.format(filename))
            sys.exit(0)

        #extract column names
        category = 'cat'
        target = 'skip'
        lower_areal_unit = 'skip'
        idx = 'ID'
        lat = 'lat'
        lon = 'lon'
        '''

        #if the command line is being used to call the code...
        if field_mapping is None:
            
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
            print('If you have no lower areal unit variable, write "skip" (no quotations)')
            while lower_areal_unit not in dest_data_columns and lower_areal_unit != 'skip':
                lower_areal_unit = input('Enter the lower areal unit variable: ')
            print('If you have no category variable, write "skip" (no quotations)')
            while category not in dest_data_columns and category != 'skip':
                category = input('Enter the category variable: ')
            while lat not in dest_data_columns:
                lat = input('Enter the latitude variable: ')
            while lon not in dest_data_columns:
                lon = input('Enter the longitude variable: ')

        

            if target == 'skip':
                target_name = 'target'
            else:
                target_name = target
        '''

        
        #otherwise, if the web app is being used to call the code...
        else:

            idx = field_mapping['idx']
            target = field_mapping['target']
            target_name = target
            category = field_mapping['category']
            lower_areal_unit = 'skip'
            lat = field_mapping['lat']
            lon = field_mapping['lon']


        #store the col names for later use
        self.secondary_hints = {'xcol':lat, 'ycol':lon,'idx':idx}

        if category == 'skip':
            category_name = 'category'
        else:
            category_name = category

        if lower_areal_unit == 'skip':
            lower_areal_unit_name = 'lower_areal_unit'
        else:
            lower_areal_unit_name = lower_areal_unit

        self.dests = self.dests.reindex(columns=[idx, target_name, category_name, lat, lon, lower_areal_unit])
        #clean the table

        rename_cols = {target:'target', category:'category', lat:'lat', 
                       lon:'lon', lower_areal_unit: 'lower_areal_unit'}
        self.dests.set_index(idx, inplace=True)
        self.dests.rename(columns=rename_cols,inplace=True)
        if category == 'skip':
            self.dests['category'] = "CAT_UNDEFINED"
            self.valid_category = False
        if target == 'skip':
            self.valid_target = False
        if lower_areal_unit == 'skip':
            self.valid_lower_areal_unit = False
        if subset:
            self.dests = self.dests[self.dests['category'].isin(subset)]
        self.category_set = set()

        self.dests['category'].apply(str)
        self.category_set = set(self.dests['category'])

        #Disregard shapefile input to avoid spatial joins and potential calculation errors.
        #join dest table with shapefile
        #copy = self.dests.copy(deep=True)
        #geometry = [Point(xy) for xy in zip(copy['lon'], copy['lat'])]
        #crs = {'init':'epsg:4326'}
        #geo_dests = gpd.GeoDataFrame(copy, crs=crs, geometry=geometry)
        #boundaries_gdf = gpd.read_file(shapefile)
        #geo_dests = gpd.sjoin(boundaries_gdf, geo_dests, how='inner', op='intersects')
        #geo_dests.set_index('index_right', inplace=True)
        #self.dests = geo_dests[['category','lat','lon','target','community',]]

        self.dest_id_list = self.dests.index
        self.dests_good = True
        self.dest_filename = filename
