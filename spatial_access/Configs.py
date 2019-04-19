# Logan Noel (github.com/lmnoel)
#
# ©2017-2019, Center for Spatial Data Science

import pandas as pd


class Configs:
    """
    A utility class to abstract the network parameter
    configurations.
    """
    DEFAULT_SPEED_LIMITS = {"road": 30,
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
                            "roundabout": 40}

    DEFAULT_SPEED_LIMITS = {key : value * 0.4 for key, value in DEFAULT_SPEED_LIMITS.items()}

    def __init__(self, walk_speed=5,
                 bike_speed=15.5,
                 default_drive_speed=40,
                 walk_node_penalty=0,
                 bike_node_penalty=0,
                 drive_node_penalty=4,
                 speed_limit_dict=None):
        """
        Args:
            walk_speed: numeric (km/hr)
            bike_speed: numeric (km/hr)
            default_drive_speed: numeric (km/hr)
            walk_node_penalty:  numeric (seconds)
            bike_node_penalty:  numeric (seconds)
            drive_node_penalty:  numeric (seconds)
            speed_limit_dict: dictionary {edge type (string) : speed in km/hr}
        """
        self.ONE_HOUR = 3600  # seconds
        self.ONE_KM = 1000  # meters
        self.walk_speed = walk_speed  # km/hr
        self.walk_node_penalty = walk_node_penalty  # seconds

        self.default_drive_speed = default_drive_speed  # km/hr
        self.drive_node_penalty = drive_node_penalty  # seconds

        self.bike_speed = bike_speed  # km/hr
        self.bike_node_penalty = bike_node_penalty  # seconds

        if speed_limit_dict is None:
            self.speed_limit_dict = Configs.DEFAULT_SPEED_LIMITS
        else:
            self.speed_limit_dict = speed_limit_dict

    def get_driving_cost_matrix(self):
        """
        Returns: DataFrame of edge unit costs.
        """
        return pd.DataFrame.from_dict(self.speed_limit_dict,
                                      orient='index',
                                      columns=['unit_cost'])

    def get_walk_speed(self):
        """
        Returns: walk speed in meters/second.
        """
        return (self.walk_speed / self.ONE_HOUR) * self.ONE_KM

    def get_bike_speed(self):
        """
        Returns: bike speed in meters/second.
        """
        return (self.bike_speed / self.ONE_HOUR) * self.ONE_KM

    def get_default_drive_speed(self):
        """
        Returns: default drive speed in meters/second.
        """
        return (self.default_drive_speed / self.ONE_HOUR) * self.ONE_KM
