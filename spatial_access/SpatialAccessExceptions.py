# Logan Noel (github.com/lmnoel)
#
# ©2017-2019, Center for Spatial Data Science

class SpatialAccessException(Exception):
    def __init__(self, errors=''):
        super().__init__("SpatialAccessException:" + errors)


class MatrixInterfaceException(SpatialAccessException):
    def __init__(self, errors=''):
        super().__init__("MatrixInterfaceException:" + errors)


class NetworkInterfaceException(SpatialAccessException):
    def __init__(self, errors=''):
        super().__init__("NetworkInterfaceException:" + errors)


class P2PException(SpatialAccessException):
    def __init__(self, errors=''):
        super().__init__("P2PException:" + errors)


class ScoreModelException(SpatialAccessException):
    def __init__(self, errors=''):
        super().__init__("ScoreModelException:" + errors)


class CommunityAnalyticsException(SpatialAccessException):
    def __init__(self, errors=''):
        super().__init__("CommunityAnalyticsException:" + errors)


class UnableToConnectException(NetworkInterfaceException):
    def __init__(self, errors=''):
        super().__init__("UnableToConnectException:" + errors)


class BoundingBoxTooLargeException(NetworkInterfaceException):
    def __init__(self, errors=''):
        super().__init__("BoundingBoxTooLargeException:" + errors)


class UnexpectedFileFormatException(MatrixInterfaceException):
    def __init__(self, errors=''):
        super().__init__("UnexpectedFileFormatException:" + errors)


class UnexpectedShapeException(MatrixInterfaceException):
    def __init__(self, errors=''):
        super().__init__("UnexpectedShapeException:" + errors)


class InvalidIdTypeException(MatrixInterfaceException):
    def __init__(self, errors=''):
        super().__init__("InvalidIdTypeException:" + errors)


class WriteCSVFailedException(MatrixInterfaceException):
    def __init__(self, errors=''):
        super().__init__("WriteCSVFailedException:" + errors)


class WriteH5FailedException(MatrixInterfaceException):
    def __init__(self, errors=''):
        super().__init__("WriteH5FailedException:" + errors)


class ReadH5FailedException(MatrixInterfaceException):
    def __init__(self, errors=''):
        super().__init__("ReadH5FailedException:" + errors)


class IndecesNotFoundException(MatrixInterfaceException):
    def __init__(self, errors=''):
        super().__init__("IndecesNotFoundException:" + errors)


class UnableToBuildMatrixException(MatrixInterfaceException):
    def __init__(self, errors=''):
        super().__init__("UnableToBuildMatrixException:" + errors)


class FileNotFoundException(MatrixInterfaceException):
    def __init__(self, errors=''):
        super().__init__("UnableToBuildMatrixException:" + errors)


class PyTransitMatrixNotBuiltException(MatrixInterfaceException):
    def __init__(self, errors=''):
        super().__init__("PyTransitMatrixNotBuiltException:" + errors)


class PrimaryDataNotFoundException(P2PException):
    def __init__(self, errors=''):
        super().__init__("PrimaryDataNotFoundException:" + errors)


class SecondaryDataNotFoundException(P2PException):
    def __init__(self, errors=''):
        super().__init__("SecondaryDataNotFoundException:" + errors)


class UnableToParsePrimaryDataException(P2PException):
    def __init__(self, errors=''):
        super().__init__("UnableToParsePrimaryDataException:" + errors)


class UnableToParseSecondaryDataException(P2PException):
    def __init__(self, errors=''):
        super().__init__("UnableToParseSecondaryDataException:" + errors)


class UnknownModeException(P2PException):
    def __init__(self, errors=''):
        super().__init__("UnknownModeException:" + errors)


class InsufficientDataException(P2PException):
    def __init__(self, errors=''):
        super().__init__("InsufficientDataException:" + errors)


class DuplicateInputException(P2PException):
    def __init__(self, errors=''):
        super().__init__("DuplicateInputException:" + errors)


class TransitMatrixNotLoadedException(ScoreModelException):
    def __init__(self, errors=''):
        super().__init__("TransitMatrixNotLoadedException:" + errors)


class SourceDataNotFoundException(ScoreModelException):
    def __init__(self, errors=''):
        super().__init__("SourceDataNotFoundException:" + errors)


class DestDataNotFoundException(ScoreModelException):
    def __init__(self, errors=''):
        super().__init__("DestDataNotFoundException:" + errors)


class SourceDataNotParsableException(ScoreModelException):
    def __init__(self, errors=''):
        super().__init__("SourceDataNotParsableException:" + errors)


class DestDataNotParsableException(ScoreModelException):
    def __init__(self, errors=''):
        super().__init__("DestDataNotParsableException:" + errors)


class ShapefileNotFoundException(ScoreModelException):
    def __init__(self, errors=''):
        super().__init__("ShapefileNotFoundException:" + errors)


class TooManyCategoriesToPlotException(ScoreModelException):
    def __init__(self, errors=''):
        super().__init__("TooManyCategoriesToPlotException:" + errors)


class SpatialIndexNotMatchedException(ScoreModelException):
    def __init__(self, errors=''):
        super().__init__("SpatialIndexNotMatchedException:" + errors)


class UnexpectedPlotColumnException(ScoreModelException):
    def __init__(self, errors=''):
        super().__init__("UnexpectedPlotColumnException:" + errors)


class UnrecognizedCategoriesException(CommunityAnalyticsException):
    def __init__(self, errors=''):
        super().__init__("UnrecognizedCategoriesException:" + errors)


class UnrecognizedDecayFunctionException(CommunityAnalyticsException):
    def __init__(self, errors=''):
        super().__init__("UnrecognizedDecayFunctionException:" + errors)


class IncompleteCategoryDictException(CommunityAnalyticsException):
    def __init__(self, errors=''):
        super().__init__("IncompleteCategoryDictException:" + errors)


class ModelNotAggregatedException(CommunityAnalyticsException):
    def __init__(self, errors=''):
        super().__init__("ModelNotAggregatedException:" + errors)


class UnexpectedNormalizeTypeException(CommunityAnalyticsException):
    def __init__(self, errors=''):
        super().__init__("UnexpectedNormalizeTypeException:" + errors)


class UnexpectedNormalizeColumnsException(CommunityAnalyticsException):
    def __init__(self, errors=''):
        super().__init__("UnexpectedNormalizeColumnsException:" + errors)


class UnexpectedEmptyColumnException(CommunityAnalyticsException):
    def __init__(self, errors=''):
        super().__init__("UnexpectedEmptyColumnException:" + errors)


class UnexpectedAggregationTypeException(CommunityAnalyticsException):
    def __init__(self, errors=''):
        super().__init__("UnexpectedAggregationTypeException:" + errors)


class AggregateOutputTypeNotExpectedException(CommunityAnalyticsException):
    def __init__(self, errors=''):
        super().__init__("UnexpectedAggregationTypeException:" + errors)

