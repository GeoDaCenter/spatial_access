import pandas as pd
from spatial_access.ScoreModel import ModelData
from spatial_access.SpatialAccessExceptions import UnrecognizedDecayFunctionException
from spatial_access.SpatialAccessExceptions import UnrecognizedCategoriesException


import numpy as np
import math
import time
import copy
import operator


def linear_decay_function(time, upper):
    """
    Linear decay function for distance
    """

    if time > upper:
        return 0
    else:
        return (upper - time) / upper


def root_decay_function(time, upper):
    """
    Square root decay function for distance.
    """
    if time > upper:
        return 0
    else:
        return (1 / math.sqrt(upper) ) * (-time ** 0.5) + 1


def logit_decay_function(time, upper):
    """
    Logit distance decay function.
    """
    if time > upper:
        return 0
    else:
        return 1-(1/(math.exp((upper/180)-(.48/60)*(time))+1))


class Coverage:
    """
    Build the CoverageScore which captures
    the level of spending for low income residents in
    urban environments.
    """

    def __init__(self, network_type, sources_filename=None, source_column_names=None,
                 destinations_filename=None, dest_column_names=None, sp_matrix_filename=None,
                 upper_threshold=1800, categories=None):

        self.model_data = ModelData(network_type=network_type,
                                    sources_filename=sources_filename,
                                    destinations_filename=destinations_filename,
                                    source_column_names=source_column_names,
                                    dest_column_names=dest_column_names,
                                    upper_threshold=upper_threshold)

        self.model_data.load_sp_matrix(sp_matrix_filename)
        self.model_results = None
        self.categories = categories
        if self.categories is not None:
            unrecognized_categories = set(categories) - self.model_data.get_all_categories()
            if len(unrecognized_categories) > 0:
                raise UnrecognizedCategoriesException(unrecognized_categories)
        else:
            self.categories = ['all_categories']

    def calculate(self):
        """
        Calculate the per-capita values and served population for each destination record.
        """

        results = {}
        for dest_id in self.model_data.get_all_dest_ids():
            population_in_range = self.model_data.get_population_in_range(dest_id)
            percapita_spending = self.model_data.get_target(dest_id) / population_in_range
            results[dest_id] = [population_in_range, percapita_spending]

        self.model_results = pd.DataFrame.from_dict(results, orient='index',
                                                    columns=['service_pop','percap_spending'])


class AccessPop:
    """
    Build the AccessPop which quantifies
    the per-resident spending for given categories.
    """

    def __init__(self, network_type, sources_filename=None, source_column_names=None,
                 destinations_filename=None, dest_column_names=None, sp_matrix_filename=None,
                 upper_threshold=1800, categories=None):

        self.model_data = ModelData(network_type=network_type,
                                    sources_filename=sources_filename,
                                    destinations_filename=destinations_filename,
                                    source_column_names=source_column_names,
                                    dest_column_names=dest_column_names,
                                    upper_threshold=upper_threshold)

        self.model_data.load_sp_matrix(sp_matrix_filename)
        self.model_results = None
        self.model_data.calculate_sources_in_range()
        self.model_data.calculate_dests_in_range()
        self.categories = categories
        if self.categories is not None:
            unrecognized_categories = set(categories) - self.model_data.get_all_categories()
            if len(unrecognized_categories) > 0:
                raise UnrecognizedCategoriesException(unrecognized_categories)
        else:
            self.categories = ['all_categories']

    def calculate(self):
        """
        Calculate the per-capita values and served population for each destination record.
        """

        # initialize results as {source_id: []}
        results = {}
        num_categories = len(self.categories)
        for source_id in self.model_data.get_all_source_ids():
            results[source_id] = [0] * num_categories

        # map category to index in results and generate column names
        category_to_index = {}
        column_names = []
        for i, category in enumerate(self.categories):
            category_to_index[category] = i
            column_names.append('access_pop_' + category)
        for category in self.categories:
            for dest_id in self.model_data.get_ids_for_category(category):
                population_in_range = self.model_data.get_population_in_range(dest_id)
                if population_in_range > 0:
                    contribution_to_spending = self.model_data.get_target(dest_id) / population_in_range
                    for source_id in self.model_data.get_sources_in_range_of_dest(dest_id):
                        results[source_id][category_to_index[category]] += contribution_to_spending

        self.model_results = pd.DataFrame.from_dict(results, orient='index',
                                                    columns=column_names)


