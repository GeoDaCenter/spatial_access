import numpy as np
import multiprocessing, math
import scipy.spatial
from sklearn.neighbors import NearestNeighbors
from geopy.distance import vincenty
from NetworkQuery import Query
from jellyfish import jaro_winkler
import geopandas as gpd
import pandas as pd
import time, sys, os.path, csv, json, logging, os, psutil
from pandana.loaders import osm
try:
    from pyengine import *
except:
    print('Unable to import pyengine. Try running setup.py again')

# Program to calculate the network time between every point in a set, hence: "p2p".
# Written by Logan Noel for the Center for Spatial Data Science, 2018.
# (runs in O(Elog(V)) time)

# Also many thanks to OSM for supplying data: www.openstreetmap.org   

def geo_area(lat1, lon1, lat2, lon2):
    '''
    Given the coordinates of a bounding box, return the area
    in square kilometers.
    '''

    EARTH_RADIUS = 6371
    area =  math.pi * (EARTH_RADIUS ** 2) 
    area *= abs(math.degrees(math.sin(lat1)) - math.degrees(math.sin(lat2))) 
    area *= abs(lon1 - lon2) / 180

    return area


class pyTMatrix(object):
    '''
    A wrapper for C++ based pandas DataFrame like object.
    '''
    def __init__(self, infile, nn_pinfile, nn_sinfile, outfile,
     N, impedence, num_threads, outer_node_rows, outer_node_cols, mode, 
     write_to_file, load_to_mem, read_from_file=False):

        GB = 1073741824
        if write_to_file and not load_to_mem:
            write_mode = 0
        elif write_to_file and load_to_mem:
            write_mode = 1
        elif not write_to_file and load_to_mem:
            write_mode = 2
        elif (read_from_file) and (not write_to_file) and (not load_to_mem):
            write_mode = 3
        if load_to_mem:
            expected_memory = int(2 * outer_node_cols * outer_node_rows / GB)
            system_memory = int(psutil.virtual_memory().total / GB)
            if expected_memory > system_memory:
                warning_text = '''WARNING: Expected memory ({} Gb) is greater than 
                available system memory ({} Gb). P2p will likely crash, 
                please run in write only mode (not load_to_mem)'''.format(expected_memory, system_memory)
                print(warning_text)

       
        self.tm = tmatrix(infile.encode('UTF-8'), nn_pinfile.encode('UTF-8'),
            nn_sinfile.encode('UTF-8'), outfile.encode('UTF-8'), N, impedence,
            num_threads, outer_node_rows, outer_node_cols, mode, write_mode)



