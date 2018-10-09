"""
Abstract interface for the c++ implementation of a matrix.
"""
import multiprocessing
import time
import sys
try:
    from transitMatrixAdapter import pyTransitMatrix
except BaseException:
    print('Unable to import pyengine. Try running setup.py again')


class MatrixInterface():
    '''
    A wrapper for C++ based pandas DataFrame like matrix.
    '''

    def __init__(self, logger):
        self.logger = logger
        self.transit_matrix = None

    @staticmethod
    def _get_thread_limit():
        '''
        Determine if the algorithm should be throttled
        based on the available system memory and number of cores.
        Returns: int (num threads to use)
        '''

        no_cores = multiprocessing.cpu_count()
        if no_cores > 2:
            no_cores -= 1
        else:
            no_cores = 1

        return no_cores

    def read_matrix_from_file(self, outfile):
        '''
        Load a matrix from file
        '''
        start_time = time.time()
        try:
            self.transit_matrix = pyTransitMatrix(infile=bytes(outfile))
            logger_vars = time.time() - start_time
            self.logger.info(
                'Shortest path matrix loaded from disk in {:,.2f} seconds', logger_vars)
            return
        except BaseException as exception:
            self.logger.error('Unable to load matrix from file: %s', exception)
            sys.exit()

    def prepare_matrix(self, num_nodes):
        '''
        Instantiate a pyTransitMatrix with the available nodes
        '''
        self.transit_matrix = pyTransitMatrix(vertices=num_nodes)

    def write_to_csv(self, outfile):
        '''
        Write the data frame to csv
        '''
        self.transit_matrix.writeCSV(bytes(outfile))

    def build_matrix(self):
        '''
        Outsources the work of computing the shortest path matrix
        to a C++ module.
        '''

        start_time = time.time()

        self.transit_matrix.compute(self._get_thread_limit())

        logger_vars = time.time() - start_time
        self.logger.info(
            'Shortest path matrix computed in {:,.2f} seconds', logger_vars)

    def get(self, source, dest):
        '''
        Fetch the time value associated with the source, dest pair.
        '''
        try:
            return self.transit_matrix.get(bytes(str(source))), bytes(str(dest))
        except BaseException:
            if self.logger:
                self.logger.error('Source, dest pair could not be found')
