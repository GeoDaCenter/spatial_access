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


class UnableToConnectException(NetworkInterfaceException):
    """Throws when the client is unable to connect to OSM server"""
    pass


class BoundingBoxTooLargeException(NetworkInterfaceException):
    """Throws when the input data has too large of a bounding box"""
    pass


class ReadTMXFailedException(MatrixInterfaceException):
    """Throws when readTMX fails"""
    pass


class ReadCSVFailedException(MatrixInterfaceException):
    """Throws when readTMX fails"""
    pass


class WriteTMXFailedException(MatrixInterfaceException):
    """Throws when writeTMX fails"""
    pass


class WriteCSVFailedException(MatrixInterfaceException):
    """Throws when writeCSV fails"""
    pass


class IndecesNotFoundException(MatrixInterfaceException):
    """Throws when indeces are not found in the matrix """
    pass


class UnableToBuildMatrixException(MatrixInterfaceException):
    """Throws when matrix cannot be built (this is a bad one)"""
    pass


class PyTransitMatrixNotBuiltException(MatrixInterfaceException):
    """Throws when pyTransitMatrix cannot be imported """
    pass

class PrimaryDataNotFoundException(P2PException):
    """ Throws when the primary data does not exist"""
    pass


class SecondaryDataNotFoundException(P2PException):
    """ Throws when the secondary data does not exist"""
    pass


class UnableToParsePrimaryDataException(P2PException):
    """ Throws when the given column mapping for primary data fails"""
    pass

class UnableToParseSecondaryDataException(P2PException):
    """ Throws when the given column mapping for secondary data fails"""
    pass


class UnknownModeException(P2PException):
    """ Throws when the user supplies an unknown mode of transit"""
    pass


class InsufficientDataException(P2PException):
    """ Throws when the user supplies neither source input data or a matrix file"""
    pass


class TransitMatrixNotLoadedException(ScoreModelException):
    """ Throws when the user has not loaded the transit matrix (shortest path matrix) """
    pass


class SourceDataNotFoundException(ScoreModelException):
    """Throws when source data cannot be found """
    pass


class DestDataNotFoundException(ScoreModelException):
    """ Throws when the destination cannot be found"""
    pass


class SourceDataNotParsableException(ScoreModelException):
    """Throws when the source data is not parsable using supplied hints """
    pass


class DestDataNotParsableException(ScoreModelException):
    """Throws when the dest data is not parsable using supplied hints """
    pass


class ShapefileNotFoundException(ScoreModelException):
    """Throws when the shapefile cannot be found """
    pass


class TooManyCategoriesToPlotException(ScoreModelException):
    """Throws when there are too many categories to plot in the cdf """
    pass


class SpatialIndexNotMatchedException(ScoreModelException):
    """Throws when the spatial index cannot be matched in the shapefile"""
    pass


class UnexpectedPlotColumnException(ScoreModelException):
    """Throws when the the column is not in the model results columns"""
    pass


class UnrecognizedCategoriesException(CommunityAnalyticsException):
    """ Throws when the user supplies categories which are not present in the data"""
    pass


class UnrecognizedDecayFunctionException(CommunityAnalyticsException):
    """ Throws when the user supplies categories which are not present in the data"""
    pass


class IncompleteCategoryDictException(CommunityAnalyticsException):
    """ Throws when the user supplies an incomplete/malformed category dictionary"""
    pass


class ModelNotAggregatedException(CommunityAnalyticsException):
    """ Throws when the user tries to perform an action that requires
    aggregation but has not yet called aggregate"""
    pass
