import os.path
import logging
import pandas as pd
from geopandas import GeoDataFrame
#from shapely.geometry import Point
#from geopandas import gpd
from spatial_access.ScoreModel import ModelData
import matplotlib.pyplot as pltcat
import matplotlib.patches as mpatches
from matplotlib import mlab
import matplotlib as mpl
import numpy as np
from scipy import stats
import math
import time
import copy
import operator
import re

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def linear_decay_function(time, upper):
    '''
    Linear decay function for distance
    '''

    if time > upper:
        return 0
    else:
        return (upper - time) / upper

def root_decay_function(time, upper):
    '''
    Square root decay function for distance.
    '''
    if time > upper:
        return 0
    else:
        return (1 / math.sqrt(upper) ) * (-time ** 0.5) + 1


def logit_decay_function(time, upper):
    '''
    Logit distance decay function.
    '''
    if time > upper:
        return 0
    else:
        return 1-(1/(math.exp((upper/180)-(.48/60)*(time))+1))
        #return 1-(1/(math.exp((upper/450)-(.3/60)*(time))+1))
        #return 1-(1/(math.exp((upper/300)-(.3/60)*(time))+1))
        #return 1-(1/(math.exp((upper/300)-(.4/60)*(time))+1))
        #return (100-(100/(math.exp((upper/300)-(.0065)*(time))+1))/100)


