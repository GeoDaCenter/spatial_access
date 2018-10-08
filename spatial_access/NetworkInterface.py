"""
An interface for a network query to OSM. Caches results and
returns the local resources if available.
"""

import os
import sys
import pandas as pd
from pandana.loaders import osm

class NetworkInterface():
    '''
    Abstracts the connection for querying OSM
    servers for city walking, driving and biking
    networks.
    '''

    def __init__(self, network_type, logger=None):
        self.logger = logger
        self.network_type = network_type
        assert isinstance(network_type, str)
        self.bbox = None
        self.cache_filename = 'osm_query_cache/'
        self._try_create_cache()
        self.nodes = None
        self.edges = None

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


    def _try_create_cache(self):
        '''
        Create the directory for the cache
        if it does not already exist.
        '''
        if not os.path.exists(self.cache_filename):
            os.makedirs(self.cache_filename)

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

        self.bbox = [lat_min, lon_min, lat_max, lon_max]
        if self.logger:
            self.logger.debug('set bbox: {}'.format(self.bbox))

    def get_nodes_filename(self):
        '''
        Return the filename of the node table for the current
        query.
        '''
        bbox_string = '_'.join([str(coord) for coord in self.bbox])
        return self.cache_filename + self.network_type + '_nodes' + bbox_string + '.csv'

    def get_edges_filename(self):
        '''
        Return the filename of the edges table for the current
        query.
        '''
        bbox_string = '_'.join([str(coord) for coord in self.bbox])
        return self.cache_filename + self.network_type + '_edges' + bbox_string + '.csv'

    def _network_exists(self):
        '''
        Return True if both the nodes and edges
        filename for the current query exist
        locally, else False.
        '''
        nodes_exist = os.path.exists(self.get_nodes_filename())
        edges_exist = os.path.exists(self.get_edges_filename())
        return nodes_exist and edges_exist

    def load_network(self, primary_data, secondary_data,
                     secondary_input, epsilon):
        '''
        Attempt to load the nodes and edges tables for
        the current query from the local cache; query OSM
        servers if not.
        Returns: nodes, edges (pandas df's)
        '''
        assert isinstance(primary_data, pd.DataFrame)
        #assert isinstance(secondary_input, (pd.DataFrame, None))
        assert isinstance(secondary_input, bool)
        assert isinstance(epsilon, tup(float, int))

        self._try_create_cache()
        self._get_bbox(primary_data, secondary_data,
                       secondary_input, epsilon)
        if self._network_exists():
            node_filename = self.get_nodes_filename()
            edge_filename = self.get_edges_filename()

            self.nodes = pd.read_csv(node_filename)
            self.edges = pd.read_csv(edge_filename)
            if self.logger:
                self.logger.debug('Read nodes from %s', node_filename)
                self.logger.debug('Read edges from %s', edge_filename)

    def _request_network(self):
        '''
        Fetch a street network from OSM for the
        current query
        '''
        try:
            self.nodes, self.edges = osm.network_from_bbox(
                lat_min=self.bbox[0], lng_min=self.bbox[1],
                lat_max=self.bbox[2], lng_max=self.bbox[3],
                network_type=self.network_type)
            self.nodes.to_csv(self.get_nodes_filename())
            self.edges.to_csv(self.get_edges_filename())

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
