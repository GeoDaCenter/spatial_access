"""
Abstract interface for the c++ implementation of a matrix.
"""
import multiprocessing
import time
import sys
import os
import json
try:
    from transitMatrixAdapter import pyTransitMatrix
except BaseException:
    print('Unable to import pyengine. Try running setup.py again')


class MatrixInterface():
    '''
    A wrapper for C++ based pandas DataFrame like matrix.
    '''

    def __init__(self, logger=None):
        self.logger = logger
        self.transit_matrix = None
        self._source_id_index = 0
        self._dest_id_index = 0
        self._int_id_map = {}
        self._source_id_remap = {}
        self._dest_id_remap = {}
        self._warned_once = False
        self._string_id_warning = '''
        To optimize performance, your non-integer row and/or
        column labels were remapped to integers. You can recover
        the mapping of integer id to old string id using the following
        methods:
            - get_source_id_remap()
            - get_dest_id_remap()
            - write_source_id_remap_to_json(filename)
            - write_dest_id_remap_to_json(filename)
        '''

    def get_source_id_remap(self):
        '''
        Get the internal mapping of user string id to 
        integer id for sources.
        '''

        return self._source_id_remap

    def write_source_id_remap_to_json(self, filename):
        '''
        Write the internal mapping of user string id to 
        integer id for sources to json.
        '''
        with open(filename, 'w') as jsonfile:
            json.dump(self._source_id_remap, jsonfile)

    def get_dest_id_remap(self):
        '''
        Get the internal mapping of user string id to 
        integer id for dests.
        '''

        return self._dest_id_remap

    def get_sources_in_range(self, threshold):
        '''
        '''
        return self.transit_matrix.getSourcesInRange(threshold)

    def get_dests_in_range(self, threshold):
        '''
        '''
        return self.transit_matrix.getDestsInRange(threshold)

    def write_dest_id_remap_to_json(self, filename):
        '''
        Write the internal mapping of user string id to 
        integer id for dests to json.
        '''
        with open(filename, 'w') as jsonfile:
            json.dump(self._dest_id_remap, jsonfile)


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

    def _get_internal_int_id(self, user_id, dest=False):
        '''
        Map the user's string id to an internal
        int id (different sets for source/dest).
        '''
        if not dest:
            if user_id in self._source_id_remap:
                return self._source_id_remap[user_id]
            else:
                self._source_id_remap[user_id] = self._source_id_index
                self._source_id_index += 1
                return self._source_id_index - 1
        else:
            if user_id in self._dest_id_remap:
                return self._dest_id_remap[user_id]
            else:
                self._dest_id_remap[user_id] = self._dest_id_index
                self._dest_id_index += 1
                return self._dest_id_index - 1


    def add_user_source_data(self, network_id, user_id, distance, primary_only):
        '''
        Add the user's source data point to the pyTransitMatrix.
        If the given user_id is a string, first map to an
        internally held int id.
        '''
        if isinstance(user_id, str):
            if self.logger and not self._warned_once:
                self.logger.warning(self._string_id_warning)
                self._warned_once = True
            user_id = self._get_internal_int_id(user_id)

        self.transit_matrix.addToUserSourceDataContainer(network_id, user_id,
                                                         distance, primary_only)

    def add_user_dest_data(self, network_id, user_id, distance):
        '''
        Add the user's dest data point to the pyTransitMatrix.
        If the given user_id is a string, first map to an
        internally held int id.
        '''
        if isinstance(user_id, str):
            if self.logger and not self._warned_once:
                self.logger.warning(self._string_id_warning)
                self._warned_once = True
            user_id = self._get_internal_int_id(user_id, True)
        self.transit_matrix.addToUserDestDataContainer(network_id, user_id,
                                                       distance)


    def add_edge_to_graph(self, source, dest, weight, is_bidirectional):
        '''
        Add an edge to the graph.
        '''
        self.transit_matrix.addEdgeToGraph(source, dest, weight, is_bidirectional)

    def read_from_file(self, infile, isOTPMatrix=False, isSymmetric=False):
        '''
        Load a matrix from file
        '''
        start_time = time.time()
        assert type(infile) == str, 'infile should be a string'
        assert type(isOTPMatrix) == bool, 'isOTPMatrix should be a bool'
        assert type(isSymmetric) == bool, 'isSymmetric should be a bool'

        if self.logger:
            self.logger.debug('isSymmetric:{}'.format(isSymmetric))
            warning_message = '''read_from_file will fail if rows or columns
                                 have non-integer indeces'''
            self.logger.warning(warning_message)
        try:
    
            self.transit_matrix = pyTransitMatrix(infile=bytes(infile, 'utf-8'), 
                                                  isSymmetric=isSymmetric, 
                                                  isOTPMatrix=isOTPMatrix)
            logger_vars = time.time() - start_time
            if self.logger:
                self.logger.info(
                'Shortest path matrix loaded from disk in {:,.2f} seconds'.format(logger_vars))
            return
        except BaseException as exception:
            if self.logger:
                self.logger.error('Unable to load matrix from file: {}'.format(exception))
            sys.exit()

    def read_from_csv(self, infile, isSymmetric=False):
        '''
        Load a matrix from csv (synonymous to read_from_file)
        '''
        self.read_from_file(infile, isSymmetric=isSymmetric)

    def read_from_tmx(self, infile, isSymmetric=False):
        '''
        Load a matrix from tmx (synonymous to read_from_file)
        '''
        self.read_from_file(infile, isSymmetric=isSymmetric)

    def prepare_matrix(self, num_nodes, isSymmetric=False):
        '''
        Instantiate a pyTransitMatrix with the available nodes
        '''
        if self.logger:
            self.logger.debug('isSymmetric:{}'.format(isSymmetric))
        self.transit_matrix = pyTransitMatrix(vertices=num_nodes, isSymmetric=isSymmetric)

    def write_to_csv(self, outfile):
        '''
        Write the data frame to csv
        '''
        start = time.time()
        self.transit_matrix.writeCSV(bytes(outfile, 'utf-8'))
        if self.logger:
            self.logger.info('Wrote to {} in {:,.2f} seconds'.format(outfile, time.time() - start))

    def write_to_tmx(self, outfile):
        '''
        Write the data frame to tmx
        '''
        if not os.path.exists(outfile):
            os.mkdir(outfile)
        start = time.time()
        self.transit_matrix.writeTMX(bytes(outfile, 'utf-8'))
        if self.logger:
            self.logger.info('Wrote to {} in {:,.2f} seconds'.format(outfile, time.time() - start))
        

    def build_matrix(self, thread_limit=None):
        '''
        Outsources the work of computing the shortest path matrix
        to a C++ module.
        '''

        start_time = time.time()
        if thread_limit is None:
            thread_limit = self._get_thread_limit()
        if self.logger:
            self.logger.info('Processing matrix with {} threads'.format(thread_limit))
        self.transit_matrix.compute(thread_limit)

        logger_vars = time.time() - start_time
        if self.logger:
            self.logger.info(
            'Shortest path matrix computed in {:,.2f} seconds using {} threads'.format(logger_vars, thread_limit))

    def get_dests_in_range(self, threshold):
        '''
        Return a source_id->[array of dest_id]
        map for dests under threshold distance
        from source.
        '''
        start_time = time.time()
        numThreads = self._get_thread_limit()
        if self.logger:
            self.logger.info('calculating get_dests_in_range (threshold: {}) using {} threads'.format(threshold, numThreads))
        res = self.transit_matrix.getDestsInRange(threshold, numThreads)
        if self.logger:
            self.logger.info('get_dests_in_range computed in {:,.2f} seconds'.format(time.time() - start_time))
        return res

    def get_sources_in_range(self, threshold):
        '''
        Return a dest_id->[array of source_id]
        map for sources under threshold distance
        from dest.
        '''
        start_time = time.time()
        numThreads = self._get_thread_limit()
        if self.logger:
            self.logger.info('calculating get_sources_in_range (threshold: {}) using {} threads'.format(threshold, numThreads))
        res = self.transit_matrix.getSourcesInRange(threshold, numThreads)
        if self.logger:
            self.logger.info('get_sources_in_range computed in {:,.2f} seconds'.format(time.time() - start_time))
        return res

    def get(self, source, dest):
        '''
        Fetch the time value associated with the source, dest pair.
        '''
        if isinstance(source, str):
            source = self._get_internal_int_id(source)
        if isinstance(dest, str):
            dest = self._get_internal_int_id(dest)
        try:
            return self.transit_matrix.get(source, dest)
        except BaseException:
            if self.logger:
                self.logger.error('Source, dest pair could not be found')

    def printDataFrame(self):
        '''
        Print the underlying data frame.
        '''
        self.transit_matrix.printDataFrame()

