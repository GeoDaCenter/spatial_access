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


class BaseModelException(SpatialAccessException):
    def __init__(self, errors=''):
        super().__init__("BaseModelException:" + errors)


class ModelException(SpatialAccessException):
    def __init__(self, errors=''):
        super().__init__("ModelException:" + errors)


class UnableToConnectException(NetworkInterfaceException):
    def __init__(self, errors=''):
        super().__init__("UnableToConnectException:" + errors)


class BoundingBoxTooLargeException(NetworkInterfaceException):
    def __init__(self, errors=''):
        super().__init__("BoundingBoxTooLargeException:" + errors)

class ConnectedComponentTrimmingFailed(NetworkInterfaceException):
    def __init__(self, errors=''):
        super().__init__("ConnectedComponentTrimmingFailed:" + errors)


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


class WriteTMXFailedException(MatrixInterfaceException):
    def __init__(self, errors=''):
        super().__init__("WriteTMXFailedException:" + errors)


class ReadTMXFailedException(MatrixInterfaceException):
    def __init__(self, errors=''):
        super().__init__("ReadTMXFailedException:" + errors)


class ReadCSVFailedException(MatrixInterfaceException):
    def __init__(self, errors=''):
        super().__init__("ReadCSVFailedException:" + errors)


class ReadOTPCSVFailedException(MatrixInterfaceException):
    def __init__(self, errors=''):
        super().__init__("ReadOTPCSVFailedException:" + errors)


class IndecesNotFoundException(MatrixInterfaceException):
    def __init__(self, errors=''):
        super().__init__("IndecesNotFoundException:" + errors)


class UnableToBuildMatrixException(MatrixInterfaceException):
    def __init__(self, errors=''):
        super().__init__("UnableToBuildMatrixException:" + errors)


class FileNotFoundException(MatrixInterfaceException):
    def __init__(self, errors=''):
        super().__init__("FileNotFoundException:" + errors)


class SourceNotBuiltException(MatrixInterfaceException):
    def __init__(self, errors=''):
        super().__init__("SourceNotBuiltException:" + errors)


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


class TransitMatrixNotLoadedException(BaseModelException):
    def __init__(self, errors=''):
        super().__init__("TransitMatrixNotLoadedException:" + errors)


class SourceDataNotFoundException(BaseModelException):
    def __init__(self, errors=''):
        super().__init__("SourceDataNotFoundException:" + errors)


class DestDataNotFoundException(BaseModelException):
    def __init__(self, errors=''):
        super().__init__("DestDataNotFoundException:" + errors)


class SourceDataNotParsableException(BaseModelException):
    def __init__(self, errors=''):
        super().__init__("SourceDataNotParsableException:" + errors)


class DestDataNotParsableException(BaseModelException):
    def __init__(self, errors=''):
        super().__init__("DestDataNotParsableException:" + errors)


class ShapefileNotFoundException(BaseModelException):
    def __init__(self, errors=''):
        super().__init__("ShapefileNotFoundException:" + errors)


class TooManyCategoriesToPlotException(BaseModelException):
    def __init__(self, errors=''):
        super().__init__("TooManyCategoriesToPlotException:" + errors)


class SpatialIndexNotMatchedException(BaseModelException):
    def __init__(self, errors=''):
        super().__init__("SpatialIndexNotMatchedException:" + errors)


class UnexpectedPlotColumnException(BaseModelException):
    def __init__(self, errors=''):
        super().__init__("UnexpectedPlotColumnException:" + errors)


class UnrecognizedCategoriesException(ModelException):
    def __init__(self, errors=''):
        super().__init__("UnrecognizedCategoriesException:" + errors)


class UnrecognizedDecayFunctionException(ModelException):
    def __init__(self, errors=''):
        super().__init__("UnrecognizedDecayFunctionException:" + errors)


class UnrecognizedFileTypeException(MatrixInterfaceException):
    def __init__(self, errors=''):
        super().__init__("UnrecognizedFileTypeException:" + errors)


class IncompleteCategoryDictException(ModelException):
    def __init__(self, errors=''):
        super().__init__("IncompleteCategoryDictException:" + errors)


class ModelNotAggregatedException(ModelException):
    def __init__(self, errors=''):
        super().__init__("ModelNotAggregatedException:" + errors)
        

class ModelNotAggregatableException(ModelException):
    def __init__(self, errors=''):
        super().__init__("ModelNotAggregatableException:" + errors)


class ModelNotCalculatedException(ModelException):
    def __init__(self, errors=''):
        super().__init__("ModelNotCalculatedException:" + errors)


class UnexpectedNormalizeTypeException(ModelException):
    def __init__(self, errors=''):
        super().__init__("UnexpectedNormalizeTypeException:" + errors)


class UnexpectedNormalizeColumnsException(ModelException):
    def __init__(self, errors=''):
        super().__init__("UnexpectedNormalizeColumnsException:" + errors)


class UnexpectedEmptyColumnException(ModelException):
    def __init__(self, errors=''):
        super().__init__("UnexpectedEmptyColumnException:" + errors)


class UnexpectedAggregationTypeException(ModelException):
    def __init__(self, errors=''):
        super().__init__("UnexpectedAggregationTypeException:" + errors)


class AggregateOutputTypeNotExpectedException(ModelException):
    def __init__(self, errors=''):
        super().__init__("UnexpectedAggregationTypeException:" + errors)

