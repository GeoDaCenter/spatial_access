# Logan Noel (github.com/lmnoel)
#
# ©2017-2019, Center for Spatial Data Science

import os
import time
import pandas as pd
from osmnet.load import network_from_bbox
from geopy import distance

from spatial_access.SpatialAccessExceptions import BoundingBoxTooLargeException
from spatial_access.SpatialAccessExceptions import UnableToConnectException
from spatial_access.SpatialAccessExceptions import SourceNotBuiltException
from spatial_access.SpatialAccessExceptions import ConnectedComponentTrimmingFailed

import logging
logging.getLogger('osmnet').disabled = True

try:
    import _p2pExtension
except ImportError:
    raise SourceNotBuiltException()


class NetworkInterface:
    """
    Manages OSM network retrieval for p2p.TransitMatrix.
    """

    def __init__(self, network_type, logger=None, disable_area_threshold=False):
        """

        Args:
            network_type: string, network type
            logger: optional, logger.
            disable_area_threshold: boolean, enable if computation fails due to
            exceeding bounding box area constraint.
        """
        self.logger = logger
        self.network_type = network_type
        self.bbox = None
        self.nodes = None
        self.edges = None
        self.area_threshold = None if disable_area_threshold else 2000  # km
        assert isinstance(network_type, str)
        self._try_create_cache()

    @staticmethod
    def clear_cache():
        """
        Remove the contents of the NetworkInterface cache.
        """
        import shutil
        if os.path.exists('data/osm_query_cache'):
            shutil.rmtree('data/osm_query_cache')

    @staticmethod
    def _try_create_cache():
        """
        Create the directory for the cache
        if it does not already exist.
        """
        if not os.path.exists('data/'):
            os.makedirs('data/')
        if not os.path.exists('data/osm_query_cache'):
            os.makedirs('data/osm_query_cache')

    def number_of_nodes(self):
        """
        Returns: number of nodes in graph.
        """
        return len(self.nodes)

    def number_of_edges(self):
        """
        Returns: number of edges in graph.
        """
        return len(self.edges)

    def _approximate_bbox_area(self):
        """
        Calculate the approximate area of the 
        bounding box in square kilometers.
        Returns: numeric area of the bounding box
            in km squared.
        """
        lat_min, lon_min, lat_max, lon_max = self.bbox
        lower_right_point = (lat_min, lon_max)
        lower_left_point = (lat_min, lon_min)
        upper_left_point = (lat_max, lon_min)
        lower_edge = distance.distance(lower_left_point, lower_right_point).km
        left_edge = distance.distance(lower_left_point, upper_left_point).km
        area = lower_edge * left_edge
        if self.logger:
            self.logger.info('Approx area of bounding box: {:,.2f} sq. km'.format(area))
        return area

    def _get_bbox(self, primary_data, secondary_data,
                  secondary_input, epsilon):
        """
        Determine bounding box for given data.

        Args:
            primary_data: DataFrame of primary points.
            secondary_data: DataFrame of secondary points.
            secondary_input: boolean, true if secondary_data
                was provided.
            epsilon: Safety margin around bounding box.

        Raises:
            BoundingBoxTooLargeException: if area is larger than
                self.area_threshold.

        """
        if secondary_input:
            composite_lon = list(primary_data['lon']) + \
                list(secondary_data['lon'])
            composite_lat = list(primary_data['lat']) + \
                list(secondary_data['lat'])
        else:
            composite_lon = list(primary_data['lon'])
            composite_lat = list(primary_data['lat'])

        lat_max = max(composite_lat) + epsilon
        lat_min = min(composite_lat) - epsilon

        lon_max = max(composite_lon) + epsilon
        lon_min = min(composite_lon) - epsilon

        self.bbox = [lat_min, lon_min, lat_max, lon_max]
        if self.area_threshold:
            approx_area = self._approximate_bbox_area()
            if approx_area > self.area_threshold:
                if self.logger:
                    self.logger.error('Supplied coordinates span too large an area')
                    self.logger.error('You can set disable_area_threshold to True if this is intentional')
                raise BoundingBoxTooLargeException(str(approx_area) + "km square")

    def _get_filename(self):
        """
        Returns: cache filename formatted for this request.
        """
        bbox_string = '_'.join([str(coord) for coord in self.bbox])
        return 'data/osm_query_cache/' + self.network_type + bbox_string + '.h5'

    def _network_exists(self):
        """
        Returns: true if a filename matching these
            network parameters is in the cache.
        """
        return os.path.exists(self._get_filename())

    def load_network(self, primary_data, secondary_data,
                     secondary_input, epsilon):
        """
        Attempt to load the nodes and edges tables for
        the current query from the local cache; query OSM
        servers if not.

        Args:
            primary_data: DataFrame of primary points.
            secondary_data: DataFrame of secondary points.
            secondary_input: boolean, true if secondary_data
                was provided.
            epsilon: Safety margin around bounding box.

        Raises:
            AssertionError: argument is not of expected type

        """
        assert isinstance(primary_data, pd.DataFrame)
        assert isinstance(secondary_data, pd.DataFrame) or secondary_data is None
        assert isinstance(secondary_input, bool)
        assert isinstance(epsilon, float) or isinstance(epsilon, int)

        self._try_create_cache()
        self._get_bbox(primary_data, secondary_data,
                       secondary_input, epsilon)
        if self._network_exists():
            filename = self._get_filename()
            self.nodes = pd.read_hdf(filename, 'nodes')
            self.edges = pd.read_hdf(filename, 'edges')
            if self.logger:
                self.logger.debug('Read network from cache: %s', filename)
        else:
            self._request_network()
        self._remove_disconnected_components()

    def _request_network(self):
        """
        Fetch a street network from OSM for the
        current query.
        Raises:
            UnableToConnectException: network connection is unavailable.
        """
        try:
            if self.network_type == 'bike':
                osm_bike_filter = '["highway"!~"motor|proposed|construction|abandoned|platform|raceway"]["foot"!~"no"]["bicycle"!~"no"]'
                self.nodes, self.edges = network_from_bbox(lat_min=self.bbox[0], lng_min=self.bbox[1],
                                                               lat_max=self.bbox[2], lng_max=self.bbox[3],
                                                               custom_osm_filter=osm_bike_filter)
            else:
                self.nodes, self.edges = network_from_bbox(
                    lat_min=self.bbox[0], lng_min=self.bbox[1],
                    lat_max=self.bbox[2], lng_max=self.bbox[3],
                    network_type=self.network_type)
                if self.network_type == 'drive':
                    self.edges.drop(['access', 'hgv', 'lanes', 'maxspeed', 'tunnel'], inplace=True, axis=1)
                else:
                    self.edges.drop(['access', 'bridge', 'lanes', 'service', 'tunnel'], inplace=True, axis=1)
            filename = self._get_filename()
            self.nodes.to_hdf(filename, 'nodes', complevel=5)
            self.edges.to_hdf(filename, 'edges', complevel=5)
            if self.logger:
                self.logger.info('Finished querying osm')
                self.logger.debug('Cached network to %s', filename)
        except BaseException:
            request_error = """Error trying to download OSM network.
            Did you reverse lat/long?
            Is your network connection functional?
            """
            if self.logger:
                self.logger.error(request_error)
            raise UnableToConnectException()

    def _get_edges_as_list(self):
        """
        Returns: a list of all edges as tuples (from, to).
        """
        return list(zip(self.edges['from'], self.edges['to']))

    def _get_vertices_as_list(self):
        """
        Returns: a list of all node ids.
        """
        return list(self.nodes['id'])

    def _apply_connected_nodes(self, nodes_to_keep):
        """
        Given a set nodes_to_keep, remove all other
        nodes and edges.
        Args:
            nodes_to_keep: array of node indeces.
        """
        self.nodes = self.nodes[self.nodes['id'].isin(nodes_to_keep)]
        self.edges = self.edges[self.edges['from'].isin(nodes_to_keep) & self.edges['to'].isin(nodes_to_keep)]

    def _remove_disconnected_components(self):
        """
        Remove all nodes and edges that are not
        a part of the largest strongly connected component.
        Raises:
            ConnectedComponentTrimmingFailed: caused by undefined behavior from extension.
        """
        len_edges_before = len(self.edges)
        len_nodes_before = len(self.nodes)
        start_time = time.time()
        try:
            trimmer = _p2pExtension.pyNetworkUtility(self._get_edges_as_list(), self._get_vertices_as_list())
            nodes_of_main_connected_component = trimmer.getConnectedNetworkNodes()
        except BaseException:
            raise ConnectedComponentTrimmingFailed()

        self._apply_connected_nodes(nodes_of_main_connected_component)

        if self.logger:
            edges_diff = len_edges_before - len(self.edges)
            nodes_diff = len_nodes_before - len(self.nodes)
            time_diff = time.time() - start_time
            edges_diff_percent = edges_diff / len_edges_before
            nodes_diff_percent = nodes_diff / len_edges_before
            self.logger.debug("Removed {}/{} ({:,.2f}%) edges and {}/{} ({:,.2f}%) nodes which were disconnected components in {:,.2f} seconds".format(edges_diff,
                                                                                                                                            len_edges_before,
                                                                                                                                            edges_diff_percent,
                                                                                                                                            nodes_diff,
                                                                                                                                            len_nodes_before,
                                                                                                                                            nodes_diff_percent,
                                                                                                                                            time_diff))

