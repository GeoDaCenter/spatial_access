# Logan Noel (github.com/lmnoel)
#
# ©2017-2019, Center for Spatial Data Science

# pylint: skip-file

import os
import time
import pandas as pd
from osmnet.load import network_from_bbox
from geopy import distance

from spatial_access.SpatialAccessExceptions import BoundingBoxTooLargeException
from spatial_access.SpatialAccessExceptions import UnableToConnectException
from spatial_access.SpatialAccessExceptions import SourceNotBuiltException

try:
    import networkAdapterUtility
except ImportError:
    raise SourceNotBuiltException()
#  TODO: move trimming to an extension


class NetworkInterface:
    """
    Abstracts the connection for querying OSM
    servers for city walking, driving and biking
    networks.
    """

    def __init__(self, network_type, logger=None, disable_area_threshold=False):
        self.logger = logger
        self.network_type = network_type
        self.bbox = None
        self.nodes = None
        self.edges = None
        self.user_node_friends = set()
        self._already_merged = set()
        self._nodes_to_merge = set()
        self._rows_to_merge = {}
        self.area_threshold = None if disable_area_threshold else 2000  # km
        assert isinstance(network_type, str)
        self.cache_filename = 'data/osm_query_cache'
        self._try_create_cache()

    def clear_cache(self):
        """
        Remove the contents of the NetworkInterface cache.
        """
        try:
            import shutil
            shutil.rmtree(self.cache_filename)
        except BaseException:
            if self.logger:
                self.logger.error('Unable to remove cache')

    def _approximate_bbox_area(self):
        """
        Calculate the approximate area of the 
        bounding box in square kilometers.
        """
        lower_left_point = (self.bbox[1], self.bbox[0])
        lower_right_point = (self.bbox[3], self.bbox[0])
        upper_left_point = (self.bbox[1], self.bbox[2])
        lower_edge = distance.distance(lower_left_point, lower_right_point).km
        left_edge = distance.distance(lower_left_point, upper_left_point).km
        area = lower_edge * left_edge
        if self.logger:
            self.logger.info('Approx area of bounding box: {:,.2f} sq. km'.format(area))
        return area

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

    def _get_bbox(self, primary_data, secondary_data,
                  secondary_input, epsilon):
        """
        Figure out how to set the upper left and lower right corners
        of the bounding box which
        is used to request a streed/road/path network from OSM,
        including a small correction to account for nodes that might
        lay just beyond the most distant data points.
        """
        if secondary_input:
            composite_lon = list(primary_data['lon']) + \
                list(secondary_data['lon'])
            composite_lat = list(primary_data['lat']) + \
                list(secondary_data['lat'])
        else:
            composite_lon = list(primary_data['lon'])
            composite_lat = list(primary_data['lat'])

        lat_max = max(composite_lon) + epsilon
        lat_min = min(composite_lon) - epsilon

        lon_max = max(composite_lat) + epsilon
        lon_min = min(composite_lat) - epsilon

        self.bbox = [lon_min, lat_min, lon_max, lat_max]
        if self.area_threshold:
            approx_area = self._approximate_bbox_area()
            if approx_area > self.area_threshold:
                if self.logger:
                    self.logger.error('Supplied coordinates span too large an area')
                    self.logger.error('You can set disable_area_threshold to True if this is intentional')
                raise BoundingBoxTooLargeException()
        if self.logger:
            self.logger.debug('set bbox: {}'.format(self.bbox))

    def get_filename(self):
        """
        Return the filename of the node table for the current
        query.
        """
        bbox_string = '_'.join([str(coord) for coord in self.bbox])
        return 'data/osm_query_cache/' + self.network_type + bbox_string + '.h5'

    def _network_exists(self):
        """
        Return True if both the nodes and edges
        filename for the current query exist
        locally, else False.
        """
        return os.path.exists(self.get_filename())

    def _merge_node(self, node_id):
        """
        Merge the given node_id and all nodes
        contiguous that need to be merged.
        """
        pass

    def trim_edges(self):
        """
        Find nodes that are the source of an edge exactly once,
        and the destination of an edge exactly once. Remove
        the nodes and connect the edges if and only if
        said node is not the snapping node of a user
        data point.
        """
        pass

    def load_network(self, primary_data, secondary_data,
                     secondary_input, epsilon):
        """
        Attempt to load the nodes and edges tables for
        the current query from the local cache; query OSM
        servers if not.
        Returns: nodes, edges (pandas df's)
        """
        assert isinstance(primary_data, pd.DataFrame)
        assert isinstance(secondary_data, pd.DataFrame) or secondary_data is None
        assert isinstance(secondary_input, bool)
        assert isinstance(epsilon, float) or isinstance(epsilon, int)

        self._try_create_cache()
        self._get_bbox(primary_data, secondary_data,
                       secondary_input, epsilon)
        if self._network_exists():
            filename = self.get_filename()
            self.nodes = pd.read_hdf(filename, 'nodes')
            self.edges = pd.read_hdf(filename, 'edges')
            if self.logger:
                self.logger.info('Read network from %s', filename)
        else:
            self._request_network()
        self._remove_disconnected_components()

    def _request_network(self):
        """
        Fetch a street network from OSM for the
        current query
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
            filename = self.get_filename()
            self.nodes.to_hdf(filename, 'nodes', complevel=5)
            self.edges.to_hdf(filename, 'edges', complevel=5)
            if self.logger:
                self.logger.info('Queried OSM...')
                self.logger.debug('Cached network to %s', filename)
        except BaseException:
            request_error = """Error trying to download OSM network.
            Did you reverse lat/long?
            Is your network connection functional?
            """
            if self.logger:
                self.logger.error(request_error)
            raise UnableToConnectException()

    def number_of_nodes(self):
        """
        Return the number of nodes in the network.
        """

        assert self.nodes is not None
        return len(self.nodes)

    def number_of_edges(self):
        """
        Return the number of edges in the network.
        """
        assert self.edges is not None
        return len(self.edges)

    def _get_adjacent_vertices(self, v):
        """
        Return a list of vertices with edges from v.
        """
        #return list(self.edges[self.edges['from'] == v])
        return list(self.edges.iloc[self.edges.index.get_level_values(0) == v].to)

    def _get_edges_as_list(self):
        """
        Return a list of all edges as tuples (from, to).
        """
        return list(zip(self.edges['from'], self.edges['to']))

    def _get_vertices_as_list(self):
        """
        Return a list of all node ids.
        """
        return list(self.nodes['id'])

    def _build_transpose_graph(self):
        """
        Build a transpose graph.
        """
        vertices = self._get_vertices_as_list()
        graph = {vertex: [] for vertex in vertices}

        # Recur for all the vertices adjacent to this vertex
        for u, v in self._get_edges_as_list():
            graph[v].append(u)

        return graph

    def _remove_disconnected_vertices(self, nodes_to_remove):
        """
        Given a set nodes_to_remove, remove them from self.nodes
        and self.edges.
        """
        self.nodes = self.nodes[~self.nodes['id'].isin(nodes_to_remove)]
        self.edges = self.edges[~self.edges['from'].isin(nodes_to_remove)]
        self.edges = self.edges[~self.edges['to'].isin(nodes_to_remove)]

    def _remove_disconnected_components(self):
        """
        Remove all nodes and edges that are not
        a part of the largest strongly connected component.
        """
        return
        trimmer_start_time = time.time()
        trimmer = networkAdapterUtility.NetworkUtility(self._get_edges_as_list(), self._get_vertices_as_list())

        self.trimmer_edges = trimmer.getConnectedNetworkEdges()
        self.trimmer_nodes = trimmer.getConnectedNetworkNodes()
        self.logger.info("trimmer in {} seconds".format(time.time() - trimmer_start_time))
        len_edges_before = len(self.edges)
        len_nodes_before = len(self.nodes)
        start_time = time.time()

        first_visit = {vertex: False for vertex in self._get_vertices_as_list()}

        # dummy = {'a':['b'],
        #          'b':['c','f', 'e'],
        #          'c':['d', 'g'],
        #          'd':['c', 'h'],
        #          'e':['a', 'f'],
        #          'f':['g'],
        #          'g':['f'],
        #          'h':['g','d']}
        # Determine order of nodes to visit
        nodes = self._get_vertices_as_list()
        pre_stack = []
        post_stack = []
        while len(post_stack) < len_nodes_before:
            v = nodes.pop()
            if first_visit[v]:
                continue
            pre_stack.append((v, False))
            while len(pre_stack) > 0:
                u, flag = pre_stack.pop()
                if flag:
                    post_stack.append(u)
                elif not first_visit[u]:
                    first_visit[u] = True
                    pre_stack.append((u, True))
                    # pre_stack += [(v, False) for v in dummy[u]]
                    pre_stack += [(v, False) for v in self._get_adjacent_vertices(u)]
        # Create a transpose graph
        transpose_graph = self._build_transpose_graph()

        second_visit = {vertex: False for vertex in self._get_vertices_as_list()}
        connected_components = []

        while len(post_stack) > 0:
            v = post_stack.pop()
            if second_visit[v]:
                continue
            connected_components.append([])
            secondary_stack = [v]
            while len(secondary_stack) > 0:
                u = secondary_stack.pop()
                second_visit[u] = True
                connected_components[-1].append(u)
                for t in transpose_graph[u]:
                    if not second_visit[t]:
                        secondary_stack.append(t)




        connected_components.sort(key=len, reverse=True)

        assert len(connected_components) > 0, 'Did not find a single connected component. Stopping executing.'
        main_component = connected_components[0]
        nodes_to_remove = set(self._get_vertices_as_list()) - set(main_component)

        self._remove_disconnected_vertices(nodes_to_remove)

        if self.logger:
            edges_diff = len_edges_before - len(self.edges)
            nodes_diff = len_nodes_before - len(self.nodes)
            time_diff = time.time() - start_time
            edges_diff_percent = edges_diff / len_edges_before
            nodes_diff_percent = nodes_diff / len_edges_before
            self.logger.info("Removed {}/{} ({:,.2f}%) edges and {}/{} ({:,.2f}%) nodes which were disconnected components in {:,.2f} seconds".format(edges_diff,
                                                                                                                                            len_edges_before,
                                                                                                                                            edges_diff_percent,
                                                                                                                                            nodes_diff,
                                                                                                                                            len_nodes_before,
                                                                                                                                            nodes_diff_percent,
                                                                                                                                            time_diff))

