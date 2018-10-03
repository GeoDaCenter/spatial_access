"""
Abstract interface for the c++ implementation of a matrix.
"""

import psutil
import time
import sys
import multiprocessing
try:
    from pyengine import tmatrix
except BaseException:
    print('Unable to import pyengine. Try running setup.py again')


class MatrixInterface(object):
    '''
    A wrapper for C++ based pandas DataFrame like matrix.
    '''

    def __init__(self, logger):
        self.logger = logger
        self._transit_matrix = None

    @staticmethod
    def _get_thread_limit(self):
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

    def read_matrix_from_file(self, matrix_to_load):
        '''
        Load a matrix from file
        '''
        start_time = time.time()
        try:
            self.build_matrix(
                network_filename=matrix_to_load,
                nn_primary_filename="none",
                nn_secondary_filename="none",
                output_filename="none",
                num_nodes=0,
                impedence_value=0.0,
                outer_node_rows=1,
                outer_node_cols=0,
                write_to_file=False,
                load_to_mem=False,
                read_from_file=True)
            logger_vars = time.time() - start_time
            self.logger.info(
                'Shortest path matrix loaded from disk in {:,.2f} seconds', logger_vars)
            return
        except BaseException as e:
            self.logger.error('Unable to load matrix from file: %s', e)
            sys.exit()


    def build_matrix(self, network_filename,
                     nn_primary_filename, nn_secondary_filename, 
                     output_filename, num_nodes, impedence_value,
                     outer_node_rows, outer_node_cols,
                     write_to_file, load_to_mem, read_from_file=False):
        '''
        Outsources the work of computing the shortest path matrix
        to a C++ module.
        '''

        start_time = time.time()

        if self.write_to_file:
            self.logger.info(
                'Writing to file: %s',
                    self.output_filename)

        assert(type(network_filename) == str)
        assert(type(nn_primary_filename) == str)
        assert(type(nn_secondary_filename) == str)
        assert(type(output_filename) == str)
        assert(type(num_nodes) == int)
        assert(type(impedence_value) == float)
        assert(type(outer_node_rows) == int)
        assert(type(outer_node_cols) == int)
        assert(type(write_to_file) == bool)
        assert(type(load_to_mem) == bool)
        assert(type(read_from_file) == bool)

        GB = 1073741824
        if write_to_file and not load_to_mem:
            write_mode = 0
        elif write_to_file and load_to_mem:
            write_mode = 1
        elif not write_to_file and load_to_mem:
            write_mode = 2
        elif (read_from_file) and (not write_to_file) and (not load_to_mem):
            write_mode = 3
        if load_to_mem:
            expected_memory = int(2 * outer_node_cols * outer_node_rows / GB)
            system_memory = int(psutil.virtual_memory().total / GB)
            if expected_memory > system_memory:
                warning_text = '''WARNING: Expected memory ({} Gb) is greater than
                available system memory ({} Gb). P2p will likely crash,
                please run in write only mode (not load_to_mem)'''.format(
                    expected_memory, system_memory)
                print(warning_text)

        self.transit_matrix = tmatrix(network_filename.encode('UTF-8'),
                                      nn_primary_filename.encode('UTF-8'),
                                      nn_secondary_filename.encode('UTF-8'),
                                      output_filename.encode('UTF-8'),
                                      num_nodes,
                                      impedence_value,
                                      self._get_thread_limit(),
                                      outer_node_rows,
                                      outer_node_cols,
                                      0, # TODO: (lnoel) remove this parameter
                                      write_mode)

        logger_vars = time.time() - start_time
        self.logger.info(
            'Shortest path matrix computed in {:,.2f} seconds', logger_vars)

    def get(self, source, dest):
        '''
        Fetch the time value associated with the source, dest pair.
        '''
        assert self.tm is not None, "tmatrix does not yet exist"
        try:
            return self.tm.get(str(source), str(dest))
        except BaseException:
            if self.logger:
                self.logger.error('Source, dest pair could not be found')