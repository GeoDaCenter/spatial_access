# Logan Noel (github.com/lmnoel)
#
# ©2017-2019, Center for Spatial Data Science


class UnableToConnectException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class BoundingBoxTooLargeException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class ConnectedComponentTrimmingFailed(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class UnexpectedFileFormatException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class UnexpectedShapeException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class InvalidIdTypeException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class WriteCSVFailedException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class WriteTMXFailedException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class ReadTMXFailedException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class ReadCSVFailedException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class ReadOTPCSVFailedException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class IndecesNotFoundException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class UnableToBuildMatrixException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class FileNotFoundException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class SourceNotBuiltException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class PrimaryDataNotFoundException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class SecondaryDataNotFoundException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class ImproperIndecesTypeException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class UnableToParsePrimaryDataException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class UnableToParseSecondaryDataException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class UnknownModeException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class InsufficientDataException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class DuplicateInputException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class TransitMatrixNotLoadedException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class SourceDataNotFoundException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class DestDataNotFoundException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class SourceDataNotParsableException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class DestDataNotParsableException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class ShapefileNotFoundException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class TooManyCategoriesToPlotException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class SpatialIndexNotMatchedException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class UnexpectedPlotColumnException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class UnrecognizedCategoriesException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class UnrecognizedDecayFunctionException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class UnrecognizedFileTypeException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class IncompleteCategoryDictException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class ModelNotAggregatedException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)
        

class ModelNotAggregatableException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class ModelNotCalculatedException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class UnexpectedNormalizeTypeException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class UnexpectedNormalizeColumnsException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class UnexpectedEmptyColumnException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class UnexpectedAggregationTypeException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)


class AggregateOutputTypeNotExpectedException(Exception):
    def __init__(self, errors=''):
        super().__init__(errors)

