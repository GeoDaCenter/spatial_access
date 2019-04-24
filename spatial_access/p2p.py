# Logan Noel (github.com/lmnoel)
#
# ©2017-2019, Center for Spatial Data Science


import time
import logging
import os
import scipy.spatial
from geopy import distance
import pandas as pd

from spatial_access.MatrixInterface import MatrixInterface
from spatial_access.NetworkInterface import NetworkInterface
from spatial_access.Configs import Configs

from spatial_access.SpatialAccessExceptions import PrimaryDataNotFoundException
from spatial_access.SpatialAccessExceptions import SecondaryDataNotFoundException
from spatial_access.SpatialAccessExceptions import UnableToParsePrimaryDataException
from spatial_access.SpatialAccessExceptions import UnableToParseSecondaryDataException
from spatial_access.SpatialAccessExceptions import UnknownModeException
from spatial_access.SpatialAccessExceptions import InsufficientDataException
from spatial_access.SpatialAccessExceptions import DuplicateInputException
from spatial_access.SpatialAccessExceptions import WriteTMXFailedException
from spatial_access.SpatialAccessExceptions import WriteCSVFailedException


class TransitMatrix:
    """
    Compute transit matrices at scale.
    """
    def __init__(
            self,
            network_type,
            primary_input=None,
            secondary_input=None,
            read_from_file=None,
            use_meters=False,
            primary_hints=None,
            secondary_hints=None,
            disable_area_threshold=False,
            walk_speed=None,
            bike_speed=None,
            epsilon=0.05,
            debug=False,
            configs=None):
        """
        Args:
            network_type: string, one of {'walk', 'bike', 'drive', 'otp'}.
            primary_input: string, csv filename.
            secondary_input: string, csv filename (omit to calculate an NxN matrix on
                the primary_input).
            read_from_file: string, tmx or csv filename.
            use_meters: output will be in meters, not seconds.
            primary_hints: dictionary, map column names to expected values.
            secondary_hints: dictionary, map column names to expected values.
            disable_area_threshold: boolean, enable if computation fails due to
                exceeding bounding box area constraint.
            walk_speed: numeric, override default walking speed (km/hr).
            bike_speed: numeric, override default walking speed (km/hr).
            epsilon: numeric, factor by which to increase the requested bounding box.
                Increasing epsilon may result in increased accuracy for points
                at the edge of the bounding box, but will increase computation times.
            debug: boolean, enable to see more detailed logging output.
            configs: defaults to None, else pass in an instance of Configs to override
                default values.

        Raises:
            UnknownModeException: If the network type is unknown.
            DuplicateInputException: If the same file is given as primary_input
                and secondary_input. To compute symmetric matrices (NxN), leave the
                secondary input field blank.
            InsufficientDataException: If neither a source data file (csv) nor a
                transit matrix file (tmx) is supplied.

        """

        # arguments
        self.network_type = network_type
        self.epsilon = epsilon
        self.primary_input = primary_input
        self.secondary_input = secondary_input
        self.primary_hints = primary_hints
        self.secondary_hints = secondary_hints
        self.use_meters = use_meters

        # member variables
        self.primary_data = None
        self.secondary_data = None

        # start the logger
        self.logger = None
        self.set_logging(debug)

        # instantiate interfaces
        if isinstance(configs, Configs):
            self.logger.debug("set custom config")
            self.configs = configs
        else:
            self.configs = Configs()

        self._network_interface = NetworkInterface(network_type, logger=self.logger,
                                                   disable_area_threshold=disable_area_threshold)

        self.matrix_interface = MatrixInterface(logger=self.logger)

        if walk_speed is not None:
            self.configs.walk_speed = walk_speed
        if bike_speed is not None:
            self.configs.bike_speed = bike_speed

        if network_type not in {'drive', 'walk', 'bike', 'otp'}:
            raise UnknownModeException(network_type)

        if self.primary_input == self.secondary_input and self.primary_input is not None:
            raise DuplicateInputException("Gave duplicate inputs: {}".format(self.primary_input))

        # need to supply either:
        if primary_input is None and read_from_file is None:
            raise InsufficientDataException()

        if read_from_file:
            self.matrix_interface.read_file(read_from_file)
        if network_type == 'otp':
            self.matrix_interface.read_otp(primary_input)

    def set_logging(self, debug):
        """
        Set the logging level.

        Args:
            debug: enable for increased details
                in logs.
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
        Args:
            keyword: the file's keyword.
            extension: the files's type.

        Returns: unique filename.
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

    def _parse_csv(self, primary):
        """
        Load source data from .csv. Identify lon, lon and id columns.

        Args:
            primary: boolean, true if loading primary data.
        Raises:
            UnableToParsePrimaryDataException: The user's supplied
                mapping to column names failed.
            UnableToParseSecondaryDataException: The user's supplied
                mapping to column names failed.
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

        keyword = "rows" if primary else "columns"
        self.logger.debug(
            'Total number of {} in the dataset: {}'.format(keyword, pre_drop))
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
        transit matrix, or two for an asymmetric matrix.

        Raises:
            PrimaryDataNotFoundException: Primary data isn't found.
            SecondaryDataNotFoundException: Secondary data isn't found.
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
        except KeyError:
            raise UnableToParsePrimaryDataException()

        if self.secondary_input:
            try:
                self._parse_csv(False)
            except KeyError:
                raise UnableToParseSecondaryDataException()

    def _reduce_node_indeces(self):
        """
        Map the network indeces to location.
        Returns:
            dictionary of {node index : node location}
        """
        simple_node_indeces = {}
        for position, id_ in enumerate(self._network_interface.nodes['id']):
            simple_node_indeces[id_] = position
        return simple_node_indeces

    def _parse_network(self):
        """
        Cleans and generates the city network.
        """

        start_time = time.time()

        edges = self._network_interface.edges

        if self.use_meters:
            edges['edge_weight'] = edges['distance']
        elif self.network_type == 'walk':
            edges['edge_weight'] = edges['distance'] / self.configs._get_walk_speed() \
                                        + self.configs.walk_node_penalty
        elif self.network_type == 'bike':
            edges['edge_weight'] = edges['distance'] / self.configs._get_bike_speed() \
                                        + self.configs.bike_node_penalty
        elif self.network_type == 'drive':
            driving_cost_matrix = self.configs._get_driving_cost_matrix()
            edges = pd.merge(edges, driving_cost_matrix, how='left', left_on='highway', right_index=True)
            edges['unit_cost'].fillna(self.configs._get_default_drive_speed(), inplace=True)
            edges['edge_weight'] = edges['distance'] / edges['unit_cost'] + self.configs.drive_node_penalty

        if self.network_type == 'walk' or self.network_type == 'bike':
            edges['is_bidirectional'] = True
        elif self.network_type == 'drive':
            edges['is_bidirectional'] = edges['oneway'] != "yes"

        simple_node_indeces = self._reduce_node_indeces()

        edges['from_loc'] = edges['from'].map(simple_node_indeces)
        edges['to_loc'] = edges['to'].map(simple_node_indeces)
        edges['edge_weight'] = edges['edge_weight'].astype('int16')

        from_column = list(edges['from_loc'])
        to_column = list(edges['to_loc'])
        edge_weight_column = list(edges['edge_weight'])
        is_bidirectional_column = list(edges['is_bidirectional'])

        self.matrix_interface.add_edges_to_graph(from_column, to_column, edge_weight_column,
                                                 is_bidirectional_column)

        time_delta = time.time() - start_time
        self.logger.debug("Prepared raw network in {:,.2f} seconds".format(time_delta))

    def _match_to_nearest_neighbor(self, is_primary=True, is_also_secondary=False):
        """
        Map each vertex in the user's data set to a vertex in
        the underlying osm network.

        Args:
            is_primary: true if this is the primary dataset.
            is_also_secondary: true if this is also acting as the secondary dataset.
        """

        if is_primary:
            data = self.primary_data
        else:
            data = self.secondary_data

        nodes = self._network_interface.nodes[['x', 'y']]

        start_time = time.time()

        # make a kd tree in the lat, long dimension
        node_array = nodes.values
        kd_tree = scipy.spatial.cKDTree(node_array)

        unit_cost = 1
        if self.use_meters:
            unit_cost = 1
        elif self.network_type == 'drive':
            unit_cost = self.configs._get_default_drive_speed()
        elif self.network_type == 'walk':
            unit_cost = self.configs._get_walk_speed()
        elif self.network_type == 'bike':
            unit_cost = self.configs._get_bike_speed()
        else:
            assert False, "Unknown type"

        # map each node in the source/dest data to the nearest
        # corresponding node in the OSM network
        # and write to file
        for row in data.itertuples():
            origin_id, origin_x, origin_y = row
            latlong_diff, node_loc = kd_tree.query([origin_x, origin_y], k=1)
            node_number = nodes.index[node_loc]
            origin_location = (origin_y, origin_x)
            closest_node_location = (nodes.loc[node_number].y,
                                                       nodes.loc[node_number].x)

            # keep track of nodes that are used to snap a user data point
            edge_distance = distance.distance(origin_location, closest_node_location).m

            edge_weight = int(edge_distance / unit_cost)

            if is_primary:
                self.matrix_interface.add_user_source_data(network_id=node_loc,
                                                           user_id=origin_id,
                                                           weight=edge_weight,
                                                           is_also_dest=is_also_secondary)
            else:
                self.matrix_interface.add_user_dest_data(network_id=node_loc,
                                                         user_id=origin_id,
                                                         weight=edge_weight)

        time_delta = time.time() - start_time
        self.logger.debug(
            'Nearest Neighbor matching completed in {:,.2f} seconds'.format(time_delta))

    def write_csv(self, outfile=None):
        """
        Write the transit matrix to csv.

        Note: Use write_tmx (as opposed to this method) to
        save the transit matrix unless exporting for external use.

        Arguments:
            outfile: optional filename.
        Raises:
            WriteCSVFailedException: filename does not have correct extension.
        """
        if not outfile:
            outfile = self._get_output_filename(self.network_type, extension='csv')
        if '.csv' not in outfile:
            raise WriteCSVFailedException('given filename does not have the correct extension (.csv)')
        self.matrix_interface.write_csv(outfile)

    def write_tmx(self, outfile=None):
        """
        Write the transit matrix to tmx.

        Note: Use this method (as opposed to write_csv) to
        save the transit matrix unless exporting data for
        external use.

        Arguments:
            outfile: optional filename.
        Raises:
            WriteTMXFailedException: filename does not have correct extension.
        """
        if not outfile:
            outfile = self._get_output_filename(self.network_type, extension='tmx')
        if '.tmx' not in outfile:
            raise WriteTMXFailedException('given filename does not have the correct extension (.tmx)')
        self.matrix_interface.write_tmx(outfile)

    def prefetch_network(self):
        """
        Fetch and cache the osm network.
        """
        self._load_inputs()

        self._network_interface.load_network(self.primary_data,
                                             self.secondary_data,
                                             self.secondary_input is not None,
                                             self.epsilon)

    @staticmethod
    def clear_cache():
        """
        Clear the network cache.
        """
        NetworkInterface.clear_cache()

    def _is_compressible(self):
        """
        Returns: true if the transit matrix can be compressed by
            half without losing any data.
        """
        return self._is_symmetric() and self.network_type in {'walk', 'bike'}

    def _is_symmetric(self):
        """
        Returns: true if the transit matrix is NxN, that is, has
            the same origins and destinations.
        """
        return self.secondary_input is None

    def process(self):
        """
        - Load the users's data.
        - Fetch the osm network.
        - Parse the network.
        - Calculate transit matrix.

        Raises:
            AssertionError: if this method is called on an OTP-matrix.
        """
        assert self.network_type != 'otp', 'no need to call process for an otp matrix'
        start_time = time.time()

        self.logger.debug("Processing network (%s) with epsilon: %f",
            self.network_type, self.epsilon)

        self.prefetch_network()

        rows = len(self.primary_data)

        if self.secondary_input is None:
            cols = rows
            self.matrix_interface.secondary_ids_are_string = self.matrix_interface.primary_ids_are_string
        else:
            cols = len(self.secondary_data)
        self.matrix_interface.prepare_matrix(is_symmetric=self._is_symmetric(),
                                             is_compressible=self._is_compressible(),
                                             rows=rows,
                                             columns=cols,
                                             network_vertices=self._network_interface.number_of_nodes())

        if self.secondary_input:
            self._match_to_nearest_neighbor(is_primary=True, is_also_secondary=False)
            self._match_to_nearest_neighbor(is_primary=False, is_also_secondary=False)
        else:
            self._match_to_nearest_neighbor(is_primary=True, is_also_secondary=True)

        self._parse_network()

        # offload primary and secondary input data frames because we don't need them anymore
        self.primary_input = None
        self.secondary_input = None

        self.matrix_interface.build_matrix()
        time_delta = time.time() - start_time

        self.logger.info('All operations completed in {:,.2f} seconds'.format(time_delta))
