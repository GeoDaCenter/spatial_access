#pylint disable=invalid-name
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
import scipy.spatial
from geopy.distance import vincenty
from jellyfish import jaro_winkler
import pandas as pd

from spatial_access.MatrixInterface import MatrixInterface
from spatial_access.NetworkInterface import NetworkInterface
from spatial_access.ConfigInterface import ConfigInterface

class TransitMatrixException(Exception):
    pass

class TransitMatrix():

    '''
    A unified class to manage all aspects of computing a transit time matrix.
    Arguments:
        -network_type: 'walk', 'drive' or 'bike'
        -epsilon: [optional] smooth out the network edges
        -primary_input: csv filename of the the rows input
        -primary_input_field_mapping: [optional] a dictionary with the column names of
            the index, lon and lat in the primary input
        -secondary_input: [optional] csv filename of the the column input. If not provided,
            the transit matrix will be symmetric using the primary input as rows and columns.
        -secondary_input_field_mapping: [optional] a dictionary with the column names of
            the index, lon and lat in the secondary input
        -read_from_file: [optional] a .csv or .tmx input of a previously calculated
            transit matrix to load
        -use_meters: [optional] Output will be in meters if True (seconds if False).
        -trim_edges: [optional] Merge sequential edges in the OSM network if True. Does not
            reduce accuracy, but is costly. Advised only for large networks.
        -debug: [optional] Enable debugging output.
    '''
    def __init__(
            self,
            network_type,
            epsilon=0.05,
            primary_input=None,
            secondary_input=None,
            read_from_file=None,
            primary_hints=None,
            secondary_hints=None,
            use_meters=False,
            disable_area_threshold=False,
            trim_edges=True,
            debug=False):

        #arguments
        self.network_type = network_type
        self.epsilon = epsilon
        self.primary_input = primary_input
        self.secondary_input = secondary_input
        self.read_from_file = read_from_file
        self.primary_hints = primary_hints
        self.secondary_hints = secondary_hints
        self.use_meters = use_meters
        self.trim_edges = trim_edges
        self.debug = debug

        #member variables
        self.primary_data = None
        self.secondary_data = None
        self.node_pair_to_speed = {}

        #instantiate interfaces
        self.set_logging()
        self._config_interface = ConfigInterface(network_type, logger=self.logger)
        self._network_interface = NetworkInterface(network_type, logger=self.logger, 
                                                   disable_area_threshold=disable_area_threshold)
        self._matrix_interface = MatrixInterface(logger=self.logger)

        assert network_type in [
            'drive', 'walk', 'bike', 'transit'], "network_type is not one of: ['drive', 'walk', 'bike', 'transit'] "

        if network_type is 'transit':
            assert read_from_file is not None, "must include read_from_file for transit network_type"
        if read_from_file:
            self._matrix_interface.read_from_file(read_from_file, isOTPMatrix=network_type=='transit')

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
    def _get_output_filename(keyword, extension):
        '''
        Given a keyword, find an unused filename.
        '''
        if not os.path.exists("data/matrices/"):
            os.makedirs("data/matrices/")
        if extension is None:
            filename = 'data/matrices/{}_0'.format(keyword)
        else:
            filename = 'data/matrices/{}_0.{}'.format(keyword, extension)
        counter = 1
        while os.path.isfile(filename):
            if extension is None:
                filename = 'data/matrices/{}_{}'.format(
                keyword, counter)
            else:    
                filename = 'data/matrices/{}_{}.{}'.format(
                    keyword, counter, extension)
            counter += 1

        return filename

    
    # pylint disable=too-many-branches
    def _parse_csv(self, primary):
        '''
        Load source data from .csv. Identify long, lat and id columns.
        '''
        # decide which input to load
        field_mapping = None

        if primary:
            filename = self.primary_input
        else:
            filename = self.secondary_input


        source_data = pd.read_csv(filename)
        source_data_columns = source_data.columns.values

        # extract the column names
        xcol = ''
        ycol = ''
        idx = ''
        skip_user_input = False
        # use the column names if we already have them
        try:
            if primary and self.primary_hints:
                xcol = self.primary_hints['xcol']
                ycol = self.primary_hints['ycol']
                idx = self.primary_hints['idx']
                skip_user_input = True
            elif not primary and self.secondary_hints:
                xcol = self.secondary_hints['xcol']
                ycol = self.secondary_hints['ycol']
                idx = self.secondary_hints['idx']
                skip_user_input = True

        except:
            #raise immediately to let the user know there is a problem
            if primary:
                self.logger.error('Unable to use primary_hints to read sources')
                raise TransitMatrixException('Unable to use primary_hints to read sources')
            else:
                self.logger.error('Unable to use secondary_hints to read dests')
                raise TransitMatrixException('Unable to use secondary_hints to read sources')
    
        if not skip_user_input:
            print('The variables in your data set are:')
            for var in source_data_columns:
                print('> ', var)
            while xcol not in source_data_columns:
                xcol = input('Enter the longitude coordinate: ')
            while ycol not in source_data_columns:
                ycol = input('Enter the latitude coordinate: ')
            while idx not in source_data_columns:
                idx = input('Enter the index name: ')

        # drop nan lines
        pre_drop = len(source_data)
        source_data.dropna(subset=[xcol, ycol], axis='index', inplace=True)

        dropped_lines = pre_drop - len(source_data)
        self.logger.info(
            'Total number of rows in the dataset: %d', pre_drop)
        if dropped_lines > 0:
            self.logger.warning(
                "Rows dropped due to missing latitude or longitude values: %d", dropped_lines)

        # set index and clean
        source_data.set_index(idx, inplace=True)
        source_data.rename(columns={xcol: 'x', ycol: 'y'}, inplace=True)

        if primary:
            self.primary_data = source_data[['x', 'y']]
            self.primary_hints = {'x':xcol, 'y':ycol, 'idx': idx}
        else:
            self.secondary_data = source_data[['x', 'y']]
            self.secondary_hints = {'x':xcol, 'y':ycol, 'idx': idx}

    def _load_inputs(self):
        '''
        Load one input file if the user wants a symmetric
        distance graph, or two for an asymmetric graph.
        '''
        if not os.path.isfile(self.primary_input):
            self.logger.error("Unable to find primary csv.")
            raise TransitMatrixException("Unable to find primary csv")
        if self.secondary_input:
            if not os.path.isfile(self.secondary_input):
                self.logger.error("Unable to find secondary csv.")
                raise TransitMatrixException("Unable to find secondary csv")
        try:
            self._parse_csv(True)
            if self.secondary_input:
                self._parse_csv(False)

        except BaseException as exception:
            self.logger.error(
                "Unable to Load inputs: %s", exception)
            raise TransitMatrixException("Unable to find load inputs")



    def _cost_model(self, distance, speed_limit):
        '''
        Return the edge impedence as specified by the cost model.
        '''
        if self.network_type == 'walk':
            return int((distance / self._config_interface.WALK_CONSTANT) +
                       self._config_interface.WALK_NODE_PENALTY)
        elif self.network_type == 'bike':
            return int((distance / self._config_interface.BIKE_CONSTANT) +
                       self._config_interface.BIKE_NODE_PENALTY)
        if speed_limit:
            edge_speed_limit = speed_limit
        else:
            # Logic reading in speed limits from either the user-supplied speed limit file or
            # the default speed limit dictionary should guarantee that the below code will
            # never execute.  Keep in for testing purposes until no longer
            # needed.
            self.logger.warning(
                'Using default drive speed. Results will be inaccurate')
            edge_speed_limit = self._config_interface.DEFAULT_DRIVE_SPEED
        drive_constant = (edge_speed_limit / self._config_interface.ONE_HOUR)
        drive_constant *= self._config_interface.ONE_KM
        return int((distance / drive_constant) + self._config_interface.DRIVE_NODE_PENALTY)


    def _reduce_node_indeces(self):
        '''
        Map the network indeces to location.
        '''
        simple_node_indeces = {}
        for position, id_ in enumerate(self._network_interface.nodes['id']):
            simple_node_indeces[id_] = position
        return simple_node_indeces


    # pylint: disable=too-many-branches,too-many-statements,invalid-name,attribute-defined-outside-init
    def _parse_network(self):
        '''
        Cleans and generates the city network.
        '''

        start_time = time.time()

        FROM_IDX = self._network_interface.edges.columns.get_loc('from') + 1
        TO_IDX = self._network_interface.edges.columns.get_loc('to') + 1
        
        # map index name to position
        simple_node_indeces = self._reduce_node_indeces()


        # create a mapping of each node to every other connected node
        # transform them by cost model as well
        for data in self._network_interface.edges.itertuples():
            from_idx = data[FROM_IDX]
            to_idx = data[TO_IDX]
            if self.use_meters:
                impedence = data.distance
            elif self.node_pair_to_speed:
                impedence = self._cost_model(
                    data.distance, self.node_pair_to_speed[(from_idx, to_idx)])
            else:
                highway_tag = data.highway
                assert isinstance(highway_tag, str), 'type: {}'.format(type(highway_tag))
                if highway_tag is None or highway_tag not in self._config_interface.speed_limit_dict["urban"]:
                    highway_tag = "unclassified"
                impedence = self._cost_model(data.distance,
                    self._config_interface.speed_limit_dict["urban"][highway_tag])

            is_bidirectional = data.oneway != 'yes' or self.network_type != 'drive'
            self._matrix_interface.add_edge_to_graph(simple_node_indeces[from_idx],
                                                     simple_node_indeces[to_idx],
                                                     impedence, is_bidirectional)
        time_delta = time.time() - start_time
        self.logger.info("Prepared raw network in {:,.2f} seconds".format(time_delta))


    def _match_nn(self, isPrimary=True, primary_only=True):
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

        nodes = self._network_interface.nodes[['x', 'y']]

        start_time = time.time()

        # make a kd tree in the lat, long dimension
        node_array = nodes.values
        kd_tree = scipy.spatial.cKDTree(node_array) # pylint: disable=not-callable

        # map each node in the source/dest data to the nearest
        # corresponding node in the OSM network
        # and write to file
        for row in data.itertuples():
            origin_id, origin_x, origin_y = row
            # pylint: disable=unused-variable
            latlong_diff, node_loc = kd_tree.query([origin_x, origin_y], k=1)
            node_number = nodes.index[node_loc]
            origin_location = (origin_y, origin_x)
            closest_node_location = (nodes.loc[node_number].y,
                                                       nodes.loc[node_number].x)

            #keep track of nodes that are used to snap a user data point
            self._network_interface.user_node_friends.add(node_number)
            distance = vincenty(origin_location, closest_node_location).m

            edge_weight = int(distance / self._config_interface.default_edge_cost)

            if isPrimary:
                # pylint disable=line-too-long
                self._matrix_interface.add_user_source_data(node_loc, origin_id, edge_weight, primary_only)
            else:
                # pylint disable=line-too-long
                self._matrix_interface.add_user_dest_data(node_loc, origin_id, edge_weight)

        time_delta = time.time() - start_time
        self.logger.info(
            'Nearest Neighbor matching completed in {:,.2f} seconds'.format(time_delta))

    def write_csv(self, outfile=None):
        '''
        Write the transit matrix to csv.

        Note: Use write_tmx (as opposed to this method) to
        save the transit matrix unless exporting for external use.

        Arguments:
            outfile-optional string
        '''
        if not outfile:
            outfile = self._get_output_filename(self.network_type, extension='csv')
        assert '.csv' in outfile, 'Error: given filename does not have the correct extension (.csv)'
        self._matrix_interface.write_to_csv(outfile)

    def write_tmx(self, outfile=None):
        '''
        Write the transit matrix to tmx.

        Note: Use this method (as opposed to write_csv) to 
        save the transit matrix unless exporting data for 
        external use.

        Arguments:
            outfile-optional string
        '''
        if not outfile:
            outfile = self._get_output_filename(self.network_type, extension=None)
        assert '.' not in outfile, 'Error: output filename must be a directory'
        self._matrix_interface.write_to_tmx(outfile)

    def prefetch_network(self):
        '''
        Fetch and cache the osm network.

        '''
        self._load_inputs()

        self._network_interface.load_network(self.primary_data,
                                             self.secondary_data,
                                             self.secondary_input is not None,
                                             self.epsilon)

    def process(self):
        '''
        Process the data.
        '''
        assert self.network_type is not 'transit', 'OTP matrix does not need to be processed'

        start_time = time.time()

        self.logger.info("Processing network (%s) with epsilon: %f",
                         self.network_type, self.epsilon)

        self.prefetch_network()
        isSymmetric = self.secondary_input is None and self.network_type in ['walk', 'bike']
        self._matrix_interface.prepare_matrix(self._network_interface.number_of_nodes(), 
                                              isSymmetric)

        self._match_nn(True, not self.secondary_input)
        if self.secondary_input:
            self._match_nn(False, self.secondary_input)

        if self.trim_edges:
            try:
                self._network_interface._trim_edges()
            except:
                if self.logger:
                    self.logger.warning('Failed to optimize network. Please report this event.')

        self._parse_network()

        # offload primary and secondary input data frames because we don't need them anymore
        self.primary_input = None
        self.secondary_input = None

        self._matrix_interface.build_matrix()
        time_delta = time.time() - start_time



        self.logger.info('All operations completed in {:,.2f} seconds'.format(time_delta))