class CoverageModel(ModelData):
    '''
    Build the Per capita spending model which captures
    the level of spending for low income residents in
    urban enviroments.
    The source_field_mapping and dest_field_mapping parameters are used by the web app client. 
    '''

    def __init__(self, network_type='drive', source_filename=None, source_field_mapping=None,
        dest_filename=None, dest_field_mapping=None, sp_matrix_filename=None, limit_categories=None,
        upper=30):

        super().__init__(network_type, upper)
        self.results = None
        self.dpc = None
        self.res_pop = None
        self.limit_categories = limit_categories
        self.results_initialized = False
        self.dest_percap_target=None
        self.dest_target=None
        self.serv_pop=None
        
        #Standardize limit_categories as a list of unique values
        if limit_categories is None:
            self.limit_categories = []
        else:
            self.limit_categories = list(set(limit_categories))
        
        self.load_sources(source_filename, field_mapping=source_field_mapping)
        self.load_dests(dest_filename, field_mapping=dest_field_mapping)
        self.load_sp_matrix(sp_matrix_filename)
        self.process()

        self.good_to_write = False

    def calculate(self):
        '''
        Calculate the per capita values and served population for each destination record.
        '''
        start_time = time.time()
        
        dest_percap_target = {}
        dest_target={}
        serv_pops={}
        
        for dest_id, source_list in self.dest2source.items():
            
            #check whether to include this destination category the output
            cat = self.get_category(dest_id)
            include = False
            if len(self.limit_categories) == 0:
                include = True
            else:
                if cat in self.limit_categories:
                    include = True
            if include:
                serv_pop = 0
                for item in source_list:
                    source_id, time_val = item
                    #Get population info
                    source_pop = self.get_population(source_id)
                    serv_pop += source_pop
                dest_target = self.get_target(dest_id)
                
                #Calculate Coverage score
                if serv_pop !=0:
                    dest_percap_target[dest_id] = dest_target / serv_pop
                else:
                    dest_percap_target[dest_id]=np.NaN

                #Get population per destination
                serv_pops[dest_id] = serv_pop

        #Convert to DataFrames
        #Get coverage score 
        dpc = pd.DataFrame.from_dict(dest_percap_target, orient='index')
        dpc.rename(columns={ dpc.columns[0]: "coverage" }, inplace=True)
        pd.to_numeric(dpc.coverage)

        #Get population
        res_pops = pd.DataFrame.from_dict(serv_pops, orient='index')
        res_pops.rename(columns={ res_pops.columns[0]: "pop_served" }, inplace=True)
        
        #Output should only contain those rows whose category is in limit_categories
        if len(self.limit_categories) > 0:
            self.dests = self.dests.loc[self.dests['category'].isin(self.limit_categories)]

        self.results = self.dests.join(res_pops)
        self.results = self.results.join(dpc)

        self.good_to_write = True
        self.logger.info("Finished calculating CoverageModel in {:,.2f} seconds".format(time.time() - start_time))

    def _get_aggregate(self, aggregate_type):
        '''
        Build an data frame of the results aggregated
        by community.
        Inputs
            aggregate_type: can be either 'coverage' or
            'population'. If the former, the aggregation
            performed is average. If the latter, the
            aggregation is summation.
        '''
        assert self.good_to_write, 'need to calculate first'

        if aggregate_type == 'category':
            #Fill in NaN only to aggregate the values
            res_0=self.results.drop(columns=['pop_served'])
            res=res_0.fillna(0)
            res = res.groupby(['category']).sum()
        elif aggregate_type == 'coverage':
            res_0=self.results.drop(columns=['pop_served'])
            res=res_0.fillna(0)
            res = res.groupby(['lower_areal_unit']).sum()
        else:
            self.logger.error('Unknown aggregate_type: ({})'.format(aggregate_type))
            return None
        low_area=pd.DataFrame(self.sources.lower_areal_unit.unique())
        low_area.rename(columns={ 0: "lower_areal_unit" }, inplace=True)
        #Making the lower areal unit the index to avoid confusions with embedded Python's index 
        low_area=low_area.set_index('lower_areal_unit')
        return low_area.join(res)


    def agg_area_cat(self):
        res=self.results.drop(columns=['pop_served'])
        res=res.fillna(0)
        res = res.groupby(['lower_areal_unit','category']).sum()
        res=res[['target','coverage']]
        res=res.unstack()

        low_area=pd.DataFrame(self.sources.lower_areal_unit.unique())
        low_area.rename(columns={ 0: "lower_areal_unit" }, inplace=True)
        #Making the lower areal unit the index to avoid confusions with embedded Python's index 
        low_area=low_area.set_index('lower_areal_unit')
        return low_area.join(res)
              
    def write_aggregate(self, aggregate_type, filename=None):
         '''
         Write the aggregate to csv
         '''
         df = self._get_aggregate(aggregate_type)
         if not filename:
             filename = self.get_output_filename_cov('{}_aggregate'.format(aggregate_type))

         df.to_csv(filename)
         self.logger.info('Wrote aggregate to file: {}'.format(filename))

    def write_agg_area_cat(self, filename=None):
         '''
         Write the aggregate2 to csv
         '''
         df = self.agg_area_cat()
         if not filename:
             filename = self.get_output_filename_cov('{}agg_area_cat'.format(self.network_type))

         df.to_csv(filename)
         self.logger.info('Wrote aggregate to file: {}'.format(filename))
            
    def plot_cdf(self, title='Coverage Amount'):
        '''
        Generate a CDF. If limit_categories was specified,
        each category will be given individually. If not, the
        aggregate value will be plotted.
        Inputs
            title: the title of the figure
        '''

        assert self.good_to_write, "must calculate first"

        #blocks with population greater than zero
        cdf_eligible = self.results.loc[self.results['population'] > 0]
        
        #initialize block parameters
        mpl.pyplot.close()
        mpl.pyplot.rcParams['axes.facecolor'] = '#cfcfd1'
        fig, ax = mpl.pyplot.subplots(figsize=(8, 4))
        n_bins = 100

        available_colors = ['black','magenta','lime','red','black','orange','grey','yellow','brown','teal']
        color_keys = []
        if len(self.limit_categories) > 0:
            for category in self.limit_categories:
                x = cdf_eligible[category]
                color = available_colors.pop(0)
                patch = mpatches.Patch(color=color, label=category)
                color_keys.append(patch)
                n, bins, blah = ax.hist(x, n_bins, density=True, histtype='step',
                    cumulative=True, label=category, color=color)
        else:
            x = cdf_eligible['all_categories']
            n, bins, patches = ax.hist(x, n_bins, density=True, histtype='step',
                cumulative=True, label='all_categories')

        if len(self.limit_categories) > 0:
            ax.legend(loc='right',handles=color_keys)
        else:
            ax.legend(loc='right')
        ax.grid(True)
        ax.set_title(title)
        ax.set_xlabel('Per Capita Spending ($)')
        ax.set_ylabel('Percent of Blocks by Value')
        fig_name = self.figure_name()
        mpl.pyplot.savefig(fig_name, dpi=400)
        mpl.pyplot.show()
        self.logger.info('Plot was saved to: {}'.format(fig_name))

        return

    def write_csv(self, filename=None, file_path=None):
        '''
        Write the model data to file.
        '''
        assert self.good_to_write, 'need to calculate first'
        if not filename:
            filename = self.get_output_filename_cov('Coverage_{}'.format(self.network_type))
        self.results.to_csv(filename)


