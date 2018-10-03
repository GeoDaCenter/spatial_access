"""
Program to calculate the network time between every point in a set, hence: "p2p".
Written by Logan Noel for the Center for Spatial Data Science, 2018.
(runs in O(Elog(V)) time)

Also many thanks to OSM for supplying data: www.openstreetmap.org
"""

import multiprocessing
import time
import sys
import csv
import json
import logging
import math
import os, os.path
from collections import deque
import ast
import scipy.spatial
from geopy.distance import vincenty
from jellyfish import jaro_winkler
import numpy as np
import pandas as pd

from spatial_access.MatrixInterface import MatrixInterface
from spatial_access.NetworkInterface import NetworkInterface
from spatial_access.ConfigInterface import ConfigInterface


class TransitMatrix(object):
    '''
    A unified class to manage all aspects of computing a transit time matrix.
    Arguments:
        -network_type: 'walk', 'drive' or 'bike'
        -epsilon: [optional] smooth out the network edges
        -primary_input:
    '''

    def __init__(
            self,
            network_type,
            epsilon=0.05,
            walk_speed=None,
            primary_input=None,
            primary_input_field_mapping=None,
            secondary_input=None,
            secondary_input_field_mapping=None,
            output_type='csv',
            n_best_matches=4,
            read_from_file=None,
            write_to_file=False,
            load_to_mem=True,
            primary_hints=None,
            secondary_hints=None,
            debug=False):

        self.network_type = network_type
        self.epsilon = epsilon
        self.primary_input = primary_input
        self.primary_input_field_mapping = primary_input_field_mapping
        self.secondary_input = secondary_input
        self.secondary_input_field_mapping = secondary_input_field_mapping
        self.sl_data = None
        self.primary_data = None
        self.secondary_data = None
        self.num_nodes = 0
        self.num_edges = 0
        self.nodes = None
        self.edges = None
        self.n_best_matches = n_best_matches
        self.output_type = output_type
        self.read_from_file = read_from_file
        if read_from_file:
            self.write_to_file = False
            self.load_to_mem = False
        else:
            self.write_to_file = write_to_file
            self.load_to_mem = load_to_mem

        self.network_filename = None
        self.output_filename = None
        self.nn_primary_filename = None
        self.nn_secondary_filename = None

        self.primary_hints = primary_hints
        self.secondary_hints = secondary_hints

        self.bbox = []
        self.node_pair_to_speed = {}
        self.speed_limit_dictionary = None

        self.INFINITY = -1
        self.debug = debug
        self.set_logging()
        self._get_thread_limit()
        self._configInterface = ConfigInterface(self.logger)
        self._networkInterface = NetworkInterface(network_type, self.logger)
        self._matrixInterface = MatrixInterface(self.logger)

        assert network_type != 'bike', "bike mode is temporarily disabled"
        assert network_type in [
            'drive', 'walk', 'bike'], "network_type is not one of: ['drive', 'walk', 'bike'] "

        assertionWarning = "Need to (write_to_file and or load_to_mem) or read_from_file"
        assert (write_to_file or load_to_mem or read_from_file), assertionWarning

    def set_logging(self):
        '''
        Set the proper logging and debugging level.
        '''

        if self.debug:
            logging.basicConfig(level=logging.DEBUG)
            self.logger.debug("Running in debug mode")
        else:
            logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)

    def _get_output_filename(self, keyword, extension='csv'):
        '''
        Given a keyword, find an unused filename.
        '''
        if not os.path.exists("data/matrices/"):
            os.makedirs("data/matrices/")
        filename = 'data/matrices/{}_0.{}'.format(keyword, extension)
        counter = 1
        while os.path.isfile(filename):
            filename = 'data/matrices/{}_{}.{}'.format(
                keyword, counter, extension)
            counter += 1

        return filename

    def _load_sl_data(self, sl_filename):
        '''
        Load speed limit data from .csv. Identify street name and speed
        limit columns.
        '''
        if not sl_filename:
            return

        # sanity check & load data
        assertionWarning = "Selected 'drive' cost model but didn't provide speed limit file"
        assert (self.network_type == 'drive' and sl_filename) or (self.network_type !=
                                                                  'drive'), assertionWarning
        assert os.path.exists(
            sl_filename), "Unable to locate provided speed limit file"
        self.sl_data = pd.read_csv(sl_filename)
        source_data_columns = self.sl_data.columns.values

        # extract column names
        street_name = ''
        speed_limit = ''

        print('The variable names in your speed limit data set are:')
        for var in source_data_columns:
            print('> ', var)
        while street_name not in source_data_columns:
            street_name = input('Enter the street name variable name: ')
        while speed_limit not in source_data_columns:
            speed_limit = input('Enter the speed limit variable name: ')

        # clean the data frame
        clean_names = {street_name: 'street_name', speed_limit: 'speed_limit'}
        self.sl_data.rename(columns=clean_names, inplace=True)

        self.sl_data = self.sl_data[['street_name', 'speed_limit']]

    def _validate_csv(self, source_data):

        # Gather input file basic counts
        record_count = source_data.shape[0]
        self.logger.info("record_count: " + str(record_count))
        column_count = source_data.shape[1]
        self.logger.info("column_count: " + str(column_count))
        cell_count = record_count * column_count
        self.logger.info("cell_count: " + str(cell_count))

        # Set total error counter to 0
        invalid_count = 0

        # Gather null counts
        index_null_count = pd.isnull(source_data[[idx]]).sum()[0]
        self.logger.info("index_null_count: " + str(index_null_count))
        invalid_count += index_null_count

        lat_null_count = pd.isnull(source_data[[lat]]).sum()[0]
        self.logger.info("lat_null_count: " + str(lat_null_count))
        invalid_count += lat_null_count

        lon_null_count = pd.isnull(source_data[[lon]]).sum()[0]
        self.logger.info("lon_null_count: " + str(lon_null_count))
        invalid_count += lon_null_count

        # Coerce numeric fields to numeric type and collect invalid values
        source_data[lat] = pd.to_numeric(source_data[lat], errors="coerce")
        invalid_lat = pd.isnull(source_data[[lat]]).sum()[0] - lat_null_count
        self.logger.info("invalid_lat: " + str(invalid_lat))
        invalid_count += invalid_lat

        source_data[lon] = pd.to_numeric(source_data[lon], errors="coerce")
        invalid_lon = pd.isnull(source_data[[lon]]).sum()[0] - lon_null_count
        self.logger.info("invalid_lon: " + str(invalid_lon))
        invalid_count += invalid_lon

        source_data[idx] = pd.to_numeric(source_data[idx], errors="coerce")
        invalid_index = pd.isnull(source_data[[idx]]).sum()[
            0] - index_null_count
        self.logger.info("invalid_index: " + str(invalid_index))
        invalid_count += invalid_index

        # Having coerced to numeric, now check for invalid values
        # check for 0 coordinates
        lat_zero_count = (source_data[[lat]] == 0).sum(axis=1).sum()
        self.logger.info("lat_zero_count: " + str(lat_zero_count))
        invalid_count += lat_zero_count

        lon_zero_count = (source_data[[lon]] == 0).sum(axis=1).sum()
        self.logger.info("lon_zero_count: " + str(lon_zero_count))
        invalid_count += lon_zero_count

        # check for coordinates with values out of bounds
        current_record_count = source_data.shape[0]
        lat_out_of_bounds_count = current_record_count - \
            source_data[lat].between(-180, 180).sum() - invalid_lat - lat_null_count
        self.logger.info(
            "lat_out_of_bounds_count: " +
            str(lat_out_of_bounds_count))
        invalid_count += lat_out_of_bounds_count

        lon_out_of_bounds_count = current_record_count - \
            source_data[lon].between(-180, 180).sum() - invalid_lon - lon_null_count
        self.logger.info(
            "lon_out_of_bounds_count: " +
            str(lon_out_of_bounds_count))
        invalid_count += lon_out_of_bounds_count

        # Drop records

        # Replace 0 and other invalid values in coordinate fields with n/a
        cols = [lat, lon]
        source_data.loc[source_data[lat] > 180, lat] = 0
        source_data.loc[source_data[lat] < -180, lat] = 0
        source_data.loc[source_data[lon] > 180, lon] = 0
        source_data.loc[source_data[lon] < -180, lon] = 0
        source_data[cols] = source_data[cols].replace({0: np.nan})

        pre_drop_indices = source_data.index
        pre_drop = len(source_data)
        source_data.dropna(subset=[xcol, ycol], axis='index', inplace=True)
        post_drop_indices = source_data.index
        post_drop = len(source_data)

        dropped_lines = pre_drop - len(source_data)
        self.logger.info(
            'Total number of rows in the dataset: %d', pre_drop)
        self.logger.info(
            'Complete number of rows for computing the matrix: %d', post_drop)
        self.logger.info(
            "Rows dropped due to missing latitude or longitude values: %d", dropped_lines)

        # Drop records with n/a values in the index/coordinate fields
        source_data.dropna(subset=[idx, lat, lon], axis='index', inplace=True)
        source_data.set_index(idx, inplace=True)

        # Drop records with a duplicate index value, keeping only the first
        source_data = source_data[~source_data.index.duplicated(keep='first')]

    def _parse_csv(self, primary):
        '''
        Load source data from .csv. Identify long, lat and id columns.
        '''
        # decide which input to load
        field_mapping = None

        if primary:
            filename = self.primary_input
            field_mapping = self.primary_input_field_mapping
        else:
            filename = self.secondary_input
            field_mapping = self.secondary_input_field_mapping

        source_data = pd.read_csv(filename)
        source_data_columns = source_data.columns.values

        # extract the column names
        xcol = ''
        ycol = ''
        idx = ''

        # use the column names if we already have them
        try:
            if primary and self.primary_hints:
                xcol = self.primary_hints['xcol']
                ycol = self.primary_hints['ycol']
                idx = self.primary_hints['idx']
            elif not primary and self.secondary_hints:
                xcol = self.secondary_hints['xcol']
                ycol = self.secondary_hints['ycol']
                idx = self.secondary_hints['idx']
        except BaseException:
            pass

        # if the web app is instantiating a TransitMatrix object/calling this code,
        # a field_mapping dictionary should be present
        if field_mapping:
            self.logger.info("Using field mapping provided by web app.")
            xcol = field_mapping["lat"]
            ycol = field_mapping["lon"]
            idx = field_mapping["idx"]

        else:
            print('The variables in your data set are:')
            for var in source_data_columns:
                print('> ', var)
            while xcol not in source_data_columns:
                xcol = input('Enter the latitude coordinate: ')
            while ycol not in source_data_columns:
                ycol = input('Enter the longitude coordinate: ')
            while idx not in source_data_columns:
                idx = input('Enter the index name: ')

        # drop nan lines
        pre_drop_indices = source_data.index
        pre_drop = len(source_data)
        source_data.dropna(subset=[xcol, ycol], axis='index', inplace=True)
        post_drop_indices = source_data.index
        post_drop = len(source_data)

        dropped_lines = pre_drop - len(source_data)
        self.logger.info(
            'Total number of rows in the dataset: %d', pre_drop)
        self.logger.info(
            'Complete number of rows for computing the matrix: %d', post_drop)
        self.logger.info(
            "Rows dropped due to missing latitude or longitude values: %d", dropped_lines)

        # set index and clean
        source_data.set_index(idx, inplace=True)
        source_data.rename(columns={xcol: 'x', ycol: 'y'}, inplace=True)
        source_data.index = source_data.index.map(str)
        if primary:
            self.primary_data = source_data[['x', 'y']]
        else:
            self.secondary_data = source_data[['x', 'y']]

    def _load_inputs(self):
        '''
        Load one input file if the user wants a symmetric
        distance graph, or two for an asymmetric graph.
        '''
        if not os.path.isfile(self.primary_input):
            self.logger.error("Unable to find primary csv.")
            sys.exit()
        if self.secondary_input:
            if not os.path.isfile(self.secondary_input):
                self.logger.error("Unable to find secondary csv.")
                sys.exit()
        
        try:
            self._parse_csv(True)
            if self.secondary_input:
                self._parse_csv(False)

        except BaseException as e:
            self.logger.error(
                "Unable to Load inputs: %s", e)
            sys.exit()


    def _set_output_filename(self, output_filename):
        '''
        Set the output filename to a default value or given.
        '''
        if not output_filename:
            key_phrase = '{}_full_results'.format(self.network_type)
            self.output_filename = self._get_output_filename(key_phrase,
                                                             self.output_type)
        else:
            self.output_filename = output_filename

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

        self.available_threads = no_cores

    def _clean_speed_limits(self):
        '''
        Map road segments to speed limits.
        '''
        edges = self.edges
        sl_file = self.sl_data

        start_time = time.time()

        # clean the table and standardize names
        sl_file.dropna(inplace=True, axis=0, how='any')
        sl_file['street_name'] = sl_file['street_name'].str.upper()
        edges['name'].fillna('PRIVATE', inplace=True)
        edges['name'] = edges['name'].str.upper()
        sl_file = sl_file[sl_file['speed_limit'] > 0]

        # load mappings for easy use
        limits = {}
        for row in sl_file.itertuples():
            limits[row[1]] = row[2]

        # extract edge names/ids from OSM network and assign defaut speed
        STR_NAME = edges.columns.get_loc('name') + 1
        network_streets = {}
        for data in edges.itertuples():
            network_streets[data[STR_NAME]] = 25

        remaining_names = set(limits.keys())

        perfect_match = 0
        great_match = 0
        good_match = 0
        non_match = 0

        # assign default value
        network_streets['PRIVATE'] = self.DEFAULT_DRIVE_SPEED

        # attempt to match edges in OSM to known street names
        # and assign corresponding speed limit
        for name in network_streets.keys():
            if name != 'PRIVATE':
                if name in remaining_names:
                    network_streets[name] = limits[name]
                    perfect_match += 1
                else:
                    best_distance = 0
                    best_match = None
                    for potential_match in remaining_names:
                        distance = jaro_winkler(name, potential_match)
                        if distance >= 0.97:
                            best_distance = distance
                            best_match = potential_match
                            great_match += 1
                            break
                        if distance > best_distance:
                            best_distance = distance
                            best_match = potential_match
                    if best_match and best_distance > 0.9:
                        network_streets[name] = limits[best_match]
                        good_match += 1
                    else:
                        non_match += 1
                        network_streets[name] = 25

        node_pair_to_speed = {}
        for data in edges.itertuples():
            if data[STR_NAME] in network_streets.keys():
                speed = network_streets[data[STR_NAME]]
            else:
                speed = 25
            node_pair_to_speed[(data[0][0], data[0][1])] = speed
            node_pair_to_speed[(data[0][1], data[0][0])] = speed

        self.logger.info(
            '''Matching street network completed in
            {:,.2f} seconds: %d perfect matches, %d near perfect matches,
            %d good matches and %d non matches''',
                time.time() - start_time,
                perfect_match,
                great_match,
                good_match,
                non_match)

        self.node_pair_to_speed = node_pair_to_speed

    def _cost_model(self, distance, sl):
        '''
        Return the edge impedence as specified by the cost model.
        '''
        if self.network_type == 'walk':
            return int(
                (distance /
                 self._configInterface.WALK_CONSTANT) +
                self._configInterface.WALK_NODE_PENALTY)
            # TODO (lmnoel): Implement meters/seconds choice
        elif self.network_type == 'bike':
            return int(
                (distance /
                 self._configInterface.BIKE_CONSTANT) +
                self._configInterface.BIKE_NODE_PENALTY)
            # TODO (lmnoel): Implement meters/seconds choice
        else:
            if sl:
                edge_speed_limit = sl
            else:
                # Logic reading in speed limits from either the user-supplied speed limit file or
                # the default speed limit dictionary should guarantee that the below code will
                # never execute.  Keep in for testing purposes until no longer
                # needed.
                self.logger.warning(
                    'Using default drive speed. Results will be inaccurate')
                edge_speed_limit = self._configInterface.DEFAULT_DRIVE_SPEED
            drive_constant = (edge_speed_limit / self._configInterface.ONE_HOUR) * self._configInterface.ONE_KM
            return int((distance / drive_constant) + self._configInterface.DRIVE_NODE_PENALTY)
            # TODO (lmnoel): Implement meters/seconds choice

    # runs a depth first search from given vertex ve
    # Way to traverse an entire graph: checking for normal weak connection

    def dfs(self, ve):
        size = 0
        stack = [ve]
        while stack:
            v = stack.pop()
            if self.visited[v]:
                continue
            self.visited[v] = True
            size = size + 1

            self.comp_id[v] = self.idd  # gives compnent id to each vertex
            if v in self.rev_adj.keys():
                for nbr in self.rev_adj[v]:
                    if self.visited[nbr] == False:
                        stack.append(nbr)
        if size > self.max_size:
            self.max_size = size
            self.rem_id = self.idd
        return

    def _read_in_speed_limit_dictionary(self):

        dir_path = os.path.dirname(os.path.realpath(__file__))
        speed_limit_dictionary_file = os.path.join(
            dir_path, "speed_limit_dictionary.txt")

        with open(speed_limit_dictionary_file, "r") as f:
            speed_limit_dictionary_text = f.read()
            self.speed_limit_dictionary = ast.literal_eval(
                speed_limit_dictionary_text)


    def _parse_network(self):
        '''
        Cleans the network and generates the csv for the network
        '''

        start_time = time.time()

        DISTANCE = self.edges.columns.get_loc('distance') + 1
        FROM_IDX = self.edges.columns.get_loc('from') + 1
        TO_IDX = self.edges.columns.get_loc('to') + 1
        ONEWAY = self.edges.columns.get_loc('oneway') + 1
        HIGHWAY = self.edges.columns.get_loc('highway') + 1

        # creating adjacency list from osmnet nodes and edges
        self.adj = {}
        self.rev_adj = {}
        self.max_size = 0
        self.rem_id = 0
        self.node = set()
        c = 0
        self.visited = {}
        self.visited2 = {}
        self.comp_id = {}
        for data in self.edges.itertuples():
            so = data[FROM_IDX]
            de = data[TO_IDX]
            if so not in self.adj.keys():
                self.adj[so] = []
            if so not in self.rev_adj.keys():
                self.rev_adj[so] = []
            if de not in self.adj.keys():
                self.adj[de] = []
            if de not in self.rev_adj.keys():
                self.rev_adj[de] = []
            oneway = data[ONEWAY]
            self.adj[so].append(de)
            self.rev_adj[de].append(so)
            self.node.add(so)
            # if it's not driving mode then directionality doesn't matter or if
            # road isn't oneway
            if oneway != 'yes' or self.network_type != 'drive':
                self.adj[de].append(so)
                self.rev_adj[so].append(de)
                self.node.add(de)
            self.visited[so] = False
            self.visited[de] = False
            self.visited2[so] = False
            self.visited2[de] = False

        # Iterative dfs (with finish times)
        # First dfs as part of KOSARAJUs algorithm to give us a stack with
        # finished times.
        time2 = 0
        finish_time_dic = {}
        self.stack2 = []
        for i in self.node:
            if not self.visited2[i]:
                start = i
                # print('source',start)
                q = deque([start])
                while q:
                    v = q.popleft()
                    if not self.visited2[v]:
                        # print(v)
                        self.visited2[v] = True
                    #q = [v] + q
                        q.appendleft(v)
                        if v in self.adj.keys():
                            for w in self.adj[v]:
                                if not self.visited2[w]:
                                    #q = [w[0]] + q
                                    q.appendleft(w)
                    else:
                        if v not in finish_time_dic:
                            finish_time_dic[v] = time2
                            time2 += 1
                            self.stack2.append(v)

        # Second dfs
        # Connected components check using depth first search of graph
        self.idd = 0
        size = 0
        for source in self.node:
            self.visited[source] = False
        c = 0

        while self.stack2:
            source = self.stack2.pop()
            if not self.visited[source]:
                # self.logger.info(source)
                self.dfs(source)
                c = c + 1
                self.idd = self.idd + 1
        self.logger.info("Number of islands initially found: %d", c)
        #print("Removing id:",self.rem_id)
        count = 0
        # Remove disconnected nodes
        for index, row in self.nodes.iterrows():
            if self.comp_id[index] != self.rem_id:
                count = count + 1
                self.nodes = self.nodes.drop(index)
        self.logger.info("Number of disconnected nodes removed: %d", count)

        self.num_nodes = len(self.nodes)
        self.num_edges = len(self.edges)

        # map index name to position
        self.node_index_to_loc = {}
        for i, index_name in enumerate(self.nodes.index):
            self.node_index_to_loc[index_name] = i

        # read in the dictionary of speed limit values used to calculate edge
        # impedences
        self._read_in_speed_limit_dictionary()

        # create a mapping of each node to every other connected node
        # transform them by cost model as well
        with open(self.network_filename, 'w') as csvfile:
            writer = csv.writer(csvfile)
            for data in self.edges.itertuples():
                from_idx = data[FROM_IDX]
                to_idx = data[TO_IDX]
                if self.node_pair_to_speed:
                    impedence = self._cost_model(
                        data[DISTANCE], self.node_pair_to_speed[(from_idx, to_idx)])
                else:
                    highway_tag = data[HIGHWAY]
                    if highway_tag is None or highway_tag not in self.speed_limit_dictionary[
                            "urban"]:
                        highway_tag = "unclassified"
                    impedence = self._cost_model(data[DISTANCE], float(
                        self.speed_limit_dictionary["urban"][highway_tag]))

                oneway = data[ONEWAY]

                # checking if edge connects any of the disconnected nodes. If
                # not, don't consider it.
                if self.comp_id[from_idx] != self.rem_id or self.comp_id[to_idx] != self.rem_id:
                    continue

                writer.writerow([self.node_index_to_loc[from_idx],
                                 self.node_index_to_loc[to_idx], impedence])

                if oneway != 'yes' or self.network_type != 'drive':
                    writer.writerow([self.node_index_to_loc[to_idx],
                                     self.node_index_to_loc[from_idx], impedence])

        self.logger.info(
            "Prepared raw network in {:,.2f} seconds and wrote to: %s",
                time.time() - start_time,
                self.network_filename)

    def _calc_shortest_path(self):
        '''
        Outsources the work of computing the shortest path matrix
        to a C++ module.
        '''

        start_time = time.time()

        # if we are provided a .csv shortest path matrix, load it
        # to memory
        if self.read_from_file:
            try:
                self.tmatrix = pyTMatrix(
                    self.read_from_file,
                    "none",
                    "none",
                    "none",
                    0,
                    0.0,
                    1,
                    0,
                    0,
                    0,
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

        # determine initialization conditions for generating matrix
        if self.network_type == 'walk':
            imp_val = self.WALK_CONSTANT
        elif self.network_type == 'bike':
            imp_val = self.BIKE_CONSTANT
        else:
            imp_val = self.DRIVE_CONSTANT

        outer_node_rows = len(self.primary_data)
        if self.secondary_input:
            outer_node_cols = len(self.secondary_data)
        else:
            outer_node_cols = len(self.primary_data)
        if self.output_type == 'csv':
            nearest_neighbors = 0
        else:
            nearest_neighbors = self.n_best_matches

        if self.write_to_file:
            self.logger.info(
                'Writing to file: %s',
                    self.output_filename)

        self.tmatrix = pyTMatrix(
            self.network_filename,
            self.nn_primary_filename,
            self.nn_secondary_filename,
            self.output_filename,
            self.num_nodes,
            imp_val,
            self.available_threads,
            outer_node_rows,
            outer_node_cols,
            nearest_neighbors,
            write_to_file=self.write_to_file,
            load_to_mem=self.load_to_mem,
            read_from_file=False)

        logger_vars = time.time() - start_time
        self.logger.info(
            'Shortest path matrix computed in {:,.2f} seconds', logger_vars)

    def _match_nn(self, secondary):
        '''
        Maps each the index of each node in the raw distance
        matrix to a tuple
        containing (source_id, distance), where
        source_id is a member of the primary_source
        or secondary_source and distance is the number of meters
        between the (primary/secondary) source and its nearest OSM node.
        '''

        if secondary:
            self.nn_secondary_filename = self._get_output_filename(
                "nn_secondary")
            data = self.secondary_data
            filename = self.nn_secondary_filename
        else:
            self.nn_primary_filename = self._get_output_filename("nn_primary")
            self.nn_secondary_filename = self.nn_primary_filename
            data = self.primary_data
            filename = self.nn_primary_filename

        nodes = self.nodes[['x', 'y']]

        node_indices = nodes.index
        start_time = time.time()
        KM_TO_METERS = 1000

        # make a kd tree in the lat, long dimension
        node_array = pd.DataFrame.as_matrix(nodes)
        kd_tree = scipy.spatial.cKDTree(node_array)

        # map each node in the source/dest data to the nearest
        # corresponding node in the OSM network
        # and write to file
        with open(filename, 'w') as csvfile_w:
            writer = csv.writer(csvfile_w)
            for row in data.itertuples():
                origin_id, origin_y, origin_x = row
                latlong_diff, node_loc = kd_tree.query(
                    [origin_x, origin_y], k=1)
                node_number = node_indices[node_loc]
                distance = vincenty(
                    (origin_y, origin_x), (nodes.loc[node_number].y, nodes.loc[node_number].x)).km

                distance = int(distance * KM_TO_METERS)

                writer.writerow([node_loc, origin_id, distance])

        self.logger.info(
            'Nearest Neighbor matching completed in {:,.2f} seconds', 
                time.time() - start_time)

    @staticmethod
    def _cleanup_artifacts(self, cleanup):
        '''
        Cleanup the files left over from computation.
        '''
        if not cleanup:
            return
        files = os.listdir("data")
        for file in files:
            if 'raw_network' in file or 'nn_primary' in file or 'nn_secondary' in file:
                os.remove('data/matrices/' + file)
        if os.path.isfile('p2p.log'):
            os.remove('p2p.log')
        if os.path.isfile('logs'):
            os.rmdir('logs')
        if os.path.isfile('__pycache__'):
            os.rmdir('__pycache__')
        print("Cleaned up calculation artifacts")

    def process(self, speed_limit_filename=None, output_filename=None,
                cleanup=True):
        '''
        Process the data.
        '''
        start_time = time.time()


        # load from file if given
        if self.read_from_file:
            self.logger.info(
                'Loading data from file: %s',
                    self.read_from_file)
            self._calc_shortest_path()
            return

        self.logger.info(
            "Processing network (%s) in format: %s with epsilon: %f",
            self.network_type,
            self.output_type,
            self.epsilon)

        self._load_inputs()

        self._load_sl_data(speed_limit_filename)

        self._set_output_filename(output_filename)

        self.nodes, self.edges = self._networkInterface.load_network(self.primary_data, 
                                                                     self.secondary_data, 
                                                                     self.secondary_input,
                                                                     self.epsilon)

        self._parse_network()

        self._match_nn(False)
        if self.secondary_input:
            self._match_nn(True)

        self._calc_shortest_path()

        self._cleanup_artifacts(cleanup)

        self.logger.info(
            'All operations completed in {:,.2f} seconds',
                time.time() - start_time)
