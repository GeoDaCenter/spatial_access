# Logan Noel (github.com/lmnoel)
#
# ©2017-2019, Center for Spatial Data Science

import multiprocessing
import time
import os
import csv

from spatial_access.SpatialAccessExceptions import WriteCSVFailedException
from spatial_access.SpatialAccessExceptions import WriteTMXFailedException
from spatial_access.SpatialAccessExceptions import ReadTMXFailedException
from spatial_access.SpatialAccessExceptions import ReadCSVFailedException
from spatial_access.SpatialAccessExceptions import ReadOTPCSVFailedException
from spatial_access.SpatialAccessExceptions import UnrecognizedFileTypeException
from spatial_access.SpatialAccessExceptions import IndecesNotFoundException
from spatial_access.SpatialAccessExceptions import SourceNotBuiltException
from spatial_access.SpatialAccessExceptions import UnableToBuildMatrixException
from spatial_access.SpatialAccessExceptions import UnexpectedShapeException


try:
    import _p2pExtension
except ImportError:
    raise SourceNotBuiltException()


class MatrixInterface:
    """
    A wrapper for C++ based transit matrix.
    """

    def __init__(self, logger=None):
        """
        Args:
            logger: optional
        """
        self.logger = logger
        self.transit_matrix = None
        self.primary_ids_are_string = False
        self.secondary_ids_are_string = False

    def _read_tmx(self, filename):
        """
        Read the transit matrix from binary format.
        (suitable for quickly saving/reloading for
        extended computations).
        Args:
            filename: filename with .tmx extension
        Raises:
            ReadTMXFailedException: file does not exist or is corrupted.
        """

        utils = _p2pExtension.pyTMXUtils()
        if not os.path.exists(filename):
            raise ReadTMXFailedException("{} does not exist".format(filename))
        tmxType = utils.getTypeOfTMX(filename)
        if tmxType == 0:
            self.transit_matrix = _p2pExtension.pyTransitMatrixIxI()
        elif tmxType == 1:
            self.transit_matrix = _p2pExtension.pyTransitMatrixIxS()
        elif tmxType == 2:
            self.transit_matrix = _p2pExtension.pyTransitMatrixSxI()
        elif tmxType == 3:
            self.transit_matrix = _p2pExtension.pyTransitMatrixSxS()
        else:
            raise ReadTMXFailedException("Unrecognized tmx type: {}".format(tmxType))
        try:
            self.transit_matrix.readTMX(filename)
        except BaseException:
            raise ReadTMXFailedException("Unable to read tmx from {}".format(filename))

    def _read_csv(self, filename):
        """
        Read the transit matrix from MxN csv. Warning:
        you shouldn't use this method! It can be up to 1000x slower
        than the tmx format.
        Args:
            filename: filename with .csv extension
        Raises:
            ReadCSVFailedException: file does not exist or is corrupted.
        """
        if self.logger:
            self.logger.warning("You should use tmx instead of csv for significantly better performance")
        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            first_line = next(reader)

        col_ids_are_int = True
        row_ids_are_int = True
        try:
            int(header[0])
        except ValueError:
            col_ids_are_int = False
        try:
            int(first_line[0])
        except ValueError:
            row_ids_are_int = False
        if row_ids_are_int and col_ids_are_int:
            self.transit_matrix = _p2pExtension.pyTransitMatrixIxI()
        elif row_ids_are_int and not col_ids_are_int:
            self.transit_matrix = _p2pExtension.pyTransitMatrixIxS()
        elif not row_ids_are_int and col_ids_are_int:
            self.transit_matrix = _p2pExtension.pyTransitMatrixSxI()
        elif not row_ids_are_int and not col_ids_are_int:
            self.transit_matrix = _p2pExtension.pyTransitMatrixSxS()
        else:
            assert False, "Logic Error"

        try:
            self.transit_matrix.read_csv(filename)
        except BaseException:
            raise ReadCSVFailedException()

    def read_file(self, filename):
        """
        Read the transit matrix from binary format.
        (suitable for quickly saving/reloading for
        extended computations).
        Args:
            filename: filename with .tmx or .csv extension
        Raises:
            UnrecognizedFileTypeException: filename without .tmx or .csv
                extension.
        """
        if not os.path.exists(filename):
            raise FileNotFoundError(filename)
        extension = filename.split('.')[-1]
        if extension == 'tmx':
            self._read_tmx(filename)
        elif extension == 'csv':
            self._read_csv(filename)
        else:
            raise UnrecognizedFileTypeException(extension)

    def write_tmx(self, filename):
        """
        Write the transit matrix to binary format.
        (suitable for quickly saving/reloading for
        extended computations).
        Args:
            filename: tmx filename.
        Raises:
            WriteTMXFailedException: unable to write tmx.
        """
        start = time.time()
        try:
            self.transit_matrix.writeTMX(filename)
        except BaseException:
            raise WriteTMXFailedException("Unable to write tmx to {}".format(filename))
        if self.logger:
            self.logger.info('Wrote to {} in {:,.2f} seconds'.format(filename, time.time() - start))

    def add_edges_to_graph(self, from_column, to_column, edge_weight_column,
                           is_bidirectional_column):
        """
        Args:
            from_column: array of integers, network node ids.
            to_column: array of integers, network node ids.
            edge_weight_column: array of integers, edge weights.
            is_bidirectional_column:, array of booleans, is the edge bidirectional.
        """
        self.transit_matrix.addEdgesToGraph(from_column, to_column, edge_weight_column, is_bidirectional_column)

    def read_otp(self, filename):
        """
        Args:
            filename: otp csv.
        Raises:
            ReadOTPCSVFailedException
        """
        try:
            self.transit_matrix = _p2pExtension.pyTransitMatrixIxI()
            self.transit_matrix.readOTPCSV(filename)
        except BaseException:
            raise ReadOTPCSVFailedException()

    def get_values_by_source(self, source_id, sort=False):
        """
        Args:
            source_id: int or string.
            sort: boolean, the resulting array will be sorted in
                increasing order if true.
        Returns:
            Array of (dest_id, value_ pairs)
        """
        return self.transit_matrix.getValuesBySource(source_id, sort)

    def get_values_by_dest(self, dest_id, sort=False):
        """
        Args:
            dest_id: int or string.
            sort: boolean, the resulting array will be sorted in
                increasing order if true.
        Returns:
            Array of (source_id, value_ pairs)
        """
        return self.transit_matrix.getValuesByDest(dest_id, sort)

    @staticmethod
    def _get_thread_limit():
        """
        Returns: int (num threads to use)
        """
        return multiprocessing.cpu_count()

    def add_user_source_data(self, network_id, user_id, weight, is_also_dest):
        """
        Add the user's source data point to the pyTransitMatrix.
        Args:
            network_id: int, osm node loc
            user_id: string or int
            weight: int, edge weight
            is_also_dest: boolean, true for symmetric matrices
        """
        self.transit_matrix.addToUserSourceDataContainer(network_id, user_id, weight)
        if is_also_dest:
            self.transit_matrix.addToUserDestDataContainer(network_id, user_id, weight)

    def add_user_dest_data(self, network_id, user_id, weight):
        """
        Add the user's dest data point to the pyTransitMatrix.
        Args:
            network_id: int, osm node loc
            user_id: string or int
            weight: int, edge weight
        """
        self.transit_matrix.addToUserDestDataContainer(network_id, user_id, weight)

    def prepare_matrix(self, is_symmetric, is_compressible, rows, columns, network_vertices):
        """
        Instantiate a pyTransitMatrix.
        Args:
            is_symmetric: boolean, true if matrix is NxN.
            is_compressible: boolean, true if matrix[i][j] == matrix[j][i]
                for all (i, j) in matrix. Enables more efficient storage
                representation.
            rows: number of user rows.
            columns: number of user columns.
            network_vertices: number of vertices in osm network.

        Raises:
            UnexpectedShapeException: if a matrix is symmetric but has mismatched rows and
                columns, or if matrix is marked is_compressible but not is_symmetric.
        """
        if is_symmetric and rows != columns:
            raise UnexpectedShapeException("Symmetric matrices should be nxn, not {}x{}".format(rows, columns))
        if is_compressible and not is_symmetric:
            raise UnexpectedShapeException("If matrix is compressible, it is also symmetric")
        if is_symmetric:
            self.secondary_ids_are_string = self.primary_ids_are_string
        if self.primary_ids_are_string and self.secondary_ids_are_string:
            self.transit_matrix = _p2pExtension.pyTransitMatrixSxS(is_compressible, is_symmetric, rows, columns)
        elif self.primary_ids_are_string and not self.secondary_ids_are_string:
            self.transit_matrix = _p2pExtension.pyTransitMatrixSxI(is_compressible, is_symmetric, rows, columns)
        elif not self.primary_ids_are_string and self.secondary_ids_are_string:
            self.transit_matrix = _p2pExtension.pyTransitMatrixIxS(is_compressible, is_symmetric, rows, columns)
        elif not self.primary_ids_are_string and not self.secondary_ids_are_string:
            self.transit_matrix = _p2pExtension.pyTransitMatrixIxI(is_compressible, is_symmetric, rows, columns)
        else:
            assert False, "Logic Error"
        self.transit_matrix.prepareGraphWithVertices(network_vertices)

    def write_csv(self, filename):
        """
        Args:
            filename: file to write the transit matrix to.
        Raises:
            WriteCSVFailedException: transit matrix encountered an
                internal error.
        """
        start = time.time()
        try:
            self.transit_matrix.writeCSV(filename)
        except BaseException:
            raise WriteCSVFailedException()
        if self.logger:
            self.logger.info('Wrote to {} in {:,.2f} seconds'.format(filename, time.time() - start))

    def build_matrix(self):
        """
        Raises:
            UnableToBuildMatrixException: transit matrix encountered
                an internal error.
        """

        start_time = time.time()

        thread_limit = self._get_thread_limit()
        if self.logger:
            self.logger.debug('Processing matrix with {} threads'.format(thread_limit))
        try:
            self.transit_matrix.compute(thread_limit)
        except BaseException:
            raise UnableToBuildMatrixException()

        logger_vars = time.time() - start_time
        if self.logger:
            self.logger.info('Shortest path matrix computed in {:,.2f} seconds'
                             .format(logger_vars))

    def get_dests_in_range(self, threshold):
        """
        Args:
            threshold: integer, max value for dests "in range".
        Returns:
             a source_id->[array of dest_id]
                map for dests under threshold distance
                from source.
        """
        return self.transit_matrix.getDestsInRange(threshold)

    def get_sources_in_range(self, threshold):
        """
        Args:
            threshold: integer, max value for dests "in range".
        Returns:
             a dest_id->[array of source_id]
                map for sources under threshold distance
                from dest.
        """
        return self.transit_matrix.getSourcesInRange(threshold)

    def _get_value_by_id(self, source, dest):
        """
        Should not be used in production.
        """
        try:
            return self.transit_matrix.getValueById(source, dest)
        except BaseException:
            raise IndecesNotFoundException() 

    def print_data_frame(self):
        """
        Print the underlying data frame.
        """
        self.transit_matrix.printDataFrame()

    def add_to_category_map(self, dest_id, category):
        """
        Args:
            dest_id: int or string
            category: string
        Map the dest_id to the category in the
        transit matrix.
        """
        self.transit_matrix.addToCategoryMap(dest_id, category)

    def time_to_nearest_dest(self, source_id, category=None):
        """
        Returns:
             Time to the nearest destination of a given
                category, or of all destinations if category is none.
        """
        if category is None:
            return self.transit_matrix.timeToNearestDest(source_id)
        else:
            return self.transit_matrix.timeToNearestDestPerCategory(source_id, category)

    def count_dests_in_range(self, source_id, threshold, category=None):
        """
        Returns:
            Count of destinations in range for a given
                category, or of all destinations if category is none.
        """
        if category is None:
            return self.transit_matrix.countDestsInRange(source_id, threshold)
        else:
            return self.transit_matrix.countDestsInRangePerCategory(source_id, category, threshold)
