class SpatialAccessException(Exception):
    """Base class for package exceptions"""
    pass

class MatrixInterfaceException(SpatialAccessException):
    """Base class for MatrixInterface Exceptions"""
    pass

class NetworkInterfaceException(SpatialAccessException):
    """Base class for NetworkInterface Exceptions"""
    pass

class P2PException(SpatialAccessException):
    """Base class for p2p Exceptions"""
    pass

class ScoreModelException(SpatialAccessException):
    """Base class for ScoreModel Exceptions"""
    pass

class CommunityAnalyticsException(SpatialAccessException):
    """Base class for CommunityAnalytics Exceptions"""
    pass


#TODO implement custom exceptions

#TODO incorporate custom exceptions into unit tests