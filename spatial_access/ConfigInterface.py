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
        self.HUMAN_WALK_SPEED = 5
        self.WALK_NODE_PENALTY = 0

        self.DEFAULT_DRIVE_SPEED = 40
        self.DRIVE_NODE_PENALTY = 0

        self.BIKE_SPEED = 15.5
        self.BIKE_NODE_PENALTY = 0

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

    
