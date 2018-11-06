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

    def __init__(self, logger=None):
        self.logger = logger
        self.transit_matrix = None
        self._internal_index_counter = 0
        self._int_id_map = {}
        self._warned_once = False
        self._string_id_warning = '''
        Using string ids is very slow. 
        You should map noninteger ids to integers instead
        '''

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

    def _get_internal_int_id(self, user_id):
        '''
        Map the user's string id to an internal
        int id.
        '''
        if user_id in self._int_id_map:
            return self._int_id_map[user_id]
        else:
            self._int_id_map[user_id] = self._internal_index_counter
            new_id = self._internal_index_counter
            self._internal_index_counter += 1
            return new_id


    def add_user_source_data(self, network_id, user_id, distance, primary_only):
        '''
        Add the user's source data point to the pyTransitMatrix.
        If the given user_id is a string, first map to an
        internally held int id.
        '''
        if self.logger:
            self.logger.debug('network_id:{}, user_id: {}, distance: {}'.format(network_id, user_id, distance))
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
        if self.logger:
            self.logger.debug('network_id:{}, user_id: {}, distance: {}'.format(network_id, user_id, distance))
        if isinstance(user_id, str):
            if self.logger and not self._warned_once:
                self.logger.warning(self._string_id_warning)
                self._warned_once = True
            user_id = self._get_internal_int_id(user_id)
        self.transit_matrix.addToUserDestDataContainer(network_id, user_id,
                                                       distance)

    def add_edge_to_graph(self, source, dest, weight, is_bidirectional):
        '''
        Add an edge to the graph.
        '''
        self.transit_matrix.addEdgeToGraph(source, dest, weight, is_bidirectional)


    def read_from_csv(self, infile, isSymmetric=False):
        '''
        Load a matrix from file
        '''
        start_time = time.time()
        if self.logger:
            self.logger.debug('isSymmetric:{}'.format(isSymmetric))
            warning_message = '''In this version of spatial_access, you cannot read a matrix
                                 from file if your data have non-integer indeces'''
            self.logger.warning(warning_message)
        try:
            self.transit_matrix = pyTransitMatrix(infile=bytes(infile, 'utf-8'), isSymmetric=isSymmetric)
            logger_vars = time.time() - start_time
            if self.logger:
                self.logger.info(
                'Shortest path matrix loaded from disk in {:,.2f} seconds', logger_vars)
            return
        except BaseException as exception:
            if self.logger:
                self.logger.error('Unable to load matrix from file: %s', exception)
            sys.exit()

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
        self.transit_matrix.writeCSV(bytes(outfile, 'utf-8'))

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
