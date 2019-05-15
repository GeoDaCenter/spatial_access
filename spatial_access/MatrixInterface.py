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
from spatial_access._parsers import BaseParser, IntStringParser, StringIntParser, StringStringParser

try:
    import _p2pExtension
except ImportError:
    raise SourceNotBuiltException()


class MatrixInterface:
    """
    A wrapper for C++ based transit matrix.
    """

    def __init__(self, logger=None, require_extended_range=False):
        """
        Args:
            logger: optional
            require_extended_range: Bool. If true, use unsigned integers
                instead of unsigned shorts for value type to increase
                max range.
        """
        self.logger = logger
        self.transit_matrix = None
        self.primary_ids_are_string = False
        self.secondary_ids_are_string = False
        self.is_extended = require_extended_range
        self._parser = None
        self._map_id_type_enum_to_is_string_boolean = {
            0: False,
            1: True
        }
        self._map_value_type_enum_to_is_extended_boolean = {
            0: False,
            1: True
        }

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
        if not os.path.exists(filename):
            raise ReadTMXFailedException("{} does not exist".format(filename))
        tmx_type_reader = _p2pExtension.pyTMXTypeReader(filename.encode('utf-8'))

        self.primary_ids_are_string = self._map_id_type_enum_to_is_string_boolean[
            tmx_type_reader.get_row_type_enum()]
        self.secondary_ids_are_string = self._map_id_type_enum_to_is_string_boolean[
            tmx_type_reader.get_col_type_enum()]
        self.is_extended = self._map_value_type_enum_to_is_extended_boolean[
            tmx_type_reader.get_value_type_enum()]

        self._load_parser()
        self._load_extension()

        try:
            self.transit_matrix.readTMX(self._parser.encode_filename(filename))
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

        try:
            int(header[1])
        except ValueError:
            self.secondary_ids_are_string = True
        try:
            int(first_line[0])
        except ValueError:
            self.primary_ids_are_string = True

        self._load_parser()
        self._load_extension()

        try:
            self.transit_matrix.readCSV(self._parser.encode_filename(filename))
        except BaseException:
            raise ReadCSVFailedException(filename)

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
            self.transit_matrix.writeTMX(self._parser.encode_filename(filename))
        except BaseException:
            raise WriteTMXFailedException(filename)
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
        if not os.path.exists(filename):
            raise FileNotFoundError(filename)

        with open(filename, 'r') as csvfile:
            reader = csv.reader(csvfile)
            first_line = next(reader)

        try:
            int(first_line[0])
        except ValueError:
            self.primary_ids_are_string = True
        try:
            int(first_line[1])
        except ValueError:
            self.primary_ids_are_string = True

        try:
            self._load_parser()
            self._load_extension()
            self.transit_matrix.readOTPCSV(self._parser.encode_filename(filename))
        except BaseException:
            raise ReadOTPCSVFailedException(filename)

    def get_values_by_source(self, source_id, sort=False):
        """
        Args:
            source_id: int or string.
            sort: boolean, the resulting array will be sorted in
                increasing order if true.
        Returns:
            Array of (dest_id, value_ pairs)
        """
        return self._parser.decode_vector_of_dest_tuples(self.transit_matrix.getValuesBySource(self._parser.encode_source_id(source_id),
                                                                                               sort))

    def get_values_by_dest(self, dest_id, sort=False):
        """
        Args:
            dest_id: int or string.
            sort: boolean, the resulting array will be sorted in
                increasing order if true.
        Returns:
            Array of (source_id, value_ pairs)
        """
        return self._parser.decode_vector_of_source_tuples(self.transit_matrix.getValuesByDest(self._parser.encode_dest_id(dest_id),
                                                                                               sort))

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
        self.transit_matrix.addToUserSourceDataContainer(network_id,
                                                         self._parser.encode_source_id(user_id),
                                                         weight)
        if is_also_dest:
            self.transit_matrix.addToUserDestDataContainer(network_id,
                                                           self._parser.encode_dest_id(user_id),
                                                           weight)

    def add_user_dest_data(self, network_id, user_id, weight):
        """
        Add the user's dest data point to the pyTransitMatrix.
        Args:
            network_id: int, osm node loc
            user_id: string or int
            weight: int, edge weight
        """
        self.transit_matrix.addToUserDestDataContainer(network_id,
                                                       self._parser.encode_dest_id(user_id),
                                                       weight)

    def _load_parser(self):
        """
        Load the relevant variant of parser.
        """
        if self.primary_ids_are_string and self.secondary_ids_are_string:
            self._parser = StringStringParser
        elif self.primary_ids_are_string and not self.secondary_ids_are_string:
            self._parser = StringIntParser
        elif not self.primary_ids_are_string and self.secondary_ids_are_string:
            self._parser = IntStringParser
        elif not self.primary_ids_are_string and not self.secondary_ids_are_string:
            self._parser = BaseParser

    def _get_extension(self):
        """
        Returns: class of transit matrix.
        """
        if self.is_extended:
            if self.primary_ids_are_string and self.secondary_ids_are_string:
                return _p2pExtension.pyTransitMatrixSxSxUI
            elif self.primary_ids_are_string and not self.secondary_ids_are_string:
                return _p2pExtension.pyTransitMatrixSxIxUI
            elif not self.primary_ids_are_string and self.secondary_ids_are_string:
                return _p2pExtension.pyTransitMatrixIxSxUI
            elif not self.primary_ids_are_string and not self.secondary_ids_are_string:
                return  _p2pExtension.pyTransitMatrixIxIxUI
        else:
            if self.primary_ids_are_string and self.secondary_ids_are_string:
                return _p2pExtension.pyTransitMatrixSxSxUS
            elif self.primary_ids_are_string and not self.secondary_ids_are_string:
                return _p2pExtension.pyTransitMatrixSxIxUS
            elif not self.primary_ids_are_string and self.secondary_ids_are_string:
                return _p2pExtension.pyTransitMatrixIxSxUS
            elif not self.primary_ids_are_string and not self.secondary_ids_are_string:
                return _p2pExtension.pyTransitMatrixIxIxUS

    def _load_extension(self):
        """
        Load the relevant variant of extension.
        """
        self.transit_matrix = self._get_extension()()

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

        self._load_parser()

        self.transit_matrix = self._get_extension()(is_compressible, is_symmetric, rows, columns)

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
            self.transit_matrix.writeCSV(self._parser.encode_filename(filename))
        except BaseException:
            raise WriteCSVFailedException(filename)
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
            self.logger.debug('Shortest path matrix computed in {:,.2f} seconds'
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
        return self._parser.decode_source_to_dest_array_dict(self.transit_matrix.getDestsInRange(threshold))

    def get_sources_in_range(self, threshold):
        """
        Args:
            threshold: integer, max value for dests "in range".
        Returns:
             a dest_id->[array of source_id]
                map for sources under threshold distance
                from dest.
        """
        return self._parser.decode_dest_to_source_array_dict(self.transit_matrix.getSourcesInRange(threshold))

    def _get_value_by_id(self, source_id, dest_id):
        """
        Warning: should not be used in production.
        """
        try:
            return self.transit_matrix.getValueById(self._parser.encode_source_id(source_id),
                                                    self._parser.encode_dest_id(dest_id))
        except BaseException:
            raise IndecesNotFoundException("{},{}".format(source_id, dest_id))

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
        self.transit_matrix.addToCategoryMap(self._parser.encode_dest_id(dest_id),
                                             self._parser.encode_category(category))

    def time_to_nearest_dest(self, source_id, category=None):
        """
        Returns:
             Time to the nearest destination of a given
                category, or of all destinations if category is none.
        """
        if category is None:
            return self.transit_matrix.timeToNearestDest(self._parser.encode_source_id(source_id))
        else:
            return self.transit_matrix.timeToNearestDestPerCategory(self._parser.encode_source_id(source_id),
                                                                    self._parser.encode_category(category))

    def count_dests_in_range(self, source_id, threshold, category=None):
        """
        Returns:
            Count of destinations in range for a given
                category, or of all destinations if category is none.
        """
        if category is None:
            return self.transit_matrix.countDestsInRange(self._parser.encode_source_id(source_id),
                                                         threshold)
        else:
            return self.transit_matrix.countDestsInRangePerCategory(self._parser.encode_source_id(source_id),
                                                                    self._parser.encode_category(category),
                                                                    threshold)

    def _set_mock_data_frame(self, dataset, source_ids, dest_ids):
        """
        Warning: Not for use in production.
        """
        self.transit_matrix.setMockDataFrame(dataset,
                                             self._parser.encode_vector_source_ids(source_ids),
                                             self._parser.encode_vector_dest_ids(dest_ids))