class AccessTime:
    """
    Measures the closest destination for each source per category.
    """

    def __init__(self, network_type, sources_filename=None, source_column_names=None,
                 destinations_filename=None, dest_column_names=None, sp_matrix_filename=None,
                 categories=None):

        self.model_data = ModelData(network_type=network_type,
                                    sources_filename=sources_filename,
                                    destinations_filename=destinations_filename,
                                    source_column_names=source_column_names,
                                    dest_column_names=dest_column_names,
                                    upper_threshold=None)

        self.model_data.load_sp_matrix(sp_matrix_filename)
        self.model_results = None
        self.categories = categories
        if self.categories is not None:
            unrecognized_categories = set(categories) - self.model_data.get_all_categories()
            if len(unrecognized_categories) > 0:
                raise UnrecognizedCategoriesException(unrecognized_categories)
        else:
            self.categories = ['all_categories']

    def calculate(self):
        """
        Calculate the closest destination for each source per category.
        """

        results = {}
        column_names = ['time_to_nearest_' + category for category in self.categories]
        for source_id in self.model_data.get_ids_for_category(category):
            results[source_id] = []
            for category in self.categories:
                time_to_nearest_neighbor = self.model_data.time_to_nearest_dest(source_id, category)
                results[source_id].append(time_to_nearest_neighbor)

        self.model_results = pd.DataFrame.from_dict(results, orient='index',
                                                    columns=column_names)


class AccessCount:
    """
    Measures the number of destinations in range
    for each source per category.
    """

    def __init__(self, network_type, sources_filename=None, source_column_names=None,
                 destinations_filename=None, dest_column_names=None, sp_matrix_filename=None,
                 upper_threshold=1800, categories=None):

        self.model_data = ModelData(network_type=network_type,
                                    sources_filename=sources_filename,
                                    destinations_filename=destinations_filename,
                                    source_column_names=source_column_names,
                                    dest_column_names=dest_column_names,
                                    upper_threshold=upper_threshold)

        self.model_data.load_sp_matrix(sp_matrix_filename)
        self.model_results = None
        self.categories = categories
        if self.categories is not None:
            unrecognized_categories = set(categories) - self.model_data.get_all_categories()
            if len(unrecognized_categories) > 0:
                raise UnrecognizedCategoriesException(unrecognized_categories)
        else:
            self.categories = ['all_categories']

    def calculate(self):
        """
        Calculate the closest destination for each source per category.
        """

        results = {}
        column_names = ['count_in_range_' + category for category in self.categories]
        for source_id in self.model_data.get_ids_for_category(category):
            counts = self.model_data.count_dests_in_range_by_categories(source_id, self.categories)
            results[source_id] = [counts]

        self.model_results = pd.DataFrame.from_dict(results, orient='index',
                                                    columns=column_names)

