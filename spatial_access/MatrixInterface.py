"""
Abstract interface for the c++ implementation of a matrix.
"""
import multiprocessing
import time
import os
import h5py

from spatial_access.SpatialAccessExceptions import UnexpectedFileFormatException
from spatial_access.SpatialAccessExceptions import FileNotFoundException
from spatial_access.SpatialAccessExceptions import WriteCSVFailedException
from spatial_access.SpatialAccessExceptions import IndecesNotFoundException
from spatial_access.SpatialAccessExceptions import PyTransitMatrixNotBuiltException
from spatial_access.SpatialAccessExceptions import UnableToBuildMatrixException

try:
    import transitMatrixAdapterIxI
    import transitMatrixAdapterSxS
    import transitMatrixAdapterSxI
    import transitMatrixAdapterIxS
except ImportError:
    raise PyTransitMatrixNotBuiltException()


class MatrixInterface:
    """
    A wrapper for C++ based transit matrix.
    """

    def __init__(self, logger=None):
        self.logger = logger
        self.transit_matrix = None
        self.primary_ids_are_string = False
        self.secondary_ids_are_string = False
        self.dataset_name = None
        self.primary_ids_name = None
        self.secondary_ids_name = None
        self.primary_ids = None
        self.secondary_ids = None

    def write_h5(self, filename):
        file = h5py.File(filename, 'w')
        file['dataset_name'] = self.dataset_name.encode()
        file['is_symmetric'] = self.transit_matrix.getIsSymmetric()
        file['rows'] = self.transit_matrix.getRows()
        file['columns'] = self.transit_matrix.getCols()
        id_dataset = [self.primary_ids_name.encode()]
        if self.secondary_ids_name:
            id_dataset.append(self.secondary_ids_name.encode())

        primary_ids_dtype = "S10" if self.primary_ids_are_string else "i8"
        file.create_dataset(self.primary_ids_name, data=self.transit_matrix.getPrimaryDatasetIds(),
                            dtype=primary_ids_dtype)
        if self.secondary_ids_name:
            secondary_ids_dtype = "S10" if self.primary_ids_are_string else "i8"
            file.create_dataset(self.secondary_ids_name, data=self.transit_matrix.getSecondaryDatasetIds(),
                                dtype=secondary_ids_dtype)
        file.create_dataset(self.dataset_name, data=self.transit_matrix.getDataset(), dtype="i2")
        file.close()

    def read_h5(self, filename):
        if not os.path.exists(filename):
            raise FileNotFoundException(filename)
        file = h5py.File(filename, 'r')
        self.dataset_name = file['dataset_name'].decode()
        is_symmetric = file['is_symmetric']
        rows = file['rows']
        columns = file['columns']

        id_dataset = [name.decode() for name in file['id_dataset_name']]
        self.primary_ids_name = id_dataset[0]
        if len(id_dataset) > 1:
            self.secondary_ids_name = id_dataset[1]
        if is_symmetric and self.secondary_ids_name is not None:
            raise UnexpectedFileFormatException("Illogical to have a symmetric matrix with secondary ids")
        if not is_symmetric and self.secondary_ids_name is None:
            raise UnexpectedFileFormatException("Illogical to have an asymmetric matrix without secondary ids")
        self.primary_ids_are_string = file[self.primary_ids_name].type == str
        if self.secondary_ids_name is None:
            self.secondary_ids_name = self.primary_ids_name
        self.secondary_ids_are_string = file[self.secondary_ids_name].type == str

        if self.primary_ids_are_string and self.secondary_ids_are_string:
            self.transit_matrix = transitMatrixAdapterSxS.pyTransitMatrix(is_symmetric, rows, columns)
        elif self.primary_ids_are_string and not self.secondary_ids_are_string:
            self.transit_matrix = transitMatrixAdapterSxI.pyTransitMatrix(is_symmetric, rows, columns)
        elif not self.primary_ids_are_string and self.primary_ids_are_string:
            self.transit_matrix = transitMatrixAdapterIxS.pyTransitMatrix(is_symmetric, rows, columns)
        elif not self.primary_ids_are_string and not self.primary_ids_are_string:
            self.transit_matrix = transitMatrixAdapterIxI.pyTransitMatrix(is_symmetric, rows, columns)
        else:
            assert False, "Logic Error"

        self.transit_matrix.setPrimaryDataIds(file[self.primary_ids_name])
        self.transit_matrix.setSecondaryDataIds(file[self.secondary_ids_name])
        self.transit_matrix.setDataset(file[self.dataset_name])

        file.close()

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
        self.transit_matrix.addToUserSourceDataContainer(network_id, user_id, distance)
        if not primary_only:
            self.transit_matrix.addToUserDestDataContainer(network_id, user_id, distance)

    def add_user_dest_data(self, network_id, user_id, distance):
        """
        Add the user's dest data point to the pyTransitMatrix.
        """
        self.transit_matrix.addToUserDestDataContainer(network_id, user_id, distance)

    def add_edge_to_graph(self, source, dest, weight, is_bidirectional):
        """
        Add an edge to the graph.
        """
        self.transit_matrix.addEdgeToGraph(source, dest, weight, is_bidirectional)


    def prepare_matrix(self, is_symmetric, rows, columns, network_vertices):
        """
        Instantiate a pyTransitMatrix
        """
        if self.primary_ids_are_string and self.secondary_ids_are_string:
            self.transit_matrix = transitMatrixAdapterSxS.pyTransitMatrix(is_symmetric, rows, columns)
        elif self.primary_ids_are_string and not self.secondary_ids_are_string:
            self.transit_matrix = transitMatrixAdapterSxI.pyTransitMatrix(is_symmetric, rows, columns)
        elif not self.primary_ids_are_string and self.primary_ids_are_string:
            self.transit_matrix = transitMatrixAdapterIxS.pyTransitMatrix(is_symmetric, rows, columns)
        elif not self.primary_ids_are_string and not self.primary_ids_are_string:
            self.transit_matrix = transitMatrixAdapterIxI.pyTransitMatrix(is_symmetric, rows, columns)
        else:
            assert False, "Logic Error"
        self.transit_matrix.prepareGraphWithVertices(network_vertices)

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
