"""
Program to calculate the network time between every point in a set, hence: "p2p".
Written by Logan Noel for the Center for Spatial Data Science, 2018.
(runs in O(Elog(V)) time)

Also many thanks to OSM for supplying data: www.openstreetmap.org
"""

import time
import sys
import logging
import os
import json
from collections import deque
import ast
import scipy.spatial
from geopy.distance import vincenty
from jellyfish import jaro_winkler
import pandas as pd

from spatial_access.MatrixInterface import MatrixInterface
from spatial_access.NetworkInterface import NetworkInterface
from spatial_access.ConfigInterface import ConfigInterface


class TransitMatrix():
    '''
    A unified class to manage all aspects of computing a transit time matrix.
    Arguments:
        -network_type: 'walk', 'drive' or 'bike'
        -epsilon: [optional] smooth out the network edges
    '''

    def __init__(
            self,
            network_type,
            epsilon=0.05,
            walk_speed=None,
            primary_input=None,
            primary_input_field_mapping=None,
            secondary_input=None,
            secondary_input_field_mapping=None,
            read_from_file=None,
            primary_hints=None,
            secondary_hints=None,
            use_meters=False,
            debug=False):

        #arguments
        self.network_type = network_type
        self.epsilon = epsilon
        self.walk_speed = walk_speed
        self.primary_input = primary_input
        self.primary_input_field_mapping = primary_input_field_mapping
        self.secondary_input = secondary_input
        self.secondary_input_field_mapping = secondary_input_field_mapping
        self.read_from_file = read_from_file        
        self.primary_hints = primary_hints
        self.secondary_hints = secondary_hints
        self.use_meters = use_meters
        self.debug = debug

        #member variables
        self.sl_data = None
        self.primary_data = None
        self.secondary_data = None
        self.node_pair_to_speed = {}
        self.speed_limit_dictionary = None

        #instantiate interfaces
        self.INFINITY = -1
        self.set_logging()
        self._configInterface = ConfigInterface(network_type, self.logger)
        self._networkInterface = NetworkInterface(network_type, self.logger)
        self._matrixInterface = MatrixInterface(self.logger)

        assert network_type != 'bike', "bike mode is temporarily disabled"
        assert network_type in [
            'drive', 'walk', 'bike'], "network_type is not one of: ['drive', 'walk', 'bike'] "

        if read_from_file:
            self._matrixInterface.read_matrix_from_file(read_from_file)

    def set_logging(self):
        '''
        Set the proper logging and debugging level.
        '''

        if self.debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        if self.debug:
            self.logger.debug("Running in debug mode")

    @staticmethod
    def _get_output_filename(keyword, extension='csv'):
        '''
        Given a keyword, find an unused filename.
        '''
        if not os.path.exists("data/matrices/"):
            os.makedirs("data/matrices/")
        filename = 'data/matrices/{}_0.{}'.format(keyword, extension)
        counter = 1
        while os.path.isfile(filename):
            filename = 'data/matrices/{}_{}.{}'.format(
                keyword, counter, extension)
            counter += 1

        return filename

    def _load_sl_data(self, sl_filename):
        '''
        Load speed limit data from .csv. Identify street name and speed
        limit columns.
        '''
        if not sl_filename:
            return

        # sanity check & load data
        assertion_warning = "Selected 'drive' cost model but didn't provide speed limit file"
        assert (self.network_type == 'drive' and sl_filename) or (self.network_type !=
                                                                  'drive'), assertion_warning
        assert os.path.exists(
            sl_filename), "Unable to locate provided speed limit file"
        self.sl_data = pd.read_csv(sl_filename)
        source_data_columns = self.sl_data.columns.values

        # extract column names
        street_name = ''
        speed_limit = ''

        print('The variable names in your speed limit data set are:')
        for var in source_data_columns:
            print('> ', var)
        while street_name not in source_data_columns:
            street_name = input('Enter the street name variable name: ')
        while speed_limit not in source_data_columns:
            speed_limit = input('Enter the speed limit variable name: ')

        # clean the data frame
        clean_names = {street_name: 'street_name', speed_limit: 'speed_limit'}
        self.sl_data.rename(columns=clean_names, inplace=True)

        self.sl_data = self.sl_data[['street_name', 'speed_limit']]

    def _parse_csv(self, primary):
        '''
        Load source data from .csv. Identify long, lat and id columns.
        '''
        # decide which input to load
        field_mapping = None

        if primary:
            filename = self.primary_input
            field_mapping = self.primary_input_field_mapping
        else:
            filename = self.secondary_input
            field_mapping = self.secondary_input_field_mapping

        source_data = pd.read_csv(filename)
        source_data_columns = source_data.columns.values

        # extract the column names
        xcol = ''
        ycol = ''
        idx = ''
        skip_user_input = field_mapping
        # use the column names if we already have them
        try:
            if primary and self.primary_hints:
                xcol = self.primary_hints['xcol']
                ycol = self.primary_hints['ycol']
                idx = self.primary_hints['idx']
            elif not primary and self.secondary_hints:
                xcol = self.secondary_hints['xcol']
                ycol = self.secondary_hints['ycol']
                idx = self.secondary_hints['idx']
            skip_user_input = True

        except BaseException:
            pass

        # if the web app is instantiating a TransitMatrix object/calling this code,
        # a field_mapping dictionary should be present
        if field_mapping:
            xcol = field_mapping["lat"]
            ycol = field_mapping["lon"]
            idx = field_mapping["idx"]

        if not skip_user_input:
            print('The variables in your data set are:')
            for var in source_data_columns:
                print('> ', var)
            while xcol not in source_data_columns:
                xcol = input('Enter the latitude coordinate: ')
            while ycol not in source_data_columns:
                ycol = input('Enter the longitude coordinate: ')
            while idx not in source_data_columns:
                idx = input('Enter the index name: ')

        # drop nan lines
        pre_drop = len(source_data)
        source_data.dropna(subset=[xcol, ycol], axis='index', inplace=True)
        post_drop = len(source_data)

        dropped_lines = pre_drop - len(source_data)
        self.logger.info(
            'Total number of rows in the dataset: %d', pre_drop)
        if dropped_lines > 0:
            self.logger.warning(
                "Rows dropped due to missing latitude or longitude values: %d", dropped_lines)

        # set index and clean
        source_data.set_index(idx, inplace=True)
        source_data.rename(columns={xcol: 'x', ycol: 'y'}, inplace=True)
        source_data.index = source_data.index.map(str)
        if primary:
            self.primary_data = source_data[['x', 'y']]
        else:
            self.secondary_data = source_data[['x', 'y']]

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

        except BaseException as exception:
            self.logger.error(
                "Unable to Load inputs: %s", exception)
            sys.exit()

    def _clean_speed_limits(self):
        '''
        Map road segments to speed limits.
        '''
        edges = self._networkInterface.edges
        sl_file = self.sl_data

        start_time = time.time()

        # clean the table and standardize names
        sl_file.dropna(inplace=True, axis=0, how='any')
        sl_file['street_name'] = sl_file['street_name'].str.upper()
        edges['name'].fillna('PRIVATE', inplace=True)
        edges['name'] = edges['name'].str.upper()
        sl_file = sl_file[sl_file['speed_limit'] > 0]

        # load mappings for easy use
        limits = {}
        for row in sl_file.itertuples():
            limits[row[1]] = row[2]

        # extract edge names/ids from OSM network and assign defaut speed
        street_name_column_index = edges.columns.get_loc('name') + 1
        network_streets = {}
        for data in edges.itertuples():
            network_streets[data[street_name_column_index]] = 25

        remaining_names = set(limits.keys())

        perfect_match = 0
        great_match = 0
        good_match = 0
        non_match = 0

        # assign default value
        network_streets['PRIVATE'] = self._configInterface.DEFAULT_DRIVE_SPEED

        # attempt to match edges in OSM to known street names
        # and assign corresponding speed limit
        for name in network_streets:
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
                speed = network_streets[data[STR_NAME]]
            else:
                speed = 25
            node_pair_to_speed[(data[0][0], data[0][1])] = speed
            node_pair_to_speed[(data[0][1], data[0][0])] = speed

        self.logger.info(
            '''Matching street network completed in
            {:,.2f} seconds: %d perfect matches, %d near perfect matches,
            %d good matches and %d non matches''', time.time() - start_time,
                                                   perfect_match,
                                                   great_match,
                                                   good_match,
                                                   non_match)

        self.node_pair_to_speed = node_pair_to_speed

    def _cost_model(self, distance, sl):
        '''
        Return the edge impedence as specified by the cost model.
        '''
        if self.network_type == 'walk':
            return int(
                (distance /
                 self._configInterface.WALK_CONSTANT) +
                self._configInterface.WALK_NODE_PENALTY)
        elif self.network_type == 'bike':
            return int(
                (distance /
                 self._configInterface.BIKE_CONSTANT) +
                self._configInterface.BIKE_NODE_PENALTY)
        else:
            if sl:
                edge_speed_limit = sl
            else:
                # Logic reading in speed limits from either the user-supplied speed limit file or
                # the default speed limit dictionary should guarantee that the below code will
                # never execute.  Keep in for testing purposes until no longer
                # needed.
                self.logger.warning(
                    'Using default drive speed. Results will be inaccurate')
                edge_speed_limit = self._configInterface.DEFAULT_DRIVE_SPEED
            drive_constant = (edge_speed_limit / self._configInterface.ONE_HOUR) * self._configInterface.ONE_KM
            return int((distance / drive_constant) + self._configInterface.DRIVE_NODE_PENALTY)
        

    def _read_in_speed_limit_dictionary(self):
        filename = 'data/speed_limit_dictionary.json'

        try:
            with open(filename, "r") as f:
                self.speed_limit_dictionary = json.load(f)
        except FileNotFoundError:
            self.logger.error('%s not found, using defaults', filename)
   

    def _reduce_node_indeces(self):
        simple_node_indeces = {}
        for position, id_ in enumerate(self._networkInterface.nodes['id']):
            simple_node_indeces[id_] = position
        return simple_node_indeces


    # pylint: disable=too-many-branches,too-many-statements,invalid-name,attribute-defined-outside-init
    def _parse_network(self):
        '''
        Cleans and generates the city network.
        '''

        start_time = time.time()

        DISTANCE = self._networkInterface.edges.columns.get_loc('distance') + 1
        FROM_IDX = self._networkInterface.edges.columns.get_loc('from') + 1
        TO_IDX = self._networkInterface.edges.columns.get_loc('to') + 1
        ONEWAY = self._networkInterface.edges.columns.get_loc('oneway') + 1
        HIGHWAY = self._networkInterface.edges.columns.get_loc('highway') + 1

    
        # map index name to position
        simple_node_indeces = self._reduce_node_indeces()

        # read in the dictionary of speed limit values used to calculate edge
        # impedences
        self._read_in_speed_limit_dictionary()

        # create a mapping of each node to every other connected node
        # transform them by cost model as well
        for data in self._networkInterface.edges.itertuples():
            from_idx = data[FROM_IDX]
            to_idx = data[TO_IDX]
            if self.use_meters:
                impedence = data[DISTANCE]
            elif self.node_pair_to_speed:
                impedence = self._cost_model(
                    data[DISTANCE], self.node_pair_to_speed[(from_idx, to_idx)])
            else:
                highway_tag = data[HIGHWAY]
                if highway_tag is None or highway_tag not in self.speed_limit_dictionary[
                        "urban"]:
                    highway_tag = "unclassified"
                impedence = self._cost_model(data[DISTANCE], float(
                        self.speed_limit_dictionary["urban"][highway_tag]))

            oneway = data[ONEWAY]

            is_bidirectional = oneway != 'yes' or self.network_type != 'drive'
            self._matrixInterface.transit_matrix.addEdgeToGraph(simple_node_indeces[from_idx],
                             simple_node_indeces[to_idx], impedence, is_bidirectional)


        self.logger.info(
            "Prepared raw network in {:,.2f} seconds".format(time.time() - start_time))


    def _match_nn(self, isPrimary=True, noSecondaryExists=True):
        '''
        Maps each the index of each node in the raw distance
        matrix to a tuple
        containing (source_id, distance), where
        source_id is a member of the primary_source
        or secondary_source and distance is the number of meters
        between the (primary/secondary) source and its nearest OSM node.
        '''

        if isPrimary:
            data = self.primary_data
        else:
            data = self.secondary_data

        nodes = self._networkInterface.nodes[['x', 'y']]

        node_indices = nodes.index
        start_time = time.time()
        KM_TO_METERS = 1000 #pylint: disable=invalid-name

        # make a kd tree in the lat, long dimension
        node_array = pd.DataFrame.as_matrix(nodes)
        kd_tree = scipy.spatial.cKDTree(node_array)

        # map each node in the source/dest data to the nearest
        # corresponding node in the OSM network
        # and write to file
        for row in data.itertuples():
            origin_id, origin_y, origin_x = row
            latlong_diff, node_loc = kd_tree.query( # pylint: disable=unused-variable
                [origin_x, origin_y], k=1)
            node_number = node_indices[node_loc]
            distance = vincenty(
                (origin_y, origin_x), (nodes.loc[node_number].y, nodes.loc[node_number].x)).km

            #distance is a misnomer. this is meters or seconds, depending on config interface settings
            distance = int(distance * KM_TO_METERS / self._configInterface.defaultImpedenceForNetworkType)
            self.logger.info('origin_id: {}, type: {}'.format(origin_id, type(origin_id)))
            if isPrimary:
                self._matrixInterface.transit_matrix.addToUserSourceDataContainer(node_loc, 
                                                                                   bytes(origin_id, 'utf-8'), 
                                                                                   distance, 
                                                                                   noSecondaryExists)
            else:
                self._matrixInterface.transit_matrix.addToUserDestDataContainer(node_loc,
                                                                                 bytes(origin_id, 'utf-8'),
                                                                                 distance)

        self.logger.info(
            'Nearest Neighbor matching completed in {:,.2f} seconds', 
                time.time() - start_time)

    def write_to_file(self, outfile=None):
        '''
        Write the transit matrix to csv.
        Arguments:
            outfile- optional string
        '''
        if not outfile:
            outfile = self._get_output_filename(self.network_type)
        self._matrixInterface.write_to_csv(outfile)
        self.logger.info("Wrote file to %s", outfile)

    def process(self, speed_limit_filename=None):
        '''
        Process the data.
        '''
        start_time = time.time()

        self.logger.info(
            "Processing network (%s) with epsilon: %f",
            self.network_type,
            self.epsilon)

        self._load_inputs()

        self._load_sl_data(speed_limit_filename)

        self._networkInterface.load_network(self.primary_data, 
                                            self.secondary_data, 
                                            self.secondary_input is not None,
                                            self.epsilon)

        self._matrixInterface.prepare_matrix(self._networkInterface.number_of_nodes())

        self._parse_network()

        self._match_nn(True, not self.secondary_input)
        if self.secondary_input:
            self._match_nn(False, self.secondary_input)

        self._matrixInterface.build_matrix()

        self.logger.info(
            'All operations completed in {:,.2f} seconds',
                time.time() - start_time)
