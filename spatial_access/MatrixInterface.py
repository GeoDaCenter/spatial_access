# Logan Noel (github.com/lmnoel)
#
# ©2017-2019, Center for Spatial Data Science

import multiprocessing
import time
import os

from spatial_access.SpatialAccessExceptions import UnexpectedFileFormatException
from spatial_access.SpatialAccessExceptions import FileNotFoundException
from spatial_access.SpatialAccessExceptions import WriteCSVFailedException
from spatial_access.SpatialAccessExceptions import WriteTMXFailedException
from spatial_access.SpatialAccessExceptions import ReadTMXFailedException
from spatial_access.SpatialAccessExceptions import IndecesNotFoundException
from spatial_access.SpatialAccessExceptions import SourceNotBuiltException
from spatial_access.SpatialAccessExceptions import UnableToBuildMatrixException
from spatial_access.SpatialAccessExceptions import UnexpectedShapeException


try:
    import transitMatrixAdapterIxI
    import transitMatrixAdapterSxS
    import transitMatrixAdapterSxI
    import transitMatrixAdapterIxS
    import TMXUtils
except ImportError:
    raise SourceNotBuiltException()


class MatrixInterface:
    """
    A wrapper for C++ based transit matrix.
    """

    def __init__(self, logger=None):
        self.logger = logger
        self.transit_matrix = None
        self.primary_ids_are_string = False
        self.secondary_ids_are_string = False

    def read_tmx(self, filename):
        """
        Read tmx from file
        """
        utils = TMXUtils.pyTMXUtils()
        if not os.path.exists(filename):
            raise ReadTMXFailedException("{} does not exist".format(filename))
        tmxType = utils.getTypeOfTMX(filename)
        if tmxType == 0:
            self.transit_matrix = transitMatrixAdapterIxI.pyTransitMatrix()
        elif tmxType == 1:
            self.transit_matrix = transitMatrixAdapterIxS.pyTransitMatrix()
        elif tmxType == 2:
            self.transit_matrix = transitMatrixAdapterSxI.pyTransitMatrix()
        elif tmxType == 3:
            self.transit_matrix = transitMatrixAdapterSxS.pyTransitMatrix()
        else:
            raise ReadTMXFailedException("Unrecognized tmx type: {}".format(tmxType))
        try:
            self.transit_matrix.readTMX(filename)
        except BaseException:
            raise ReadTMXFailedException("Unable to read tmx from {}".format(filename))

    def write_tmx(self, filename):
        """
        Write tmx to file
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
        """
        self.transit_matrix = transitMatrixAdapterIxI.pyTransitMatrix()
        self.transit_matrix.readOTPCSV(filename)

    def get_values_by_source(self, source_id, sort=False):
        """
        Get a list of (dest_id, value) pairs, with the option
        to sort in increasing order by value.
        """
        return self.transit_matrix.getValuesBySource(source_id, sort)

    def get_values_by_dest(self, dest_id, sort=False):
        """
        Get a list of (source_id, value) pairs, with the option
        to sort in increasing order by value.
        """
        return self.transit_matrix.getValuesByDest(dest_id, sort)

    @staticmethod
    def _get_thread_limit():
        """
        Determine if the algorithm should be throttled
        based on the available system memory and number of cores.
        Returns: int (num threads to use)
        """

        no_cores = multiprocessing.cpu_count()
        if no_cores > 2:
            no_cores -= 1
        else:
            no_cores = 1

        return no_cores

    def add_user_source_data(self, network_id, user_id, weight, is_also_dest):
        """
        Add the user's source data point to the pyTransitMatrix.
        """
        self.transit_matrix.addToUserSourceDataContainer(network_id, user_id, weight)
        if is_also_dest:
            self.add_user_dest_data(network_id, user_id, weight)

    def add_user_dest_data(self, network_id, user_id, weight):
        """
        Add the user's dest data point to the pyTransitMatrix.
        """
        self.transit_matrix.addToUserDestDataContainer(network_id, user_id, weight)

    def prepare_matrix(self, is_symmetric, is_compressible, rows, columns, network_vertices):
        """
        Instantiate a pyTransitMatrix
        """

        if is_symmetric and rows != columns:
            raise UnexpectedShapeException("Symmetric matrices should be nxn, not {}x{}".format(rows, columns))
        if is_symmetric:
            self.secondary_ids_are_string = self.primary_ids_are_string
        if self.primary_ids_are_string and self.secondary_ids_are_string:
            self.transit_matrix = transitMatrixAdapterSxS.pyTransitMatrix(is_compressible, is_symmetric, rows, columns)
        elif self.primary_ids_are_string and not self.secondary_ids_are_string:
            self.transit_matrix = transitMatrixAdapterSxI.pyTransitMatrix(is_compressible, is_symmetric, rows, columns)
        elif not self.primary_ids_are_string and self.secondary_ids_are_string:
            self.transit_matrix = transitMatrixAdapterIxS.pyTransitMatrix(is_compressible, is_symmetric, rows, columns)
        elif not self.primary_ids_are_string and not self.secondary_ids_are_string:
            self.transit_matrix = transitMatrixAdapterIxI.pyTransitMatrix(is_compressible, is_symmetric, rows, columns)
        else:
            assert False, "Logic Error"
        self.transit_matrix.prepareGraphWithVertices(network_vertices)

    def write_csv(self, outfile):
        """
        Write the data frame to csv
        """
        start = time.time()
        try:
            self.transit_matrix.writeCSV(outfile)
        except BaseException:
            raise WriteCSVFailedException()
        if self.logger:
            self.logger.info('Wrote to {} in {:,.2f} seconds'.format(outfile, time.time() - start))

    def build_matrix(self, thread_limit=None):
        """
        Outsources the work of computing the shortest path matrix
        to a C++ module.
        """

        start_time = time.time()
        if thread_limit is None:
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
        Return a source_id->[array of dest_id]
        map for dests under threshold distance
        from source.
        """
        return self.transit_matrix.getDestsInRange(threshold)

    def get_sources_in_range(self, threshold):
        """
        Return a dest_id->[array of source_id]
        map for sources under threshold distance
        from dest.
        """
        return self.transit_matrix.getSourcesInRange(threshold)

    def get_value_by_id(self, source, dest):
        """
        Fetch the time value associated with the source, dest pair.
        Warning! This method expects int arguments only!
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
        Map the dest_id to the category in the
        transit matrix.
        """
        self.transit_matrix.addToCategoryMap(dest_id, category)

    def time_to_nearest_dest(self, source_id, category=None):
        """
        Return the time to the nearest destination of a given
        category, or of all destinations if category is none.
        """
        if category is None:
            return self.transit_matrix.timeToNearestDest(source_id)
        else:
            return self.transit_matrix.timeToNearestDestPerCategory(source_id, category)

    def count_dests_in_range(self, source_id, threshold, category=None):
        """
        Return the count of destinations in range for a given
        category, or of all destinations if category is none.
        """
        if category is None:
            return self.transit_matrix.countDestsInRange(source_id, threshold)
        else:
            return self.transit_matrix.countDestsInRangePerCategory(source_id, category, threshold)
