"""
Abstract interface for the c++ implementation of a matrix.
"""

import psutil
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

    def process_matrix(self,
                        infile,
                        nn_pinfile,
                        nn_sinfile,
                        outfile,
                        N,
                        impedence,
                        num_threads,
                        outer_node_rows,
                        outer_node_cols,
                        mode,
                        write_to_file,
                        load_to_mem,
                        read_from_file=False):
        assert(type(infile) == str)
        assert(type(nn_pinfile) == str)
        assert(type(nn_sinfile) == str)
        assert(type(outfile) == str)
        assert(type(N) == int)
        assert(type(impedence) == float)
        assert(type(num_threads) == int)
        assert(type(outer_node_rows) == int)
        assert(type(outer_node_cols) == int)
        assert(type(mode) == int)
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

        self.tm = tmatrix(
            infile.encode('UTF-8'),
            nn_pinfile.encode('UTF-8'),
            nn_sinfile.encode('UTF-8'),
            outfile.encode('UTF-8'),
            N,
            impedence,
            num_threads,
            outer_node_rows,
            outer_node_cols,
            mode,
            write_mode)

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