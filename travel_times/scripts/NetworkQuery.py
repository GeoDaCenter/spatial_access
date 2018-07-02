import requests, logging
import pandas as pd
from geopy.distance import vincenty


class Query(object):
    '''
    Manages requesting network data from OSM
    for walk, drive and bicycle network types.
    '''

    def __init__(self, bbox, network_type):

        self.bbox = bbox
        self.network_type = network_type
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.nodes = None
        self.edges = None


    def request(self):
        '''
        Send a GET to the overpass API with the network
        type and bounding box, and populate the nodes and
        edges members of the Query with data
        '''

        #Choose request parameters based on network type
        if self.network_type == 'drive':
            data = '[maxsize:2000000000][out:json][timeout:900];(way["highway"]["highway"!~"cycleway|footway|path|pedestrian|steps|track|proposed|construction|bridleway|abandoned|platform|raceway|service"]["motor_vehicle"!~"no"]["motorcar"!~"no"]["service"!~"parking|parking_aisle|driveway|emergency_access"]({},{},{},{});>;);out;'.format(self.bbox[0], self.bbox[1], self.bbox[2], self.bbox[3])
        elif self.network_type == 'walk':
            data = '[maxsize:2000000000][out:json][timeout:900];(way["highway"]["highway"!~"motor|proposed|construction|abandoned|platform|raceway"]["foot"!~"no"]["pedestrians"!~"no"]({},{},{},{});>;);out;'.format(self.bbox[0], self.bbox[1], self.bbox[2], self.bbox[3])
        elif self.network_type == 'bicycle' or self.network_type == 'bike':
            data = '[maxsize:2000000000][out:json][timeout:900];(way["highway"]["highway"!~"motor|proposed|construction|abandoned|platform|raceway"]["bicycle"!~"no"]({},{},{},{});>;);out;'.format(self.bbox[0], self.bbox[1], self.bbox[2], self.bbox[3])
        else:
            self.logger.error('unrecognized network_type: {}'.format(self.network_type))

        self.logger.info('GET {}'.format(data))
        #catch errors caused by network connectivity
        try:
            r = requests.get('http://www.overpass-api.de/api/interpreter', 
            {'data': data})
        except:
            self.logger.error('Unable to establish connection with http://www.overpass-api.de/api/interpreter. Please check your internet connection')
            return

        #parse way and node elements of response
        edges = []
        nodes = []
        self.r = r
        for entry in r.json()['elements']:
            if entry['type'] == 'node':
                nodes.append(entry)
            elif entry['type'] == 'way':
                edges.append(entry)
            else:
                self.logger.warning('recieved unrecognized entry type:{}'.format(entry['type']))

        #sanity check to make sure we got some data back
        assert len(edges) > 0, 'Error, query returned no edges'
        assert len(nodes) > 0, 'Error, query returned no nodes'
        
        self.logger.info('Downloaded {} ways and {} nodes from http://www.overpass-api.de/api/interpreter'.format(len(edges), len(nodes)))
        self.nodes = pd.DataFrame(nodes)
        self.nodes.set_index('id', inplace=True)


        #A way is an ordered list of nodes describing a route
        #Therefore, the n to the n + 1 node described by each 
        #way can be separated into an independent edge
        #(each way contains num_nodes - 1 edges)
        KM_TO_METERS = 1000
        edge_results = {}
        for entry in edges:
            way_id = entry['id']
            num_nodes = len(entry['nodes'])
            if 'oneway' in entry['tags'].keys():
                oneway = entry['tags']['oneway']
            else:
                oneway = 'no'
            if 'name' in entry['tags'].keys():
                name = entry['tags']['name']
            else:
                name = None


            for i, node_id in enumerate(entry['nodes']):
                if i < num_nodes - 1:
                    source_node_lat = self.nodes.loc[node_id, 'lat']
                    source_node_lon = self.nodes.loc[node_id, 'lon']

                    dest_node_id = entry['nodes'][i + 1]

                    dest_node_lat = self.nodes.loc[dest_node_id, 'lat']
                    dest_node_lon = self.nodes.loc[dest_node_id, 'lon']
                    distance = vincenty((source_node_lat, source_node_lon), 
                        (dest_node_lat, dest_node_lon)).km
                    distance = int(distance * KM_TO_METERS)
                    edge_results[(node_id, dest_node_id)] = {'distance':distance, 
                    'from': node_id, 'to': dest_node_id, 'name': name,
                    'oneway': oneway}

        self.nodes = self.nodes[['lat', 'lon']]
        self.nodes.rename(columns={'lat':'x', 'lon':'y'}, inplace=True)
        self.edges = pd.DataFrame.from_dict(edge_results, orient='index')

