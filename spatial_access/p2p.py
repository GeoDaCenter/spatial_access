# Logan Noel (github.com/lmnoel)
#
# ©2017-2019, Center for Spatial Data Science

# pylint disable=invalid-name

import time
import logging
import os
import scipy.spatial
from geopy import distance
import pandas as pd

from spatial_access.MatrixInterface import MatrixInterface
from spatial_access.NetworkInterface import NetworkInterface
from spatial_access.ConfigInterface import ConfigInterface

from spatial_access.SpatialAccessExceptions import PrimaryDataNotFoundException
from spatial_access.SpatialAccessExceptions import SecondaryDataNotFoundException
from spatial_access.SpatialAccessExceptions import UnableToParsePrimaryDataException
from spatial_access.SpatialAccessExceptions import UnableToParseSecondaryDataException
from spatial_access.SpatialAccessExceptions import UnknownModeException
from spatial_access.SpatialAccessExceptions import InsufficientDataException
from spatial_access.SpatialAccessExceptions import DuplicateInputException


class TransitMatrix:

    """
    A unified class to manage all aspects of computing a transit time matrix.
    Arguments:
        -network_type: 'walk', 'drive' or 'bike'
        -epsilon: [optional] smooth out the network edges
        -primary_input: csv filename of the the rows input
        -primary_hints: [optional] a dictionary with the column names of
            the index, lon and lat in the primary input
        -secondary_input: [optional] csv filename of the the column input. If not provided,
            the transit matrix will be symmetric using the primary input as rows and columns.
        -secondary_hints: [optional] a dictionary with the column names of
            the index, lon and lat in the secondary input
        -read_from_h5: [optional] a .csv or .tmx input of a previously calculated
            transit matrix to load
        -use_meters: [optional] Output will be in meters if True (seconds if False).
        -debug: [optional] Enable debugging output.
    """
    def __init__(
            self,
            network_type,
            epsilon=0.05,
            primary_input=None,
            secondary_input=None,
            read_from_h5=None,
            primary_hints=None,
            secondary_hints=None,
            use_meters=False,
            disable_area_threshold=False,
            debug=False):

        # arguments
        self.network_type = network_type
        self.epsilon = epsilon
        self.primary_input = primary_input
        self.secondary_input = secondary_input
        self.read_from_h5 = read_from_h5
        self.primary_hints = primary_hints
        self.secondary_hints = secondary_hints
        self.use_meters = use_meters

        # member variables
        self.primary_data = None
        self.secondary_data = None
        self.node_pair_to_speed = {}

        # start the logger
        self.logger = None
        self.set_logging(debug)

        # instantiate interfaces
        self._config_interface = ConfigInterface(network_type, logger=self.logger)
        self._network_interface = NetworkInterface(network_type, logger=self.logger,
                                                   disable_area_threshold=disable_area_threshold)

        self.matrix_interface = MatrixInterface(primary_input_name=primary_input,
                                                secondary_input_name=secondary_input,
                                                logger=self.logger, )

        if network_type not in ['drive', 'walk', 'bike', 'transit']:
            raise UnknownModeException()

        if self.primary_input == self.secondary_input and self.primary_input is not None:
            raise DuplicateInputException("Gave duplicate inputs: {}".format(self.primary_input))

        # need to supply either:
        if primary_input is None and read_from_h5 is None:
            raise InsufficientDataException()

        if read_from_h5:
            self.matrix_interface.read_h5(read_from_h5)

    def set_logging(self, debug):
        """
        Set the proper logging and debugging level.
        """

        if debug:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.logger.debug("Running in debug mode")

    @staticmethod
    def _get_output_filename(keyword, extension):
        """
        Given a keyword, find an unused filename.
        """
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
        """
        Load source data from .csv. Identify lon, lon and id columns.
        """
        if primary:
            filename = self.primary_input
        else:
            filename = self.secondary_input

        source_data = pd.read_csv(filename)
        source_data_columns = source_data.columns.values

        # extract the column names
        lon = ''
        lat = ''
        idx = ''
        skip_user_input = False
        # use the column names if we already have them

        try:
            if primary and self.primary_hints:
                lon = self.primary_hints['lon']
                lat = self.primary_hints['lat']
                idx = self.primary_hints['idx']
                skip_user_input = True
            elif not primary and self.secondary_hints:
                lon = self.secondary_hints['lon']
                lat = self.secondary_hints['lat']
                idx = self.secondary_hints['idx']
                skip_user_input = True

        except KeyError:
            # raise immediately to let the user know there is a problem
            if primary:
                self.logger.error('Unable to use primary_hints to read sources')
                raise UnableToParsePrimaryDataException('Unable to use primary_hints to read sources')
            else:
                self.logger.error('Unable to use secondary_hints to read dests')
                raise UnableToParseSecondaryDataException('Unable to use secondary_hints to read sources')
    
        if not skip_user_input:
            print('The variables in your data set are:')
            for var in source_data_columns:
                print('> ', var)
            while lon not in source_data_columns:
                lon = input('Enter the longitude coordinate: ')
            while lat not in source_data_columns:
                lat = input('Enter the latitude coordinate: ')
            while idx not in source_data_columns:
                idx = input('Enter the index name: ')

        # drop nan lines
        pre_drop = len(source_data)
        source_data.dropna(subset=[lon, lat], axis='index', inplace=True)

        dropped_lines = pre_drop - len(source_data)
        self.logger.info(
            'Total number of rows in the dataset: %d', pre_drop)
        if dropped_lines > 0:
            self.logger.warning(
                "Rows dropped due to missing latitude or longitude values: %d", dropped_lines)

        # set index and clean
        if primary:
            self.matrix_interface.primary_ids_are_string = source_data[idx].dtype != int
        else:
            self.matrix_interface.secondary_ids_are_string = source_data[idx].dtype != int
        source_data.set_index(idx, inplace=True)

        source_data.rename(columns={lon: 'lon', lat: 'lat'}, inplace=True)
        if primary:
            self.primary_data = source_data[['lon', 'lat']]
            self.primary_hints = {'idx': idx, 'lon': lon, 'lat': lat}
        else:
            self.secondary_data = source_data[['lon', 'lat']]
            self.secondary_hints = {'idx': idx, 'lon': lon, 'lat': lat}

    def _load_inputs(self):
        """
        Load one input file if the user wants a symmetric
        distance graph, or two for an asymmetric graph.
        """
        if not os.path.isfile(self.primary_input):
            self.logger.error("Unable to find primary csv.")
            raise PrimaryDataNotFoundException("Unable to find primary csv")
        if self.secondary_input:
            if not os.path.isfile(self.secondary_input):
                self.logger.error("Unable to find secondary csv.")
                raise SecondaryDataNotFoundException("Unable to find secondary csv")
        else:
            self.matrix_interface.secondary_ids_are_string = self.matrix_interface.primary_ids_are_string
        try:
            self._parse_csv(True)
            if self.secondary_input:
                self._parse_csv(False)

        except BaseException:
            if self.secondary_input:
                raise UnableToParseSecondaryDataException()
            else:
                raise UnableToParsePrimaryDataException()

    def _cost_model(self, distance, speed_limit):
        """
        Return the edge impedence as specified by the cost model.
        """
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
        """
        Map the network indeces to location.
        """
        simple_node_indeces = {}
        for position, id_ in enumerate(self._network_interface.nodes['id']):
            simple_node_indeces[id_] = position
        return simple_node_indeces

    # pylint: disable=too-many-branches,too-many-statements,invalid-name,attribute-defined-outside-init
    def _parse_network(self):
        """
        Cleans and generates the city network.
        """

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
            self.matrix_interface.add_edge_to_graph(simple_node_indeces[from_idx],
                                                    simple_node_indeces[to_idx],
                                                    impedence, is_bidirectional)
        time_delta = time.time() - start_time
        self.logger.info("Prepared raw network in {:,.2f} seconds".format(time_delta))

    def _match_nn(self, is_primary=True, is_also_secondary=False):
        """
        Maps each the index of each node in the raw distance
        matrix to a tuple
        containing (source_id, distance), where
        source_id is a member of the primary_source
        or secondary_source and distance is the number of meters
        between the (primary/secondary) source and its nearest OSM node.
        """

        if is_primary:
            data = self.primary_data
        else:
            data = self.secondary_data

        nodes = self._network_interface.nodes[['x', 'y']]

        start_time = time.time()

        # make a kd tree in the lat, long dimension
        node_array = nodes.values
        kd_tree = scipy.spatial.cKDTree(node_array)  # pylint: disable=not-callable

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

            # keep track of nodes that are used to snap a user data point
            self._network_interface.user_node_friends.add(node_number)
            edge_distance = distance.distance(origin_location, closest_node_location).m

            edge_weight = int(edge_distance / self._config_interface.default_edge_cost)

            if is_primary:
                # pylint disable=line-too-long
                self.matrix_interface.add_user_source_data(network_id=node_loc,
                                                           user_id=origin_id,
                                                           weight=edge_weight,
                                                           is_also_dest=is_also_secondary)
            else:
                # pylint disable=line-too-long
                self.matrix_interface.add_user_dest_data(network_id=node_loc,
                                                         user_id=origin_id,
                                                         weight=edge_weight)

        time_delta = time.time() - start_time
        self.logger.debug(
            'Nearest Neighbor matching completed in {:,.2f} seconds'.format(time_delta))

    def write_csv(self, outfile=None):
        """
        Write the transit matrix to csv.

        Note: Use write_h5 (as opposed to this method) to
        save the transit matrix unless exporting for external use.

        Arguments:
            outfile-optional string
        """
        if not outfile:
            outfile = self._get_output_filename(self.network_type, extension='csv')
        assert '.csv' in outfile, 'Error: given filename does not have the correct extension (.csv)'
        self.matrix_interface.write_csv(outfile)

    def write_h5(self, outfile=None):
        """
        Write the transit matrix to h5.

        Note: Use this method (as opposed to write_csv) to 
        save the transit matrix unless exporting data for 
        external use.

        Arguments:
            outfile-optional string
        """
        if not outfile:
            outfile = self._get_output_filename(self.network_type, extension='h5')
        assert '.h5' in outfile, 'Error: given filename does not have the correct extension (.h5)'
        self.matrix_interface.write_h5(outfile)

    def prefetch_network(self):
        """
        Fetch and cache the osm network.

        """
        self._load_inputs()

        self._network_interface.load_network(self.primary_data,
                                             self.secondary_data,
                                             self.secondary_input is not None,
                                             self.epsilon)

    def clear_cache(self):
        """
        Clear the network cache.
        """
        self._network_interface.clear_cache()

    def process(self):
        """
        Process the data.
        """
        if self.network_type == 'transit':
            self.logger.error("Don't need to call process for matrix of type transit. Returning...")
            return

        start_time = time.time()

        self.logger.debug("Processing network (%s) with epsilon: %f",
                          self.network_type, self.epsilon)

        self.prefetch_network()

        is_symmetric = self.secondary_input is None and self.network_type is not 'drive'
        rows = len(self.primary_data)

        if self.secondary_input is None:
            cols = rows
        else:
            cols = len(self.secondary_data)
        self.matrix_interface.prepare_matrix(is_symmetric=is_symmetric, rows=rows, columns=cols,
                                             network_vertices=self._network_interface.number_of_nodes())

        if self.secondary_input:
            self._match_nn(is_primary=True, is_also_secondary=False)
            self._match_nn(is_primary=False, is_also_secondary=False)
        else:
            self._match_nn(is_primary=True, is_also_secondary=True)

        self._parse_network()

        # offload primary and secondary input data frames because we don't need them anymore
        self.primary_input = None
        self.secondary_input = None

        self.matrix_interface.build_matrix()
        time_delta = time.time() - start_time

        self.logger.info('All operations completed in {:,.2f} seconds'.format(time_delta))
