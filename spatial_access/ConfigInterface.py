# Logan Noel (github.com/lmnoel)
#
# ©2017-2019, Center for Spatial Data Science

# pylint: disable=invalid-name, too-many-instance-attributes
class ConfigInterface():
    """
    A utility class to abstract the network parameter
    configurations.
    """

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

        self.speed_limit_dict = {"urban": 
                                    {"road": 3,
                                     "motorway": 96, 
                                     "motorway_link": 48, 
                                     "motorway_junction": 48, 
                                     "trunk": 80, 
                                     "trunk_link": 40, 
                                     "primary": 48, 
                                     "primary_link": 32, 
                                     "secondary": 40, 
                                     "secondary_link": 40, 
                                     "tertiary": 32, 
                                     "tertiary_link": 32, 
                                     "residential": 24, 
                                     "living_street": 16, 
                                     "service": 16, 
                                     "track": 32, 
                                     "pedestrian": 3.2, 
                                     "services": 3.2, 
                                     "bus_guideway": 3.2, 
                                     "path": 8, 
                                     "cycleway": 16, 
                                     "footway": 3.2, 
                                     "bridleway": 3.2, 
                                     "byway": 3.2, 
                                     "steps": 0.16, 
                                     "unclassified": 24, 
                                     "lane": 16, 
                                     "opposite_lane": 16, 
                                     "opposite": 16, 
                                     "grade1": 16, 
                                     "grade2": 16, 
                                     "grade3": 16, 
                                     "grade4": 16, 
                                     "grade5": 16, 
                                     "roundabout": 40}, 
                                 "rural": 
                                    {"motorway": 112, 
                                     "motorway_link": 48, 
                                     "motorway_junction": 48,
                                     "trunk": 80, 
                                     "trunk_link": 48, 
                                     "primary": 72, 
                                     "primary_link": 32, 
                                     "secondary": 32, 
                                     "secondary_link": 32, 
                                     "tertiary": 48, 
                                     "tertiary_link": 32, 
                                     "residential": 32, 
                                     "living_street": 16, 
                                     "service": 16, 
                                     "track": 32, 
                                     "pedestrian": 3.2, 
                                     "services": 3.2, 
                                     "bus_guideway": 3.2, 
                                     "path": 8, 
                                     "cycleway": 16, 
                                     "footway": 3.2, 
                                     "bridleway": 3.2, 
                                     "byway": 3.2, 
                                     "steps": 0.16, 
                                     "lane": 16, 
                                     "opposite_lane": 16, 
                                     "opposite": 16, 
                                     "grade1": 16, 
                                     "grade2": 16, 
                                     "grade3": 16, 
                                     "grade4": 16, 
                                     "grade5": 16, 
                                     "roundabout": 40, 
                                     "unclassified": 40, 
                                     "road": 32}
                                }


