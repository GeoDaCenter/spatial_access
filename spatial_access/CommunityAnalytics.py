import pandas as pd
from spatial_access.ScoreModel import ModelData
from spatial_access.SpatialAccessExceptions import UnrecognizedDecayFunctionException
from spatial_access.SpatialAccessExceptions import UnrecognizedCategoriesException
from spatial_access.SpatialAccessExceptions import IncompleteCategoryDictException
from spatial_access.SpatialAccessExceptions import ModelNotAggregatedException

import math


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
    Build Coverage which captures
    the level of spending for low income residents in
    urban environments.
    """

    def __init__(self, network_type, sources_filename=None, source_column_names=None,
                 destinations_filename=None, dest_column_names=None, sp_matrix_filename=None,
                 categories=None):

        self.model_data = ModelData(network_type=network_type,
                                    sources_filename=sources_filename,
                                    destinations_filename=destinations_filename,
                                    source_column_names=source_column_names,
                                    dest_column_names=dest_column_names)

        self.model_data.load_sp_matrix(sp_matrix_filename)
        self.model_results = None
        self.aggregated_results = None
        self.categories = categories
        if self.categories is not None:
            unrecognized_categories = set(categories) - self.model_data.get_all_categories()
            if len(unrecognized_categories) > 0:
                raise UnrecognizedCategoriesException(unrecognized_categories)
        else:
            self.categories = ['all_categories']

    def calculate(self, upper_threshold):
        """
        Calculate the per-capita values and served population for each destination record.
        """
        self.model_data.calculate_sources_in_range(upper_threshold)
        results = {}
        for category in self.categories:
            for dest_id in self.model_data.get_ids_for_category(category):
                population_in_range = self.model_data.get_population_in_range(dest_id, upper_threshold)
                if population_in_range > 0:
                    percapita_spending = self.model_data.get_target(dest_id) / population_in_range
                else:
                    percapita_spending = 0
                results[dest_id] = [population_in_range, percapita_spending, category]

        self.model_results = pd.DataFrame.from_dict(results, orient='index',
                                                    columns=['service_pop',
                                                             'percap_spending',
                                                             'category'])


    def aggregate(self, shapefile='data/chicago_boundaries/chicago_boundaries.shp',
                        spatial_index='community', projection='epsg:4326'):
        """
        Aggregate results by community area
        """
        aggregation_args = {}
        for column in self.model_results.columns:
            if 'service_pop' in column:
                aggregation_args[column] = 'sum'
            elif 'percap_spending' in column:
                aggregation_args[column] = 'mean'

        self.aggregated_results = self.model_data.build_aggregate(model_results=self.model_results,
                                                                  is_source=False,
                                                                  aggregation_args=aggregation_args,
                                                                  shapefile=shapefile,
                                                                  spatial_index=spatial_index,
                                                                  projection=projection)

    def plot_cdf(self, type, title='title', xlabel='xlabel', ylabel='ylabel'):
        """
        Plot cdf of results
        """
        self.model_data.plot_cdf(model_results=self.model_results,
                                 plot_type=type,
                                 xlabel=xlabel,
                                 ylabel=ylabel,
                                 title=title,
                                 is_source=False)

    # ToDO test this
    def plot_chloropleth(self, column, title='title', color_map='greens',
                         projection='epsg:4326'):
        """
        Plot chloropleth of results
        """
        if self.aggregated_results is None:
            raise ModelNotAggregatedException()
        self.model_data.plot_choropleth(model_results=self.aggregated_results,
                                 column=column,
                                 title=title,
                                color_map=color_map,
                                categories=self.categories,
                                        projection=projection)

class AccessPop:
    """
    Build the AccessPop which quantifies
    the per-resident spending for given categories.
    """

    def __init__(self, network_type, sources_filename=None, source_column_names=None,
                 destinations_filename=None, dest_column_names=None, sp_matrix_filename=None,
                 categories=None):

        self.model_data = ModelData(network_type=network_type,
                                    sources_filename=sources_filename,
                                    destinations_filename=destinations_filename,
                                    source_column_names=source_column_names,
                                    dest_column_names=dest_column_names)

        self.model_data.load_sp_matrix(sp_matrix_filename)
        self.model_results = None
        self.aggregated_results = None
        self.categories = categories
        if self.categories is not None:
            unrecognized_categories = set(categories) - self.model_data.get_all_categories()
            if len(unrecognized_categories) > 0:
                raise UnrecognizedCategoriesException(unrecognized_categories)
        else:
            self.categories = ['all_categories']

    def calculate(self, upper_threshold):
        """
        Calculate the per-capita spending for each source record.
        """
        self.model_data.calculate_sources_in_range(upper_threshold)
        self.model_data.calculate_dests_in_range(upper_threshold)

        # initialize results as {source_id: []}
        results = {}
        num_categories = len(self.categories)
        for source_id in self.model_data.get_all_source_ids():
            results[source_id] = [0, 0] * num_categories

        # map category to index in results and generate column names
        column_name_to_index = {}
        column_names = []
        index = 0
        for category in self.categories:
            column_names.append('percap_spend_' + category)
            column_names.append('total_spend_' + category)
            column_name_to_index[category] = (index, index + 1)
            index += 2

        for category in self.categories:
            for dest_id in self.model_data.get_ids_for_category(category):
                population_in_range = self.model_data.get_population_in_range(dest_id, upper_threshold)
                if population_in_range > 0:
                    contribution_to_spending = self.model_data.get_target(dest_id) / population_in_range
                    for source_id in self.model_data.get_sources_in_range_of_dest(dest_id):
                        source_population = self.model_data.get_population(source_id)
                        if source_population > 0:
                            pc_col_index, t_col_index = column_name_to_index[category]
                            results[source_id][pc_col_index] += contribution_to_spending
                            results[source_id][t_col_index] += contribution_to_spending * source_population
        self.model_results = pd.DataFrame.from_dict(results, orient='index',
                                                    columns=column_names)

    def aggregate(self, shapefile='data/chicago_boundaries/chicago_boundaries.shp',
                        spatial_index='community', projection='epsg:4326'):
        """
        Aggregate results by community area
        """
        aggregation_args = {}
        for column in self.model_results.columns:
            if 'percap_spend' in column:
                aggregation_args[column] = 'mean'
            elif 'total_spend' in column:
                aggregation_args[column] = 'sum'

        self.aggregated_results = self.model_data.build_aggregate(model_results=self.model_results,
                                                                  is_source=False,
                                                                  aggregation_args=aggregation_args,
                                                                  shapefile=shapefile,
                                                                  spatial_index=spatial_index,
                                                                  projection=projection)

    def plot_cdf(self, type, title='title', xlabel='xlabel', ylabel='ylabel'):
        """
        Plot cdf of results
        """
        self.model_data.plot_cdf(model_results=self.model_results,
                                 plot_type=type,
                                 xlabel=xlabel,
                                 ylabel=ylabel,
                                 title=title,
                                 is_source=True)

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
                                    dest_column_names=dest_column_names)

        self.model_data.load_sp_matrix(sp_matrix_filename)
        self.model_results = None
        self.aggregated_results = None
        self.categories = categories
        if self.categories is not None:
            unrecognized_categories = set(categories) - self.model_data.get_all_categories()
            if len(unrecognized_categories) > 0:
                raise UnrecognizedCategoriesException(unrecognized_categories)
            # Add category->dest_id map to sp matrix
            self.model_data.map_categories_to_sp_matrix()

        else:
            self.categories = ['all_categories']

    def calculate(self):
        """
        Calculate the closest destination for each source per category.
        """

        results = {}
        column_names = ['time_to_nearest_' + category for category in self.categories]
        for source_id in self.model_data.get_all_source_ids():
            results[source_id] = []
            for category in self.categories:
                time_to_nearest_neighbor = self.model_data.time_to_nearest_dest(source_id, category)
                results[source_id].append(time_to_nearest_neighbor)

        self.model_results = pd.DataFrame.from_dict(results, orient='index',
                                                    columns=column_names)


    def aggregate(self, shapefile='data/chicago_boundaries/chicago_boundaries.shp',
                        spatial_index='community', projection='epsg:4326'):
        """
        Aggregate results by community area
        """
        aggregation_args = {}
        for column in self.model_results.columns:
            aggregation_args[column] = ['mean', 'min', 'max']

        self.aggregated_results = self.model_data.build_aggregate(model_results=self.model_results,
                                                                  is_source=False,
                                                                  aggregation_args=aggregation_args,
                                                                  shapefile=shapefile,
                                                                  spatial_index=spatial_index,
                                                                  projection=projection)

    def plot_cdf(self, type, title='title', xlabel='xlabel', ylabel='ylabel'):
        """
        Plot cdf of results
        """
        self.model_data.plot_cdf(model_results=self.model_results,
                                 plot_type=type,
                                 xlabel=xlabel,
                                 ylabel=ylabel,
                                 title=title,
                                 is_source=True)


class AccessCount:
    """
    Measures the number of destinations in range
    for each source per category.
    """

    def __init__(self, network_type, sources_filename=None, source_column_names=None,
                 destinations_filename=None, dest_column_names=None, sp_matrix_filename=None,
                 categories=None):

        self.model_data = ModelData(network_type=network_type,
                                    sources_filename=sources_filename,
                                    destinations_filename=destinations_filename,
                                    source_column_names=source_column_names,
                                    dest_column_names=dest_column_names)

        self.model_data.load_sp_matrix(sp_matrix_filename)
        self.model_results = None
        self.aggregated_results = None
        self.categories = categories
        if self.categories is not None:
            unrecognized_categories = set(categories) - self.model_data.get_all_categories()
            if len(unrecognized_categories) > 0:
                raise UnrecognizedCategoriesException(unrecognized_categories)
            # Add category->dest_id map to sp matrix
            self.model_data.map_categories_to_sp_matrix()
        else:
            self.categories = ['all_categories']

    def calculate(self, upper_threshold):
        """
        Calculate the closest destination for each source per category.
        """

        results = {}
        column_names = ['count_in_range_' + category for category in self.categories]
        for source_id in self.model_data.get_all_source_ids():
            results[source_id] = []
            for category in self.categories:
                count_in_range = self.model_data.count_dests_in_range_by_categories(source_id, upper_threshold, category)
                results[source_id].append(count_in_range)

        self.model_results = pd.DataFrame.from_dict(results, orient='index',
                                                    columns=column_names)

    def aggregate(self, shapefile='data/chicago_boundaries/chicago_boundaries.shp',
                        spatial_index='community', projection='epsg:4326'):
        """
        Aggregate results by community area
        """
        aggregation_args = {}
        for column in self.model_results.columns:
            aggregation_args[column] = 'mean'

        self.aggregated_results = self.model_data.build_aggregate(model_results=self.model_results,
                                                                  is_source=False,
                                                                  aggregation_args=aggregation_args,
                                                                  shapefile=shapefile,
                                                                  spatial_index=spatial_index,
                                                                  projection=projection)

    def plot_cdf(self, type, title='title', xlabel='xlabel', ylabel='ylabel'):
        """
        Plot cdf of results
        """
        self.model_data.plot_cdf(model_results=self.model_results,
                                 plot_type=type,
                                 xlabel=xlabel,
                                 ylabel=ylabel,
                                 title=title,
                                 is_source=True)

class AccessModel():
    """
    Build the Access model which captures the accessibility of 
    nonprofit services in urban environments.
    """

    def __init__(self, network_type, sources_filename=None, source_column_names=None,
                 destinations_filename=None, dest_column_names=None, sp_matrix_filename=None,
                decay_function='linear'):

        self.set_decay_function(decay_function)
        self.model_data = ModelData(network_type=network_type,
                                    sources_filename=sources_filename,
                                    destinations_filename=destinations_filename,
                                    source_column_names=source_column_names,
                                    dest_column_names=dest_column_names)
        self.model_data.load_sp_matrix(sp_matrix_filename)

        self.model_results = {}
        self.aggregated_results = None

    def set_decay_function(self, decay_function):
        """
        Set the decay function. Should be a string:
        'linear', 'root', 'logit', or a lambda of
        the form f(x, y) -> z.

        Range should be the nonnegative integer space.
        """
        if isinstance(decay_function, str):
            if decay_function == 'linear':
                self.decay_function = linear_decay_function
            elif decay_function == 'root':
                self.decay_function = root_decay_function
            elif decay_function == 'logit':
                self.decay_function = logit_decay_function
            else:
                raise UnrecognizedDecayFunctionException(decay_function)
        elif isinstance(decay_function, type(lambda : x)):
            try:
                x = decay_function(1, 2)
                assert isinstance(x, int) or isinstance(x, float)
            except (TypeError, AssertionError):
                raise UnrecognizedDecayFunctionException('lambda sbould have form:f(x, y) -> z')
            self.decay_function = decay_function
        else:
            message = "Decay function should be either a string: ['linear', 'root', 'logit'], or a lamda"
            raise UnrecognizedDecayFunctionException(message)

    def _test_category_weight_dict(self, category_weight_dict):
        """
        Ensure category_weight_dict has the expected form
        """
        if not isinstance(category_weight_dict, dict):
            raise IncompleteCategoryDictException('category_weight_dict should be a dictionary')

        if len(category_weight_dict) == 0:
            raise IncompleteCategoryDictException('category_weight_dict cannot be empty')

        for value in category_weight_dict.values():
            if not (isinstance(value, list) or isinstance(value, tuple)):
                raise IncompleteCategoryDictException('category_weight_dict values should be arrays or tuples')

    def calculate(self, category_weight_dict, upper_threshold, good_access_threshold=40,
                      normalize=True):
        """
        Calculate the model.
        """
        self._test_category_weight_dict(category_weight_dict)

        # create a quick reference for the number of times to include a dest in each category
        max_category_occurances = {category : len(weights) for category, weights in category_weight_dict.items()}

        # order the user's weights in ascending order so the highest one gets used
        # first, for the closest dest of that category
        category_weight_dict = {category : sorted(weights, reverse=True) for category, weights in category_weight_dict.items()}

        # warn the user if the data has more categories than their category_weight_dict
        key_diffs = set(self.model_data.get_all_categories()) - set(max_category_occurances.keys())
        for key in key_diffs:
            max_category_occurances[key] = 0
        if len(key_diffs) > 0:
            self.model_data.logger.warning('Found these keys in data but not in category_weight_dict: {}'.format(key_diffs))
        results = {}

        for source_id in self.model_data.get_all_source_ids():
            category_encounters = {category: 0 for category in self.model_data.get_all_categories()}
            score = 0
            for dest_id, time in self.model_data.get_values_by_source(source_id, sort=True):
                decayed_time = self.decay_function(time, upper_threshold)
                category = self.model_data.get_category(dest_id)
                category_occurances = category_encounters[category]
                if category_occurances < max_category_occurances[category]:
                    decayed_category_weight = category_weight_dict[category][category_occurances]
                    category_encounters[category] += 1
                else:
                    decayed_category_weight = 0
                score += decayed_time * decayed_category_weight
            results[source_id] = [score]

        self.model_results = pd.DataFrame.from_dict(results, orient='index',
                                                    columns=['score'])

        if normalize:
            max_score = self.model_results['score'].max()
            self.model_results['score'] = (self.model_results['score'] / max_score) * 100.0

        self.model_results['good_access'] = self.model_results['score'] > good_access_threshold

    def aggregate(self, shapefile='data/chicago_boundaries/chicago_boundaries.shp',
                        spatial_index='community', projection='epsg:4326'):
        """
        Aggregate results by community area
        """
        aggregation_args = {}
        for column in self.model_results.columns:
            if 'score' in column:
                aggregation_args[column] = 'mean'
            elif 'good_access' in column:
                aggregation_args[column] = 'count'

        self.aggregated_results = self.model_data.build_aggregate(model_results=self.model_results,
                                                                  is_source=False,
                                                                  aggregation_args=aggregation_args,
                                                                  shapefile=shapefile,
                                                                  spatial_index=spatial_index,
                                                                  projection=projection)

    def plot_cdf(self, type, title='title', xlabel='xlabel', ylabel='ylabel'):
        """
        Plot cdf of results
        """
        self.model_data.plot_cdf(model_results=self.model_results,
                                 plot_type=type,
                                 xlabel=xlabel,
                                 ylabel=ylabel,
                                 title=title,
                                 is_source=True)