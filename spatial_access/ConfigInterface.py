"""
Abstracts the network parameter configurations.
"""

import json

# pylint: disable=invalid-name, too-many-instance-attributes
class ConfigInterface():
    '''
    A utility class to abstract the network parameter
    configurations.
    '''
    filename = 'spatial_access/p2p_parameters.json'
    def __init__(self, network_type, logger=None):
        self.network_type = network_type
        self.logger = logger
        self.ONE_HOUR = 3600 # seconds
        self.ONE_KM = 1000 # meters
        self.default_edge_cost = None
        self.load_from_file()


    def load_from_file(self):
        '''
        Load model parameters from json.
        '''

        try:
            with open(ConfigInterface.filename) as json_data:

                params = json.load(json_data)
                self.HUMAN_WALK_SPEED = params['walk']['default_speed']

                self.WALK_NODE_PENALTY = params['walk']['node_penalty']

                self.DEFAULT_DRIVE_SPEED = params['drive']['default_speed']
                self.DRIVE_NODE_PENALTY = params['drive']['node_penalty']

                self.BIKE_SPEED = params['bike']['default_speed']
                self.BIKE_NODE_PENALTY = params['bike']['node_penalty']

                self.WALK_CONSTANT = (
                    self.HUMAN_WALK_SPEED / self.ONE_HOUR) * self.ONE_KM # meters/ second
                self.BIKE_CONSTANT = (
                    self.BIKE_SPEED / self.ONE_HOUR) * self.ONE_KM # meters/ second
                self.DRIVE_CONSTANT = (
                    self.DEFAULT_DRIVE_SPEED / self.ONE_HOUR) * self.ONE_KM # meters/ second
            if self.network_type == 'walk':
                self.default_edge_cost = self.WALK_CONSTANT
            elif self.network_type == 'drive':
                self.default_edge_cost = self.DRIVE_CONSTANT
            elif self.network_type == 'bike':
                self.default_edge_cost = self.BIKE_CONSTANT
            else:
                self.logger.error("Invalid network type")
                raise EnvironmentError("Invalid network type")
            if self.logger:
                self.logger.debug('Set default_edge_cost: {}'.format(self.default_edge_cost))
        except FileNotFoundError as error:
            if self.logger:
                self.logger.error(error)
            raise EnvironmentError(
                "Config file: {} could not be found".format(ConfigInterface.filename))