class AccessModel(ModelData):
    '''
    Build the Access model which captures the accessibility of 
    nonprofit services in urban environments.
    The source_field_mapping and dest_field_mapping parameters are used by the web app client. 
    '''

    def __init__(self, network_type='drive', source_filename=None, source_field_mapping=None, 
        dest_filename=None, dest_field_mapping=None, sp_matrix_filename=None, decay_function='linear',
        limit_categories=None, upper=30):

        super().__init__(network_type, upper)
        self.results = None

        if decay_function == 'linear':
            self.decay_function = linear_decay_function
        elif decay_function == 'root':
            self.decay_function = root_decay_function
        elif decay_function == 'logit':
            self.decay_function = logit_decay_function
        else:
            self.logger.error('Unrecognized decay function. Must be one of: linear, root or logit')

        self.load_sources(source_filename, field_mapping=source_field_mapping)
        self.load_dests(dest_filename, field_mapping=dest_field_mapping)
        self.load_sp_matrix(sp_matrix_filename)
        
        self.process()

        #Standardize limit_categories as a list of unique values
        if limit_categories is None:
            self.limit_categories = []
        else:
            self.limit_categories = list(set(limit_categories))
        
        self.good_to_write = False
        self.custom_threshold = None


    def calculate(self, custom_threshold=40, normalize=True, 
        custom_weight_dict=None, largest_weights_first=True, subset_provided=False):
        '''
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
        '''

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
                '''
                Sort the destination list so the weight_dict[cat].pop
                will take the nearest neighbor first.
                '''
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

    def _create_field_names(self, category_subset):

        #Derive column names for this category subset

        #Derive column name suffixes
        if len(category_subset) == 0:   #case where no subset is chosen, output measure is for aggregate of all categories, no suffix necessary
            suffix = ""
        elif len(category_subset) > 1:  #suffix for the aggregate measure when subsets are chosen  
            suffix = "_agg"
        else:
            #Some categoriy names may contain characters that can't be used as a field name.  Replace with underscores.
            suffix = "_" + self._replace_symbols(category_subset[0])[:8]
        
        #Assemble final column names
        #Add a counter to the column name if field names end up being the same (through truncation, mapping of symbols to underscores)
        access_column_base_name = "access" + suffix
        access_column_name = access_column_base_name
        counter = 1
        add_subscript = False   
        if self.results is not None:
            while access_column_name in self.results.columns.values:
                add_subscript = True
                access_column_name = '{}_{}'.format(access_column_base_name, counter)
                counter += 1

        if add_subscript:
            access_cat_column_name = '{}{}_{}'.format("access_cat", suffix, counter)
            access_sd_column_name = '{}{}_{}'.format("access_sd", suffix, counter)
            access_time_column_name = '{}{}_{}'.format("access_time", suffix, counter)
        else:
            access_cat_column_name = '{}{}'.format("access_cat", suffix)
            access_sd_column_name = '{}{}'.format("access_sd", suffix)
            access_time_column_name = '{}{}'.format("access_time", suffix)

        return access_column_name, access_sd_column_name, access_cat_column_name, access_time_column_name

    def _replace_symbols(self, txt):
        
        # Replace all non-word characters (everything except numbers, letters and underscores) with underscores
        txt = re.sub(r"[^\w]", '_', txt)
        return txt

    def write_csv(self, filename=None):
        '''
        Write the model data to file.
        '''
        assert self.good_to_write, 'need to calculate first'
        if not filename:
            filename = self.get_output_filename_access('Access_{}'.format(self.network_type))
        self.results.to_csv(filename)

    def _get_aggregate(self, aggregate_type):
        '''
        Build an data frame of the results aggregated
        by community.
        Inputs
            aggregate_type: can be either 'access' or
            'population'. If the former, the aggregation
            performed is average. If the latter, the
            aggregation is summation.
        '''
        assert self.good_to_write, 'need to calculate first'
        
        if aggregate_type == 'access': 
            res_0=self.results
            res=res_0.fillna(0)
            #The .mean() disregards the NaN values
            res = res.groupby(['lower_areal_unit']).mean()
            #Can add any fields from AccessModel
            res = res[['access']]
        else:
            self.logger.error('Unknown aggregate_type: ({})'.format(aggregate_type))
            return None
            
        low_area=pd.DataFrame(self.sources.lower_areal_unit.unique())
        low_area.rename(columns={ 0: "lower_areal_unit" }, inplace=True)
        #Making the lower areal unit the index to avoid confusions with embedded Python's index 
        low_area=low_area.set_index('lower_areal_unit')
        return low_area.join(res)

        
    def write_aggregate(self, aggregate_type, filename=None):
        '''
        Write the aggregate to csv
        '''
        df = self._get_aggregate(aggregate_type)
        if not filename:
            filename = self.get_output_filename_access('{}_aggregate'.format(aggregate_type))

        df.to_csv(filename)
        self.logger.info('Wrote aggregate to file: {}'.format(filename))
        

    def plot_cdf(self, title='CDF Access Score'):
        '''
        Generate a CDF of the aggregate Access score.
        Inputs
            title: the title of the figure
        '''
        assert self.good_to_write, "must calculate first"
        mpl.pyplot.rcParams['axes.facecolor'] = '#cfcfd1'
        x = self.results.loc[self.results['population'] > 0]['access']
       
        mpl.pyplot.close()
        fig, ax = mpl.pyplot.subplots(figsize=(8, 4))
        n_bins = 100
        n, bins, patches = ax.hist(x, n_bins, density=True, histtype='step',
                           cumulative=True, label='All Categories of Spending')

        ax.grid(True)
        ax.legend(loc='right')
        ax.set_title(title)
        ax.set_xlabel('Access Score')
        ax.set_ylabel('Percent of Areal Units by Value')
        fig_name = self.figure_name()
        mpl.pyplot.savefig(fig_name, dpi=400)
        mpl.pyplot.show()
        self.logger.info('Plot was saved to: {}'.format(fig_name))

        return


