"""
Abstract interface for the c++ implementation of a matrix.
"""
import multiprocessing
import time
import os
import json
import h5py

from spatial_access.SpatialAccessExceptions import ReadTMXFailedException
from spatial_access.SpatialAccessExceptions import ReadCSVFailedException
from spatial_access.SpatialAccessExceptions import WriteTMXFailedException
from spatial_access.SpatialAccessExceptions import WriteCSVFailedException
from spatial_access.SpatialAccessExceptions import IndecesNotFoundException
from spatial_access.SpatialAccessExceptions import PyTransitMatrixNotBuiltException
from spatial_access.SpatialAccessExceptions import UnableToBuildMatrixException

try:
    from transitMatrixAdapter import pyTransitMatrix
except ImportError:
    raise PyTransitMatrixNotBuiltException()


class MatrixInterface:
    """
    A wrapper for C++ based pandas DataFrame like matrix.
    """

    def __init__(self, logger=None):
        self.logger = logger
        self.transit_matrix = None
        self._warned_once = False
        self._string_id_warning = """
        To optimize performance, your non-integer row and/or
        column labels were remapped to integers. You can recover
        the mapping of integer id to old string id using the following
        methods:
            - get_source_id_remap()
            - get_dest_id_remap()
            - write_source_id_remap_to_json(filename)
            - write_dest_id_remap_to_json(filename)
        """

    def write_h5(self, filename):
        file = h5py.File(filename, 'w')
        meta = file.create_group("meta")
        meta['dataset_name'] = 'dataset_name_'
        #
        meta['rows'] = 9
        meta['columns'] = 5
        meta['is_symmetric'] = False
        strList = ["LEHD","contracts"]
        asciiList = [n.encode("ascii", "ignore") for n in strList]
        meta['id_dataset_name'] = asciiList
        data = file.create_dataset(name="DistMatrix", dtype="i2",shape=(3,2))
        data[0,...] = [1, 2]
        data[1, ...] = [3, 4]
        data[2, ...] = [5, 6]
        string_ids = ["a", "b", "c"]
        asci_ids = [n.encode("ascii", "ignore") for n in string_ids]
        primary_ids = file.create_dataset("LEHD", data=asci_ids, dtype="S10")
        secondary_ids = file.create_dataset("contracts", data=[1, 2], dtype="i8")
        file.close()


    def read_h5(self, filename):
        pass


    def get_source_id_remap(self):
        """
        Get the internal mapping of user string id to 
        integer id for sources, remap bytes to strings.
        """

        remapped_ids = self.transit_matrix.getUserRowIdCache()
        remapped_ids = {k.decode() :v for k, v in remapped_ids.items()}
        if len(remapped_ids) == 0:
            return None
        return remapped_ids

    def write_source_id_remap_to_json(self, filename):
        """
        Write the internal mapping of user string id to 
        integer id for sources to json.
        """
        with open(filename, 'w') as jsonfile:
            json.dump(self.get_source_id_remap(), jsonfile)

    def get_dest_id_remap(self):
        """
        Get the internal mapping of user string id to 
        integer id for dests, remap bytes to strings.
        """
        remapped_ids = self.transit_matrix.getUserColIdCache()
        remapped_ids = {k.decode(): v for k, v in remapped_ids.items()}
        if len(remapped_ids) == 0:
            return None
        return remapped_ids

    def write_dest_id_remap_to_json(self, filename):
        """
        Write the internal mapping of user string id to
        integer id for dests to json.
        """
        with open(filename, 'w') as jsonfile:
            json.dump(self.get_dest_id_remap(), jsonfile)

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

    def add_user_source_data(self, network_id, user_id, distance, primary_only):
        """
        Add the user's source data point to the pyTransitMatrix.
        """
        if isinstance(user_id, str):
            self.transit_matrix.addToUserSourceDataContainerString(network_id, bytes(user_id, 'utf-8'),
                                                                   distance, primary_only)
        else:
            self.transit_matrix.addToUserSourceDataContainerInt(network_id, user_id,
                                                                distance, primary_only)

    def add_user_dest_data(self, network_id, user_id, distance):
        """
        Add the user's dest data point to the pyTransitMatrix.
        """
        if isinstance(user_id, str):
            self.transit_matrix.addToUserDestDataContainerString(network_id, bytes(user_id, 'utf-8'),
                                                                 distance)
        else:
            self.transit_matrix.addToUserDestDataContainerInt(network_id, user_id,
                                                              distance)

    def add_edge_to_graph(self, source, dest, weight, is_bidirectional):
        """
        Add an edge to the graph.
        """
        self.transit_matrix.addEdgeToGraph(source, dest, weight, is_bidirectional)

    def read_from_file(self, infile, is_otp_matrix=False, is_symmetric=False):
        """
        Load a matrix from file
        """
        start_time = time.time()
        assert type(infile) == str, 'infile should be a string'
        assert type(is_otp_matrix) == bool, 'isOTPMatrix should be a bool'
        assert type(is_symmetric) == bool, 'isSymmetric should be a bool'

        if self.logger:
            self.logger.debug('isSymmetric:{}'.format(is_symmetric))
            warning_message = """read_from_file will fail if rows or columns
                                 have non-integer indeces"""
            self.logger.warning(warning_message)

        try:
            self.transit_matrix = pyTransitMatrix(infile=bytes(infile, 'utf-8'),
                                                  isSymmetric=is_symmetric,
                                                  isOTPMatrix=is_otp_matrix)
        except BaseException:
            raise ReadTMXFailedException()
        logger_vars = time.time() - start_time
        if self.logger:
            self.logger.info('Shortest path matrix loaded from disk in {:,.2f} seconds'.format(logger_vars))

    def read_from_csv(self, infile, is_symmetric=False):
        """
        Load a matrix from csv (synonymous to read_from_file)
        """
        try:
            self.read_from_file(infile, is_symmetric=is_symmetric)
        except BaseException:
            raise ReadCSVFailedException()

    def read_from_tmx(self, infile, is_symmetric=False):
        """
        Load a matrix from tmx (synonymous to read_from_file)
        """
        try:
            self.read_from_file(infile, is_symmetric=is_symmetric)
        except BaseException:
            raise ReadTMXFailedException()

    def prepare_matrix(self, num_nodes, is_symmetric=False):
        """
        Instantiate a pyTransitMatrix with the available nodes
        """
        try:
            self.transit_matrix = pyTransitMatrix(vertices=num_nodes, isSymmetric=is_symmetric)
        except BaseException:
            raise UnableToBuildMatrixException()

    def write_to_csv(self, outfile):
        """
        Write the data frame to csv
        """
        start = time.time()
        try:
            self.transit_matrix.writeCSV(bytes(outfile, 'utf-8'))
        except BaseException:
            raise WriteCSVFailedException()
        if self.logger:
            self.logger.info('Wrote to {} in {:,.2f} seconds'.format(outfile, time.time() - start))

    def write_to_tmx(self, outfile):
        """
        Write the data frame to tmx
        """
        try:
            if not os.path.exists(outfile):
                os.mkdir(outfile)
            start = time.time()
            self.transit_matrix.writeTMX(bytes(outfile, 'utf-8'))
        except BaseException:
            raise WriteTMXFailedException()
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
            self.logger.info('Processing matrix with {} threads'.format(thread_limit))
        try:
            self.transit_matrix.compute(thread_limit)
        except BaseException:
            raise UnableToBuildMatrixException()

        logger_vars = time.time() - start_time
        if self.logger:
            self.logger.info('Shortest path matrix computed in {:,.2f} seconds using {} threads'
                             .format(logger_vars, thread_limit))

    def get_dests_in_range(self, threshold):
        """
        Return a source_id->[array of dest_id]
        map for dests under threshold distance
        from source.
        """
        num_threads = self._get_thread_limit()
        return self.transit_matrix.getDestsInRange(threshold, num_threads)

    def get_sources_in_range(self, threshold):
        """
        Return a dest_id->[array of source_id]
        map for sources under threshold distance
        from dest.
        """
        num_threads = self._get_thread_limit()
        return self.transit_matrix.getSourcesInRange(threshold, num_threads)

    def get_value(self, source, dest):
        """
        Fetch the time value associated with the source, dest pair.
        Warning! This method expects int arguments only!
        """
        try:
            return self.transit_matrix.get(source, dest)
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
        self.transit_matrix.addToCategoryMap(dest_id, bytes(category, 'utf-8'))

    def time_to_nearest_dest(self, source_id, category=None):
        """
        Return the time to the nearest destination of a given
        category, or of all destinations if category is none.
        """
        if category is None:
            return self.transit_matrix.timeToNearestDest(source_id)
        else:
            return self.transit_matrix.timeToNearestDestPerCategory(source_id, bytes(category, 'utf-8'))

    def count_dests_in_range(self, source_id, threshold, category=None):
        """
        Return the count of destinations in range for a given
        category, or of all destinations if category is none.
        """
        if category is None:
            return self.transit_matrix.countDestsInRange(source_id, threshold)
        else:
            return self.transit_matrix.countDestsInRangePerCategory(source_id, bytes(category, 'utf-8'), threshold)
