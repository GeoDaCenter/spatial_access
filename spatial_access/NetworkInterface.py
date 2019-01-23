"""
An interface for a network query to OSM. Caches results and
returns the local resources if available.
"""
# pylint: skip-file

import os
import sys
import pandas as pd
import numpy as np
import time
from pandana.loaders import osm
from geopy import distance

class NetworkInterface():
    '''
    Abstracts the connection for querying OSM
    servers for city walking, driving and biking
    networks.
    '''

    def __init__(self, network_type, logger=None, disable_area_threshold=False):
        self.logger = logger
        self.network_type = network_type
        self.bbox = None
        self.nodes = None
        self.edges = None
        self.user_node_friends = set()
        self.edges_to_drop = set()
        self.area_threshold = None if disable_area_threshold else 2000 #km
        assert isinstance(network_type, str)
        self._try_create_cache()

    def clear_cache(self):
        '''
        Remove the contents of the NetworkInterface cache.
        '''
        try:
            import shutil
            shutil.rmtree(self.cache_filename)
        except BaseException:
            if self.logger:
                self.logger.error('Unable to remove cache')

    def _approximate_bbox_area(self):
        '''
        Calculate the approximate area of the 
        bounding box in square kilometers.
        '''
        lower_left_point = (self.bbox[1], self.bbox[0])
        lower_right_point = (self.bbox[3], self.bbox[0])
        upper_left_point = (self.bbox[1], self.bbox[2])
        lower_edge = distance.distance(lower_left_point, lower_right_point).km
        left_edge = distance.distance(lower_left_point, upper_left_point).km
        area = lower_edge * left_edge
        if self.logger:
            self.logger.info('Approx area of bounding box: {:,.2f} sq. km'.format(area))
        return area

    def _try_create_cache(self):
        '''
        Create the directory for the cache
        if it does not already exist.
        '''
        if not os.path.exists('data/'):
            os.makedirs('data/')
        if not os.path.exists('data/osm_query_cache'):
            os.makedirs('data/osm_query_cache')

    def _get_bbox(self, primary_data, secondary_data,
                  secondary_input, epsilon):
        '''
        Figure out how to set the upper left and lower right corners
        of the bounding box which
        is used to request a streed/road/path network from OSM,
        including a small correction to account for nodes that might
        lay just beyond the most distant data points.
        '''
        if secondary_input:
            composite_x = list(primary_data.x) + \
                list(secondary_data.x)
            composite_y = list(primary_data.y) + \
                list(secondary_data.y)
        else:
            composite_x = list(primary_data.x)
            composite_y = list(primary_data.y)

        lat_max = max(composite_x) + epsilon
        lat_min = min(composite_x) - epsilon

        lon_max = max(composite_y) + epsilon
        lon_min = min(composite_y) - epsilon

        self.bbox = [lon_min, lat_min, lon_max, lat_max]
        if self.area_threshold:
            approx_area = self._approximate_bbox_area()
            if approx_area > self.area_threshold:
                if self.logger:
                    self.logger.error('Supplied coordinates span too large an area')
                    self.logger.error('You can set disable_area_threshold to True if this is intentional')
                raise Exception('Bounding box contains too large an area')
        if self.logger:
            self.logger.debug('set bbox: {}'.format(self.bbox))

    def get_filename(self):
        '''
        Return the filename of the node table for the current
        query.
        '''
        bbox_string = '_'.join([str(coord) for coord in self.bbox])
        return 'data/osm_query_cache/' + self.network_type + bbox_string + '.h5'


    def _network_exists(self):
        '''
        Return True if both the nodes and edges
        filename for the current query exist
        locally, else False.
        '''
        return os.path.exists(self.get_filename())

    def _erase_node(self, node_id):
        '''
        Assumes node is the source of a single edge
        and the destination of a single edge.

        Merges those edges and deletes the node.
        '''

        #the edge that the node originated
        from_edge = self.edges[self.edges['from'] == node_id]
        assert len(from_edge) == 1, 'node_id: {}, from_edge: {}'.format(node_id, from_edge)

        #the edge that the node terminated
        to_edge = self.edges[self.edges['to'] == node_id]
        assert len(to_edge) == 1, 'node_id: {}, to_edge: {}'.format(node_id, to_edge)


        self.edges_to_drop.add((from_edge['from'], from_edge['to']))
        self.edges_to_drop.add((to_edge['from'], to_edge['to']))

        row_to_add = {key: np.NaN for key in self.edges.columns}
        row_to_add['from'] = to_edge['from']
        row_to_add['to'] = from_edge['to']
        row_to_add['distance'] = from_edge['distance'] + to_edge['distance']

        #grab the highway and name parameters from the "from" edge
        row_to_add['highway'] = from_edge['highway']
        row_to_add['name'] = from_edge['name']

        new_edge_id = (row_to_add['from'], row_to_add['to'])
        row_to_add['Name'] = new_edge_id

        return row_to_add


    def _trim_edges(self):
        '''
        Find nodes that are the source of an edge exactly once,
        and the destination of an edge exactly once. Remove
        the nodes and connect the edges if and only if
        said node is not the snapping node of a user
        data point.
        '''
        start_time = time.time()
        assert isinstance(self.edges, pd.DataFrame)
        assert isinstance(self.nodes, pd.DataFrame)
        len_nodes = len(self.nodes)
        len_edges = len(self.edges)
        from_value_counts = self.edges['from'].value_counts()
        to_value_counts = self.edges['to'].value_counts()
        count_of_dropped_nodes = 0
        rows_to_add = []
        for node_id in self.nodes.index:
            if node_id in from_value_counts.index and node_id in to_value_counts.index:
                if from_value_counts[node_id] == 1 and to_value_counts[node_id] == 1:
                    if node_id not in self.user_node_friends:
                        rows_to_add.append(self._erase_node(node_id))
                        count_of_dropped_nodes += 1
        self.edges.drop(list(self.edges_to_drop))
        df_to_add = pd.DataFrame(rows_to_add)
        self.edges = pd.concat([self.edges, df_to_add], sort=False)
        assert len(self.nodes) == len_nodes - count_of_dropped_nodes
        assert len(self.edges) == len_edges - count_of_dropped_nodes

        if self.logger:
            self.logger.info('Trimmed {} nodes in {:,.2f} seconds'.format(count_of_dropped_nodes, time.time() - start_time))
    
    def load_network(self, primary_data, secondary_data,
                     secondary_input, epsilon):
        '''
        Attempt to load the nodes and edges tables for
        the current query from the local cache; query OSM
        servers if not.
        Returns: nodes, edges (pandas df's)
        '''
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
                self.logger.debug('Read network from %s', filename)
        else:
            self._request_network()

    def _request_network(self):
        '''
        Fetch a street network from OSM for the
        current query
        '''
        try:
            if self.network_type == 'bike':
                osm_bike_filter = '["highway"!~"motor|proposed|construction|abandoned|platform|raceway"]["foot"!~"no"]["bicycle"!~"no"]'
                self.nodes, self.edges = osm.network_from_bbox(
                lat_min=self.bbox[0], lng_min=self.bbox[1],
                lat_max=self.bbox[2], lng_max=self.bbox[3],
                custom_osm_filter=osm_bike_filter)
            else:
                self.nodes, self.edges = osm.network_from_bbox(
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
            request_error = '''Error trying to download OSM network.
            Did you reverse lat/long?
            Is your network connection functional?
            '''
            if self.logger:
                self.logger.error(request_error)
            sys.exit()

    def number_of_nodes(self):
        '''
        Return the number of nodes in the network.
        '''

        assert self.nodes is not None
        return len(self.nodes)

    def number_of_edges(self):
        '''
        Return the number of edges in the network.
        '''
        assert self.edges is not None
        return len(self.edges)