class TTMetrics(ModelData):
    '''
    Build the Access model which captures the accessibility of 
    nonprofit services in urban environments.
    '''

    def __init__(self, network_type='walk', source_filename=None, 
        dest_filename=None, sp_matrix_filename=None, decay_function='linear',
        limit_categories=None, upper=30):

        super().__init__(network_type, upper)
        self.results = None
        self.limit_categories = limit_categories
        
        #Standardize limit_categories as a list of unique values
        if limit_categories is None:
            self.limit_categories = []
        else:
            self.limit_categories = list(set(limit_categories))
        
        self.load_sources(source_filename)
        self.load_dests(dest_filename)
        self.load_sp_matrix(sp_matrix_filename)
        self.process()

        self.good_to_write = False
        self.custom_threshold = None
    
    def calculate(self):

        #Stores no of destination wthin upper for a given source and category
        # self.n_dests_in_range ={}
        # for s, val in self.source2dest.items():
        #     self.n_dests_in_range[s] = {}

        #     for catt in self.category_set:
        #         self.n_dests_in_range[s][catt] = 0
        #     for d in val:
        #         cat = self.get_category(d[0])
        #         if d[1] >= 0:
        #             self.n_dests_in_range[s][cat] +=1

        #Create count of destinations within range
        for s, val in self.source2dest.items():
            self.n_dests_in_range[s] = {}
            no_cat = 0
            if self.category_set == set(["CAT_UNDEFINED"]):
                self.n_dests_in_range[s]= len([item for item in val if item])

            else:
                for catt in self.category_set:
                    self.n_dests_in_range[s][catt] = 0
                for d in val:
                    cat = self.get_category(d[0])
                    if d[1] >= 0:
                        self.n_dests_in_range[s][cat] +=1

        #Create nearest neighbour to given source of a given category
        self.near_nbr = {}
        for s,val in self.dicto.items():
            self.near_nbr[s] = {}
            if self.category_set == set(["CAT_UNDEFINED"]):
                self.near_nbr[s] = val[0][1]
            else:
                for d in val:
                    cat = self.get_category(d[0])
                    if cat not in self.near_nbr[s] and d[1]>0:
                        self.near_nbr[s][cat] = d[1]
                        no_cat +=1
                        if(no_cat == len(self.category_set)):
                            break

        # #Stores nearest neighbour to given source of a given category
        # self.near_nbr = {}
        # for s,val in self.dicto.items():
        #     self.near_nbr[s] = {}
        #     no_cat = 0
        #     for d in val:
        #         cat = self.get_category(d[0])
        #         if cat not in self.near_nbr[s] and d[1]>0:
        #             self.near_nbr[s][cat] = d[1]
        #             no_cat +=1
        #             if(no_cat == len(self.category_set)):
        #                 break

        self.n_dests_in_range = pd.DataFrame.from_dict(self.n_dests_in_range, orient='index')
        self.near_nbr = pd.DataFrame.from_dict(self.near_nbr, orient='index')


        # self.n_dests_in_range.fillna(0,inplace=True)
        # #self.n_dests_in_range=self.n_dests_in_range.replace(-9999, 0)
        # for keyy, negs in self.neg_val.items():
        #     for j in self.category_set:
        #         self.near_nbr.at[keyy,j] = -999
        #         self.n_dests_in_range.at[keyy,j] = -999

        # self.n_dests_in_range=self.n_dests_in_range.replace(-9999, np.nan)
        # self.near_nbr=self.near_nbr.replace(-999, np.nan)

        if self.category_set == set(["CAT_UNDEFINED"]):
            self.n_dests_in_range.rename(columns={ self.n_dests_in_range.columns[0]: 'n_dests' }, inplace=True)
            self.n_dests_in_range=self.n_dests_in_range['n_dests']
            self.n_dests_in_range=pd.DataFrame(self.n_dests_in_range)

            #self.near_nbr = pd.DataFrame.from_dict(self.near_nbr, orient='index')
            self.near_nbr.rename(columns={ self.near_nbr.columns[0]: 'nn' }, inplace=True)
            self.near_nbr=self.near_nbr['nn']
            self.near_nbr=pd.DataFrame(self.near_nbr)

        
    def plot_nearest_providers(self, limit_categories=None, 
        title='Closest Point CDF', n_bins=500, resolution='block'):
        '''
        Plot a cdf of travel times to the closest provider
        for each category.
        '''

        assert resolution in ['block', 'population'], 'must use block or resolution'
        #assert resolution != 'population', 'this feature is a Work in Progress'
        
        figure_name = self.figure_name()

        
        #initialize block parameters
        mpl.pyplot.close()
        mpl.pyplot.rcParams['axes.facecolor'] = '#cfcfd1'
        fig, ax = mpl.pyplot.subplots(figsize=(8, 4))

        available_colors = ['black','magenta','lime','red','black','orange','grey','yellow','brown','teal']
        color_keys = []
        if len(self.limit_categories) > 0:
            for category in self.limit_categories:
                self.near_nbr[category][self.near_nbr[category] > self.upper] = self.upper
                x = self.near_nbr[category]
                #Drop any NaNs to avoid error in plotting 
                x=x.dropna()
                color = available_colors.pop(0)
                patch = mpatches.Patch(color=color, label=category)
                color_keys.append(patch)
                if resolution == 'population':
                    res = {}
                    for block_id, time_val in x.iteritems():
                        block_pop = self.get_population(block_id)
                        if block_pop <= 0:
                            continue
                        for i in range(block_pop):
                            temp_id = '{}_{}'.format(block_id, i)
                            res[temp_id] = time_val
                    res = pd.Series(data=res)
                    n, bins, blah = ax.hist(res, n_bins, density=True, histtype='step',
                    cumulative=True, label=category, color=color)
                else:
                    n, bins, blah = ax.hist(x, n_bins, density=True, histtype='step',
                    cumulative=True, label=category, color=color)

        else:
            for category in self.category_set:
                self.near_nbr[category][self.near_nbr[category] > self.upper] = self.upper
                x = self.near_nbr[category]
                #Drop any NaNs to avoid error in plotting 
                x=x.dropna()
                color = available_colors.pop(0)
                patch = mpatches.Patch(color=color, label=category)
                color_keys.append(patch)
                if resolution == 'population':
                    res = {}
                    for block_id, time_val in x.iteritems():
                        #block_pop = self.get_population(block_id)
                        block_pop = self.sources.loc[int(float(block_id)), 'population']
                        if block_pop <= 0:
                            continue
                        for i in range(block_pop):
                            temp_id = '{}_{}'.format(block_id, i)
                            res[temp_id] = time_val
                    res = pd.Series(data=res)
                    n, bins, blah = ax.hist(res, n_bins, density=True, histtype='step',
                    cumulative=True, label=category, color=color)
                else:
                    n, bins, blah = ax.hist(x, n_bins, density=True, histtype='step',
                    cumulative=True, label=category, color=color)

        if len(self.limit_categories) > 0:
            ax.legend(loc='best',handles=color_keys)
        else:
            ax.legend(loc='best', handles=color_keys)
        ax.grid(True)
        ax.set_title(title)
        ax.set_xlabel('Time in seconds')
        ax.set_ylabel('Percent of {} Within Range'.format(resolution))
        fig_name = self.figure_name()
        mpl.pyplot.savefig(fig_name, dpi=400)
        mpl.pyplot.show()
        self.logger.info('Plot was saved to: {}'.format(fig_name))