class TransitMatrix(object):
    '''
    A unified class to manage all aspects of computing a transit time matrix.
    Arguments:
        -network_type: 'walk', 'drive' or 'bike'
        -epsilon: [optional] smooth out the network edges
        -primary_input: 
    '''
    def __init__(self, network_type, epsilon=0.05, primary_input=None, 
        secondary_input=None, output_type='csv', n_best_matches=4, 
        read_from_file=None, write_to_file=False, load_to_mem=True,
        primary_hints=None, secondary_hints=None):

        self.network_type = network_type
        self.epsilon = epsilon
        self.primary_input = primary_input
        self.secondary_input = secondary_input
        self.sl_data = None
        self.primary_data = None
        self.secondary_data = None
        self.num_nodes = 0
        self.num_edges = 0
        self.nodes = None
        self.edges = None
        self.n_best_matches = n_best_matches
        self.output_type = output_type
        self.read_from_file = read_from_file
        if read_from_file:
            self.write_to_file = False
            self.load_to_mem = False
        else:
            self.write_to_file = write_to_file
            self.load_to_mem = load_to_mem

        self.network_filename = None
        self.output_filename = None
        self.nn_primary_filename = None
        self.nn_secondary_filename = None

        self.primary_hints = primary_hints
        self.secondary_hints = secondary_hints

        self.bbox = []
        self.node_pair_to_speed = {}
        self.tmatrix = None

        #CONSTANTS
        self.HUMAN_WALK_SPEED = 5 #km per hour
        self.BIKE_SPEED = 15 #km per hour
        self.ONE_HOUR = 3600 #seconds
        self.ONE_KM = 1000 #meters
        self.WALK_CONSTANT = (self.HUMAN_WALK_SPEED / self.ONE_HOUR) * self.ONE_KM
        self.WALK_NODE_PENALTY = 0
        self.BIKE_CONSTANT = (self.BIKE_SPEED / self.ONE_HOUR) * self.ONE_KM
        self.BIKE_NODE_PENALTY = 0

        self.DEFAULT_DRIVE_SPEED = 40 #km per hour
        self.DRIVE_CONSTANT = (self.DEFAULT_DRIVE_SPEED / self.ONE_HOUR) * self.ONE_KM 
        self.DRIVE_NODE_PENALTY = 0
        self.INFINITY = -1

        self.debug = False
        assert network_type != 'bike', "bike mode is temporarily disabled"
        assert network_type in ['drive', 'walk', 'bike'], "network_type is not one of: ['drive', 'walk', 'bike'] "

        assert (write_to_file or load_to_mem or read_from_file), "Need to (write_to_file and or load_to_mem) or read_from_file, can't do nothing"

    def get(self, source, dest):
        '''
        Fetch the time value associated with the source, dest pair.
        '''
        assert self.tmatrix != None, "tmatrix does not yet exist"
        try:
            return self.tmatrix.tm.get(str(source), str(dest))
        except:
            self.logger.error('Source, dest pair could not be found')


    def _load_parameters(self, filename='p2p_parameters.json'):
        '''
        Load model parameters from json.
        '''
        try:
            with open(filename) as json_data:
                params = json.load(json_data)

                self.HUMAN_WALK_SPEED = params['walk']['default_speed']
                self.WALK_NODE_PENALTY = params['walk']['node_penalty']

                self.DEFAULT_DRIVE_SPEED = params['drive']['default_speed']
                self.DRIVE_NODE_PENALTY = params['drive']['node_penalty']

                self.BIKE_SPEED = params['bike']['default_speed']
                self.BIKE_NODE_PENALTY = params['bike']['node_penalty']

                self.WALK_CONSTANT = (self.HUMAN_WALK_SPEED / self.ONE_HOUR) * self.ONE_KM
                self.BIKE_CONSTANT = (self.BIKE_SPEED / self.ONE_HOUR) * self.ONE_KM
                self.DRIVE_CONSTANT = (self.DEFAULT_DRIVE_SPEED / self.ONE_HOUR) * self.ONE_KM
        except:
            raise EnvironmentError("Necessary file: {} could not be found in current directory".format(filename))


    def set_logging(self, debug=False):
        '''
        Set the proper logging and debugging level.
        '''

        if debug:
            logging.basicConfig(level=logging.DEBUG)
            self.debug = True
        else:
            logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

        if debug:
             self.logger.debug("Running in debug mode") 

    def _get_output_filename(self, keyword, extension='csv'):
        '''
        Given a keyword, find an unused filename.
        '''
        if not os.path.exists("data/"):
            os.makedirs("data/")
        filename = 'data/{}_0.{}'.format(keyword, extension)
        counter = 1
        while os.path.isfile(filename):
            filename = 'data/{}_{}.{}'.format(keyword, counter, extension)
            counter += 1

        return filename


    def _load_sl_data(self, sl_filename):
        '''
        Load speed limit data from .csv. Identify street name and speed
        limit columns.
        '''
        if not sl_filename:
            return

        #sanity check & load data
        assert (self.network_type == 'drive' and sl_filename) or (self.network_type != 'drive'), "Selected 'drive' cost model but didn't provide speed limit file"
        assert os.path.exists(sl_filename), "Unable to locate provided speed limit file"
        self.sl_data = pd.read_csv(sl_filename)
        source_data_columns = self.sl_data.columns.values

        #extract column names
        street_name = ''
        speed_limit = ''

        print('The variable names in your speed limit data set are:')
        for var in source_data_columns:
            print('> ',var)
        while street_name not in source_data_columns:
            street_name = input('Enter the street name variable name: ')
        while speed_limit not in source_data_columns:
            speed_limit = input('Enter the speed limit variable name: ')
        
        #clean the data frame
        clean_names = {street_name:'street_name',speed_limit:'speed_limit'}
        self.sl_data.rename(columns=clean_names, inplace=True)

        self.sl_data = self.sl_data[['street_name','speed_limit']]


    def _parse_csv(self, primary):
        '''
        Load source data from .csv. Identify long, lat and id columns.
        '''
        #decide which input to load
        if primary:
            filename = self.primary_input
        else:
            filename = self.secondary_input

        
        source_data = pd.read_csv(filename)
        source_data_columns = source_data.columns.values

        #extract the column names
        xcol = ''
        ycol = ''
        idx = ''


        #use the column names if we already have them
        try:
            if primary and self.primary_hints:
                xcol = self.primary_hints['xcol']
                ycol = self.primary_hints['ycol']
                idx = self.primary_hints['idx']
            elif not primary and self.secondary_hints:
                xcol = self.secondary_hints['xcol']
                ycol = self.secondary_hints['ycol']
                idx = self.secondary_hints['idx']
        except:
            pass


        print('The variables in your data set are:')
        for var in source_data_columns:
            print('> ',var)
        while xcol not in source_data_columns:
            xcol = input('Enter the latitude coordinate: ')
        while ycol not in source_data_columns:
            ycol = input('Enter the longitude coordinate: ')
        while idx not in source_data_columns:
            idx = input('Enter the index name: ')

        #drop nan lines
        pre_drop_indices = source_data.index
        pre_drop = len(source_data)
        source_data.dropna(subset=[xcol, ycol], axis='index', inplace=True)
        post_drop_indices = source_data.index
        post_drop = len(source_data)
       
        dropped_lines = pre_drop - len(source_data)
        self.logger.info('Total number of rows in the dataset: {}'.format(pre_drop))
        self.logger.info('Complete number of rows for computing the matrix: {}'.format(post_drop))
        self.logger.info("Total number of rows dropped due to missing latitude or longitude values: {}".format(dropped_lines))

        #set index and clean
        source_data.set_index(idx, inplace=True)
        source_data.rename(columns={xcol:'x',ycol:'y'},inplace=True)
        source_data.index = source_data.index.map(str)
        if primary:
            self.primary_data = source_data[['x','y']]
        else:
            self.secondary_data = source_data[['x','y']]


    def _load_inputs(self):
        '''
        Load one input file if the user wants a symmetric
        distance graph, or two for an asymmetric graph.
        '''
        if not os.path.isfile(self.primary_input):
            self.logger.error("Unable to find primary csv.")
            sys.exit()
        if self.secondary_input:
            if not os.path.isfile(self.secondary_input):
                self.logger.error("Unable to find secondary csv.")
                sys.exit()
        try:
            self._parse_csv(True)
            if self.secondary_input:
                self._parse_csv(False)

        except:
            self.logger.error("Unable to find matching network. Did you reverse lat/long?")
            sys.exit()


    def _get_bbox(self):
        '''
        Figure out how to set the upper left and lower right corners
        of the bounding box which
        is used to request a streed/road/path network from OSM, 
        including a small correction to account for nodes that might
        lay just beyond the most distant data points.
        '''
        if self.secondary_input:
            composite_x = list(self.primary_data.x) + list(self.secondary_data.x)
            composite_y = list(self.primary_data.y) + list(self.secondary_data.y)
        else:
            composite_x = list(self.primary_data.x)
            composite_y = list(self.primary_data.y)

        if max(composite_x) > 0:
            ul_x = max(composite_x) + self.epsilon
        else:
            ul_x = max(composite_x) - self.epsilon
        if min(composite_x) > 0:
            lr_x = min(composite_x) - self.epsilon
        else:
            lr_x = min(composite_x) + self.epsilon

        if max(composite_y) > 0:
            ul_y = max(composite_y) - self.epsilon
        else:  
            ul_y = max(composite_y) - self.epsilon
        if min(composite_y) > 0:
            lr_y = min(composite_y) + self.epsilon
        else:
            lr_y = min(composite_y) + self.epsilon

        self.bbox = [ul_x, ul_y, lr_x, lr_y]
        self.logger.debug('set bbox: {}'.format(self.bbox))


    def _set_output_filename(self, output_filename):
        '''
        Set the output filename to a default value or given.
        '''
        if not output_filename:
            key_phrase = '{}_full_results'.format(self.network_type)
            self.output_filename = self._get_output_filename(key_phrase, 
                self.output_type)
        else:
            self.output_filename = output_filename


    def _get_thread_limit(self):
        '''
        Determine if the algorithm should be throttled
        based on the available system memory and number of cores.
        Returns: int (num threads to use)
        '''

        no_cores = multiprocessing.cpu_count()
        if no_cores > 2:
            no_cores -= 1
        else:
            no_cores = 1

        self.available_threads = no_cores


    def _clean_speed_limits(self):
        '''
        Map road segments to speed limits.
        '''
        edges = self.edges
        sl_file = self.sl_data

        start_time = time.time()

        #clean the table and standardize names
        sl_file.dropna(inplace=True, axis=0, how='any')
        sl_file['street_name'] = sl_file['street_name'].str.upper()
        edges['name'].fillna('PRIVATE', inplace=True)
        edges['name'] = edges['name'].str.upper()
        sl_file = sl_file[sl_file['speed_limit'] > 0]
        
        #load mappings for easy use
        limits = {}
        for row in sl_file.itertuples():
            limits[row[1]] = row[2]

        #extract edge names/ids from OSM network and assign defaut speed
        STR_NAME = edges.columns.get_loc('name') + 1
        network_streets = {}
        for data in edges.itertuples():
            network_streets[data[STR_NAME]] = 25
        
        remaining_names = set(limits.keys())

        perfect_match = 0
        great_match = 0
        good_match = 0
        non_match = 0

        #assign default value
        network_streets['PRIVATE'] = self.DEFAULT_DRIVE_SPEED

        #attempt to match edges in OSM to known street names
        #and assign corresponding speed limit
        for name in network_streets.keys():
            if name != 'PRIVATE':
                if name in remaining_names:
                    network_streets[name] = limits[name]
                    perfect_match += 1
                else:
                    best_distance = 0
                    best_match = None
                    for potential_match in remaining_names:
                        distance = jaro_winkler(name, potential_match)
                        if distance >= 0.97:
                            best_distance = distance
                            best_match = potential_match
                            great_match += 1
                            break
                        if distance > best_distance:
                            best_distance = distance
                            best_match = potential_match
                    if best_match and best_distance > 0.9:
                        network_streets[name] = limits[best_match]
                        good_match += 1
                    else:
                        non_match += 1
                        network_streets[name] = 25


        node_pair_to_speed = {}
        for data in edges.itertuples():
            if data[STR_NAME] in network_streets.keys():
                speed =  network_streets[data[STR_NAME]]
            else:
                speed = 25
            node_pair_to_speed[(data[0][0], data[0][1])] = speed
            node_pair_to_speed[(data[0][1], data[0][0])] = speed 

        self.logger.info('''Matching street network completed in 
            {:,.2f} seconds: {} perfect matches, {} near perfect matches,
            {} good matches and {} non matches'''.format(time.time() - start_time, 
                perfect_match, great_match, good_match, non_match))

        self.node_pair_to_speed = node_pair_to_speed

      
    def _cost_model(self, distance, sl):
        '''
        Return the edge impedence as specified by the cost model.
        '''
        if self.network_type == 'walk':
            return int((distance / self.WALK_CONSTANT) + self.WALK_NODE_PENALTY)
        elif self.network_type == 'bike':
            return int((distance / self.BIKE_CONSTANT) + self.BIKE_NODE_PENALTY)
        else:
            if sl:
                edge_speed_limit = sl
            else:
                #if we weren't provided speed limit data, we use defaults
                #ideally, never want to be here
                self.logger.warning('Using default drive speed. Results will be inaccurate')
                edge_speed_limit = self.DEFAULT_DRIVE_SPEED
            drive_constant = (edge_speed_limit / self.ONE_HOUR) * self.ONE_KM
            return int((distance / drive_constant) + self.DRIVE_NODE_PENALTY) 


    def _request_network(self):
        '''
        Fetch a street network from OSM that encompasses the data points.
        Writes three .csv files:
            distance_matrix: matrix representing the distance from each point in
            the OSM network to every other point (in meters)
            nodes: list of all nodes in the network
            edges: list of all edges in the network
        '''
        
        self.network_filename = self._get_output_filename("raw_network")
        self._get_bbox()

        #query OSM
        try:
            self.nodes, self.edges = osm.network_from_bbox(self.bbox[0], 
                self.bbox[1], self.bbox[2], self.bbox[3],
                network_type=self.network_type)
        except:
            request_error = '''Error trying to download OSM network. 
            Did you reverse lat/long? 
            Is your network connection functional?
            '''
            self.logger.error(request_error)
            sys.exit()


        if self.network_type == 'drive':
            self._clean_speed_limits()


        self.num_nodes = len(self.nodes)
        self.num_edges = len(self.edges)

        start_time = time.time()

        #map index name to position
        node_index_to_loc = {}
        for i, index_name in enumerate(self.nodes.index):
            node_index_to_loc[index_name] = i

        DISTANCE = self.edges.columns.get_loc('distance') + 1
        FROM_IDX = self.edges.columns.get_loc('from') + 1
        TO_IDX = self.edges.columns.get_loc('to') + 1
        ONEWAY = self.edges.columns.get_loc('oneway') + 1

        #create a mapping of each node to every other connected node
        #transform them by cost model as well
        with open(self.network_filename, 'w') as csvfile:
            writer = csv.writer(csvfile)
            for data in self.edges.itertuples():
                from_idx = data[FROM_IDX]
                to_idx = data[TO_IDX]
                if self.node_pair_to_speed:
                    impedence = self._cost_model(data[DISTANCE], 
                        self.node_pair_to_speed[(from_idx, to_idx)])
                else:
                    impedence = self._cost_model(data[DISTANCE], None)
                oneway = data[ONEWAY]
                
                writer.writerow([node_index_to_loc[from_idx], 
                    node_index_to_loc[to_idx], impedence])

                if oneway != 'yes':
                    writer.writerow([node_index_to_loc[to_idx], 
                        node_index_to_loc[from_idx], impedence])

        
        self.logger.info("Prepared raw network in {:,.2f} seconds and wrote to: {}".format(time.time() - start_time, self.network_filename))


    def _calc_shortest_path(self):
        '''
        Outsources the work of computing the shortest path matrix
        to a C++ module.
        '''

        start_time = time.time()

        #if we are provided a .csv shortest path matrix, load it 
        #to memory
        if self.read_from_file:
            try:
                self.tmatrix = pyTMatrix(self.read_from_file,
                    "none", "none", "none", 0, 0.0, 1, 0, 0, 0, 
                    write_to_file=False, load_to_mem=False, read_from_file=True)
                logger_vars = time.time() - start_time
                self.logger.info('Shortest path matrix loaded from disk in {:,.2f} seconds'.format(logger_vars))
                return
            except:
                self.logger.error('Unable to load matrix from file')
                sys.exit()

        #determine initialization conditions for generating matrix
        if self.network_type == 'walk':
            imp_val = self.WALK_CONSTANT
        elif self.network_type == 'bike':
            imp_val = self.BIKE_CONSTANT
        else:
            imp_val = self.DRIVE_CONSTANT


        outer_node_rows = len(self.primary_data)
        if self.secondary_input:
            outer_node_cols = len(self.secondary_data)
        else:
            outer_node_cols = len(self.primary_data)
        if self.output_type == 'csv':
            nearest_neighbors = 0
        else:
            nearest_neighbors = self.n_best_matches
    
        if self.write_to_file:
            self.logger.info('Writing to file: {}'.format(self.output_filename))
        
        self.tmatrix = pyTMatrix(self.network_filename,
            self.nn_primary_filename, self.nn_secondary_filename,
            self.output_filename, self.num_nodes, imp_val, 
            self.available_threads, outer_node_rows, outer_node_cols, 
            nearest_neighbors, write_to_file=self.write_to_file, 
            load_to_mem=self.load_to_mem, read_from_file=False)
        
        logger_vars = time.time() - start_time
        self.logger.info('Shortest path matrix computed in {:,.2f} seconds'.format(logger_vars))
    

    def _match_nn(self, secondary):
        '''
        Maps each the index of each node in the raw distance 
        matrix to a tuple
        containing (source_id, distance), where
        source_id is a member of the primary_source
        or secondary_source and distance is the number of meters
        between the (primary/secondary) source and its nearest OSM node.
        '''

        if secondary:
            self.nn_secondary_filename = self._get_output_filename("nn_secondary")
            data = self.secondary_data
            filename = self.nn_secondary_filename
        else:
            self.nn_primary_filename = self._get_output_filename("nn_primary")
            self.nn_secondary_filename = self.nn_primary_filename
            data = self.primary_data
            filename = self.nn_primary_filename

        nodes = self.nodes[['x', 'y']]

        node_indices = nodes.index
        start_time = time.time()
        KM_TO_METERS = 1000

        #make a kd tree in the lat, long dimension
        node_array = pd.DataFrame.as_matrix(nodes)
        kd_tree = scipy.spatial.cKDTree(node_array)

        #map each node in the source/dest data to the nearest
        #corresponding node in the OSM network
        #and write to file
        with open(filename, 'w') as csvfile_w:
            writer = csv.writer(csvfile_w)
            for row in data.itertuples():
                origin_id, origin_y, origin_x = row
                latlong_diff, node_loc = kd_tree.query([origin_x, origin_y],k=1)
                node_number = node_indices[node_loc]
                distance = vincenty((origin_y, origin_x), (nodes.loc[node_number].y, 
                    nodes.loc[node_number].x)).km

                distance = int(distance * KM_TO_METERS)

                writer.writerow([node_loc, origin_id, distance])

        self.logger.info('Nearest Neighbor matching completed in {:,.2f} seconds'.format(time.time() - start_time))



    def _cleanup_artifacts(self, cleanup):
        '''
        Cleanup the files left over from computation.
        '''
        if not cleanup:
            return
        files = os.listdir("data")
        for file in files:
            if 'raw_network' in file or 'nn_primary' in file or 'nn_secondary' in file:
                os.remove('data/' + file)
        if os.path.isfile('p2p.log'):
            os.remove('p2p.log')
        if os.path.isfile('logs'):
            os.rmdir('logs')
        if os.path.isfile('__pycache__'):
            os.rmdir('__pycache__')
        print("Cleaned up calculation artifacts")


    def process(self, speed_limit_filename=None, output_filename=None, 
                cleanup=True, debug=False):
        '''
        Process the data.
        '''

        self.set_logging(debug)

        #load from file if given
        if self.read_from_file:
            self.logger.info('Loading data from file: {}'.format(self.read_from_file))
            self._calc_shortest_path()
            return

        #sanity check
        if self.network_type == 'drive':
            if not speed_limit_filename:
                self.logger.error('Network type is drive. Must provide speed limit table')
                sys.exit()
              

        self.logger.info("Processing network ({}) in format: {} with epsilon: {}".format(self.network_type, 
            self.output_type, self.epsilon))

        self._load_inputs()

        self._get_thread_limit()

        self._load_parameters()

        self._load_sl_data(speed_limit_filename)

        start_time = time.time()

        self._set_output_filename(output_filename)

        self._request_network()

        self._match_nn(False)
        if self.secondary_input:
            self._match_nn(True)

        self._calc_shortest_path()

        self._cleanup_artifacts(cleanup)

        self.logger.info('All operations completed in {:,.2f} seconds'.format(time.time() - start_time))