class AccessModel():
    """
    Build the Access model which captures the accessibility of 
    nonprofit services in urban environments.
    """

    def __init__(self, network_type, sources_filename=None, source_column_names=None,
                 destinations_filename=None, dest_column_names=None, sp_matrix_filename=None,
                 upper_threshold=1800, categories=None, decay_function='linear'):

        if decay_function == 'linear':
            self.decay_function = linear_decay_function
        elif decay_function == 'root':
            self.decay_function = root_decay_function
        elif decay_function == 'logit':
            self.decay_function = logit_decay_function
        else:
            raise UnrecognizedDecayFunctionException(decay_function)

        self.model_data = ModelData(network_type=network_type,
                                    sources_filename=sources_filename,
                                    destinations_filename=destinations_filename,
                                    source_column_names=source_column_names,
                                    dest_column_names=dest_column_names,
                                    upper_threshold=upper_threshold)

        self.model_data.load_sp_matrix(sp_matrix_filename)

        self.model_results = {}
        self.categories = categories

        if self.categories is not None:
            unrecognized_categories = set(categories) - self.model_data.get_all_categories()
            if len(unrecognized_categories) > 0:
                raise UnrecognizedCategoriesException(unrecognized_categories)

    def calculate(self, custom_threshold=40, normalize=True, 
        custom_weight_dict=None, largest_weights_first=True, subset_provided=False):
        """
        Calculate the Access score for each block
        from the vendors within the specified range.
        Inputs:
            custom_threshold- integer or float, optional. Results will contain
            a column showing percent of population with score greater
            than or equal to this value
            normalize-Boolean, optional (defaults to true). If true,
            final scores will be normalized on a range from 0-100.
            custom_weight_dict-a dictionary mapping strings of category names
            to a list of integer or float weights.  If a key 'Default' is found, the
            weight list will be used for any categories without a key in the dictionary.
            largest_weights_first: boolean, if using custom_weight_dict. If True,
            sort the weight arrays such that largest will be used first. IF false,
            do the opposite.
            by_category: if True, calculate() returns access values for each 
            provided destination category individually as well as for the aggregate
            of the selected categories.  if False, just the aggregate access value
            for facilities matching the destination categories is output.
        """

        start_time = time.time()
        self.custom_threshold = custom_threshold
                
        DIMINISH_WEIGHTS =  [1,1,1,1,1,1,1,1,1,1]
        
        #Construct a list of category subsets for which access should be calculated.
        #First append the full list of categories chosen (so the aggregate measure for those categories is also calculated)
        #If only a single category was chosen, there's no need to append the full list, since the aggregate will just be that single category.
        category_list = [self.limit_categories] #If no categories chosen, we end up with [[]]
        if subset_provided and len(self.limit_categories) > 1:
            for category in self.limit_categories:
                category_list.append([category])

        #sort the user's input arrays, such that the highest
        #weight will be used first and the lowest weight will be
        #used last
        if custom_weight_dict is not None:

            for key in custom_weight_dict.keys():
                custom_weight_dict[key].sort(reverse= not largest_weights_first)

        #Calculate measures for each category subset
        #Note that if no limit_categories input is specified, category_list will contain one empty list
        for category_subset in category_list:
            print("category_subset: " + str(category_subset))
            results = {}
            results_cat = {}
            results_time = {}   #Holds the time to the nearest facility for the current category subset

            access_column_name, access_sd_column_name, access_cat_column_name, access_time_column_name = self._create_field_names(category_subset)

            #For each origin...
            for source_id, dest_list in self.source2dest.items():
                if custom_weight_dict is not None:
                    weight_dict = copy.deepcopy(custom_weight_dict)
                else:
                    weight_dict = {}
                access = 0
                access_cat = 0
                shortest_time = 9999999
                """
                Sort the destination list so the weight_dict[cat].pop
                will take the nearest neighbor first.
                """
                dest_list.sort(key=operator.itemgetter(1))

                #Iterate through each destination 
                for item in dest_list:
                    dest_id, time_val = item
                    cat = self.get_category(dest_id)
                    
                    #Skip this dest if not in the current category_subset.
                    #Let the record be included if no subset was chosen (i.e., category_subset = [], length is 0)
                    if cat not in category_subset and len(category_subset) > 0:
                        continue

                    if time_val < shortest_time:
                        shortest_time = time_val
                    distance_weight = self.decay_function(time_val, self.upper)
                    
                    #if we haven't encountered this category for this source,
                    #create a new list of weights
                    #If the user has passed in a list with key "Default", use that as the 
                    #default set of weights.  Otherwise use DIMINISH_WEIGHTS[:].
                    if cat not in weight_dict.keys():
                        if "Default" in weight_dict.keys():
                            weight_dict[cat] = weight_dict["Default"]
                        else:
                            weight_dict[cat] = DIMINISH_WEIGHTS[:]
                  
                    #if we have encountered this category for this source,
                    #take the next highest weight (0 if all weights have)
                    #already been used
                    if len(weight_dict[cat]) > 0:
                        diminish_cat_weight = weight_dict[cat].pop()
                        dw = distance_weight * diminish_cat_weight
                    else:
                        diminish_cat_weight = 0
                        dw = 0
                    #In order to check that the score is calculated correctly:
                    #print(distance_weight,diminish_cat_weight,dw,cat)
                    #Access score for weights and distance decay
                    access += dw
                    #Count of weights by areal unit
                    access_cat += diminish_cat_weight 

                results[source_id] = access
                results_cat[source_id] = access_cat
                if shortest_time != 9999999:
                    results_time[source_id] = shortest_time/60
                

            #convert to DataFrame
            res = pd.DataFrame.from_dict(results, orient='index')
            res.rename(columns={ res.columns[0]: access_column_name }, inplace=True)
            
            # res_cat = pd.DataFrame.from_dict(results_cat, orient='index')
            # res_cat.rename(columns={ res_cat.columns[0]: access_cat_column_name }, inplace=True)

            shortest_time_df = pd.DataFrame.from_dict(results_time, orient='index')
            shortest_time_df.rename(columns={ shortest_time_df.columns[0]: access_time_column_name }, inplace=True)

            #join with source data
            #Joins the missing values created from the units exceeding the 'upper' threshold. Later converts them to 0.
            if self.results is None:
                self.results = self.sources.join(res)
            else: 
                self.results = self.results.join(res)

            if normalize:
                num = self.results[access_column_name] - self.results[access_column_name].min()
                denom = self.results[access_column_name].max() - self.results[access_column_name].min()
                self.results[access_sd_column_name] = (num / denom) * 100

            # self.results = self.results.join(res_cat)
            self.results = self.results.join(shortest_time_df)

        #Replace the null values with zeros (values above upper)
        self.results.fillna(0, inplace=True)

        #Find list within matrix with negative values
        #When constructing the matrix with p2p, the negative values (-1) are the edges on the border of the bounding box.
        #So we make those values NA
        for keyy, negs in self.neg_val.items():
            for j in self.results.keys():
                self.results.at[keyy, j] = -9999

        self.results = self.results.replace(-9999, np.nan)
        # self.results = self.results.replace(9999999, np.nan)
        
        self.good_to_write = True
        self.logger.info("Finished calculating Access Model in {:,.2f} seconds".format(time.time() - start_time))
