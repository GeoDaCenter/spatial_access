# Logan Noel (github.com/lmnoel)
#
# ©2017-2019, Center for Spatial Data Science

import pandas as pd
from spatial_access.BaseModel import ModelData
from spatial_access.SpatialAccessExceptions import UnrecognizedDecayFunctionException
from spatial_access.SpatialAccessExceptions import IncompleteCategoryDictException
from spatial_access.SpatialAccessExceptions import UnexpectedNormalizeTypeException
from spatial_access.SpatialAccessExceptions import UnexpectedNormalizeColumnsException
from spatial_access.SpatialAccessExceptions import UnexpectedEmptyColumnException

import math

# TODO: Don't prompt for variable for models which don't use them
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
        return (1 / math.sqrt(upper)) * (-time ** 0.5) + 1


def logit_decay_function(time, upper):
    """
    Logit distance decay function.
    """
    if time > upper:
        return 0
    else:
        return 1-(1/(math.exp((upper/180)-(.48/60)*time)+1))

# TODO: separate each category into its own column
class Coverage(ModelData):
    """
    Build Coverage which captures
    the level of spending for low income residents in
    urban environments.
    """

    def __init__(self, network_type, sources_filename=None, source_column_names=None,
                 destinations_filename=None, dest_column_names=None, transit_matrix_filename=None,
                 categories=None, debug=False):
        """
        Args:
            network_type: string, one of {'walk', 'bike', 'drive', 'otp'}.
            sources_filename: string, csv filename.
            destinations_filename: string, csv filename.
            source_column_names: dictionary, map column names to expected values.
            dest_column_names: dictionary, map column names to expected values.
            debug: boolean, enable to see more detailed logging output.
            transit_matrix_filename: string, optional
        """
        super().__init__(network_type,
                         sources_filename=sources_filename,
                         source_column_names=source_column_names,
                         destinations_filename=destinations_filename,
                         dest_column_names=dest_column_names,
                         debug=debug)
        self.load_transit_matrix(transit_matrix_filename)
        self.set_focus_categories(categories=categories)
        self._is_source = False
        self._result_column_names = {'service_pop', 'percap_spending'}

    # TODO: optimize
    def calculate(self, upper_threshold):
        """
        Args:
            upper_threshold: numeric, time in seconds.
        Calculate the per-capita values and served population for each destination record.

        Returns: DataFrame
        """
        self.calculate_sources_in_range(upper_threshold)
        results = {}
        for category in self.focus_categories:
            for dest_id in self.get_ids_for_category(category):
                population_in_range = self.get_population_in_range(dest_id)
                if population_in_range > 0:
                    percapita_spending = self.get_capacity(dest_id) / population_in_range
                else:
                    percapita_spending = 0
                results[dest_id] = [population_in_range, percapita_spending, category]

        self.model_results = pd.DataFrame.from_dict(results, orient='index',
                                                    columns=['service_pop',
                                                             'percap_spending',
                                                             'category'])
        for column in self.model_results.columns:
            if 'service_pop' in column:
                self._aggregation_args[column] = 'sum'
            elif 'percap_spending' in column:
                self._aggregation_args[column] = 'mean'

        return self.model_results


class DestSum(ModelData):
    """
    Build DestSum which captures the capacity
    and capacity per capita of providers in a
    community area.
    """

    def __init__(self, network_type, sources_filename=None, source_column_names=None,
                 destinations_filename=None, dest_column_names=None,
                 categories=None, bike_speed=None, walk_speed=None, debug=False):
        """
        Args:
            network_type: string, one of {'walk', 'bike', 'drive', 'otp'}.
            sources_filename: string, csv filename.
            destinations_filename: string, csv filename.
            source_column_names: dictionary, map column names to expected values.
            dest_column_names: dictionary, map column names to expected values.
            walk_speed: numeric, override default walking speed (km/hr).
            bike_speed: numeric, override default walking speed (km/hr).
            debug: boolean, enable to see more detailed logging output.
        """

        super().__init__(network_type, sources_filename=sources_filename, source_column_names=source_column_names,
                         destinations_filename=destinations_filename, dest_column_names=dest_column_names,
                         bike_speed=bike_speed, walk_speed=walk_speed, debug=debug)

        self.reload_sources(sources_filename)
        self.reload_dests(destinations_filename)
        self.set_focus_categories(categories=categories)
        self._is_aggregatable = False
        self._is_source = False

    def calculate(self, shapefile='data/chicago_boundaries/chicago_boundaries.shp',
                  spatial_index='community',  projection='epsg:4326'):
        """
        Calculate the target/capacity per capita of providers in spatial areas.
        Args:
            shapefile: filename of shapefile
            spatial_index: index of geospatial area in shapefile
            projection: defaults to 'epsg:4326'

        Returns: data frame.
        """

        dests_copy = self.dests.copy(deep=True)

        capacity_col = dests_copy.columns.get_loc('capacity') + 1
        category_col = dests_copy.columns.get_loc('category') + 1
        for row in dests_copy.itertuples():
            dests_copy.loc[row[0], row[category_col]] = row[capacity_col]
            dests_copy.loc[row[0], 'all_categories'] = row[capacity_col]
        dest_aggregation_args = {key:'sum' for key in set(dests_copy['category'])}
        dest_aggregation_args['all_categories'] = 'sum'
        dests_copy.fillna(value=0, inplace=True)

        self._rejoin_results_with_coordinates(dests_copy, is_source=False)
        self._rejoin_results_with_coordinates(self.sources, is_source=True)
        aggregated_dests = self._build_aggregate(data_frame=dests_copy,
                                                 shapefile=shapefile,
                                                 spatial_index=spatial_index,
                                                 projection=projection,
                                                 aggregation_args=dest_aggregation_args)

        aggregated_sources = self._build_aggregate(data_frame=self.sources,
                                                   shapefile=shapefile,
                                                   spatial_index=spatial_index,
                                                   projection=projection,
                                                   aggregation_args={'population': 'sum'})

        for column in aggregated_dests.columns:
            aggregated_dests[column + '_per_capita'] = aggregated_dests[column] / aggregated_sources['population']
        self.aggregated_results = aggregated_dests
        return self.aggregated_results


class TSFCA(ModelData):
    """
    Build the TSFCA which quantifies
    the per-resident spending for given categories.
    """

    def __init__(self, network_type, sources_filename=None, source_column_names=None,
                 destinations_filename=None, dest_column_names=None, transit_matrix_filename=None,
                 categories=None, bike_speed=None, walk_speed=None, debug=False):
        """
        Args:
            network_type: string, one of {'walk', 'bike', 'drive', 'otp'}.
            sources_filename: string, csv filename.
            destinations_filename: string, csv filename.
            source_column_names: dictionary, map column names to expected values.
            dest_column_names: dictionary, map column names to expected values.
            walk_speed: numeric, override default walking speed (km/hr).
            bike_speed: numeric, override default walking speed (km/hr).
            debug: boolean, enable to see more detailed logging output.
            transit_matrix_filename: string, optional.
        """

        super().__init__(network_type=network_type,
                         sources_filename=sources_filename,
                         destinations_filename=destinations_filename,
                         source_column_names=source_column_names,
                         dest_column_names=dest_column_names,
                         walk_speed=walk_speed,
                         bike_speed=bike_speed,
                         debug=debug)

        self.load_transit_matrix(transit_matrix_filename)
        self.set_focus_categories(categories=categories)
        self._result_column_names = {'percap_spend', 'total_spend'}

    def calculate(self, upper_threshold):
        """
        Args:
            upper_threshold: numeric, time in seconds.

        Returns: DataFrame
        """
        self.calculate_sources_in_range(upper_threshold)
        self.calculate_dests_in_range(upper_threshold)

        # initialize results as {source_id: []}
        results = {}
        num_categories = len(self.focus_categories)
        for source_id in self.get_all_source_ids():
            results[source_id] = [0] * num_categories

        # map category to index in results and generate column names
        column_name_to_index = {}
        column_names = []

        for index, category in enumerate(self.focus_categories):
            column_names.append('percap_spend_' + category)
            column_name_to_index[category] = index

        dests_capacity = {}
        for category in self.focus_categories:
            for dest_id in self.get_ids_for_category(category):
                population_in_range = self.get_population_in_range(dest_id)
                if population_in_range > 0:
                    contribution_to_spending = self.get_capacity(dest_id) / population_in_range
                    dests_capacity[dest_id] = contribution_to_spending
                else:
                    dests_capacity[dest_id] = 0
        for source_id in self.get_all_source_ids():
            for dest_id in self.get_dests_in_range_of_source(source_id):
                category = self.get_category(dest_id)
                if category in self.focus_categories:
                    results[source_id][column_name_to_index[category]] += dests_capacity[dest_id]

        self.model_results = pd.DataFrame.from_dict(results, orient='index',
                                                    columns=column_names)

        for column in self.model_results.columns:
            if 'percap_spend' in column:
                self._aggregation_args[column] = 'mean'
            elif 'total_spend' in column:
                self._aggregation_args[column] = 'sum'

        return self.model_results


class AccessTime(ModelData):
    """
    Measures the closest destination for each source per category.
    """

    def __init__(self, network_type, sources_filename=None, source_column_names=None,
                 destinations_filename=None, dest_column_names=None, transit_matrix_filename=None,
                 categories=None, bike_speed=None, walk_speed=None, debug=False):
        """
        Args:
            network_type: string, one of {'walk', 'bike', 'drive', 'otp'}.
            sources_filename: string, csv filename.
            destinations_filename: string, csv filename.
            source_column_names: dictionary, map column names to expected values.
            dest_column_names: dictionary, map column names to expected values.
            walk_speed: numeric, override default walking speed (km/hr).
            bike_speed: numeric, override default walking speed (km/hr).
            debug: boolean, enable to see more detailed logging output.
            transit_matrix_filename: string, optional.
        """

        super().__init__(network_type=network_type,
                         sources_filename=sources_filename,
                         destinations_filename=destinations_filename,
                         source_column_names=source_column_names,
                         dest_column_names=dest_column_names,
                         walk_speed=walk_speed,
                         bike_speed=bike_speed,
                         debug=debug)
        self.load_transit_matrix(transit_matrix_filename)
        self.set_focus_categories(categories=categories)
        self._requires_user_aggregation_type = True
        self._map_categories_to_sp_matrix()

    def calculate(self):
        """
        Returns: DataFrame
        """

        results = {}
        focus_categories_list = list(self.focus_categories)
        column_names = ['time_to_nearest_' + category for category in focus_categories_list]
        for source_id in self.get_all_source_ids():
            results[source_id] = []
            for category in focus_categories_list:
                time_to_nearest_neighbor = self.time_to_nearest_dest(source_id, category)
                results[source_id].append(time_to_nearest_neighbor)

        self.model_results = pd.DataFrame.from_dict(results, orient='index',
                                                    columns=column_names)
        return self.model_results


class AccessCount(ModelData):
    """
    Measures the number of destinations in range
    for each source per category.
    """

    def __init__(self, network_type, sources_filename=None, source_column_names=None,
                 destinations_filename=None, dest_column_names=None, transit_matrix_filename=None,
                 categories=None, bike_speed=None, walk_speed=None, debug=False):
        """
        Args:
            network_type: string, one of {'walk', 'bike', 'drive', 'otp'}.
            sources_filename: string, csv filename.
            destinations_filename: string, csv filename.
            source_column_names: dictionary, map column names to expected values.
            dest_column_names: dictionary, map column names to expected values.
            walk_speed: numeric, override default walking speed (km/hr).
            bike_speed: numeric, override default walking speed (km/hr).
            debug: boolean, enable to see more detailed logging output.
            transit_matrix_filename: string, optional.
        """

        super().__init__(network_type=network_type,
                         sources_filename=sources_filename,
                         destinations_filename=destinations_filename,
                         source_column_names=source_column_names,
                         dest_column_names=dest_column_names,
                         walk_speed=walk_speed,
                         bike_speed=bike_speed,
                         debug=debug)

        self.load_transit_matrix(transit_matrix_filename)
        self.set_focus_categories(categories=categories)
        self._map_categories_to_sp_matrix()
        self._result_column_names = 'count_in_range'

    def calculate(self, upper_threshold):
        """
        Args:
            upper_threshold: numeric, time in seconds.

        Returns: DataFrame
        """
        results = {}
        focus_categories_list = list(self.focus_categories)
        column_names = ['count_in_range_' + category for category in focus_categories_list]
        self.calculate_dests_in_range(upper_threshold)
        for source_id in self.get_all_source_ids():
            results[source_id] = []
            for category in focus_categories_list:
                count_in_range = self.count_dests_in_range_by_categories(source_id=source_id,
                                                                                category=category,
                                                                                    upper_threshold=upper_threshold)
                results[source_id].append(count_in_range)

        self.model_results = pd.DataFrame.from_dict(results, orient='index',
                                                    columns=column_names)

        for column in self.model_results.columns:
            self._aggregation_args[column] = 'mean'

        return self.model_results


class AccessSum(ModelData):
    """
    Measures the capacity of providers in range
    for each source per category.
    """

    def __init__(self, network_type, sources_filename=None, source_column_names=None,
                 destinations_filename=None, dest_column_names=None, transit_matrix_filename=None,
                 categories=None, bike_speed=None, walk_speed=None, debug=False):
        """
        Args:
            network_type: string, one of {'walk', 'bike', 'drive', 'otp'}.
            sources_filename: string, csv filename.
            destinations_filename: string, csv filename.
            source_column_names: dictionary, map column names to expected values.
            dest_column_names: dictionary, map column names to expected values.
            walk_speed: numeric, override default walking speed (km/hr).
            bike_speed: numeric, override default walking speed (km/hr).
            debug: boolean, enable to see more detailed logging output.
            transit_matrix_filename: string, optional.
        """

        super().__init__(network_type=network_type,
                         sources_filename=sources_filename,
                         destinations_filename=destinations_filename,
                         source_column_names=source_column_names,
                         dest_column_names=dest_column_names,
                         walk_speed=walk_speed,
                         bike_speed=bike_speed,
                         debug=debug)

        self.load_transit_matrix(transit_matrix_filename)
        self.set_focus_categories(categories=categories)
        self._map_categories_to_sp_matrix()
        self._result_column_names = 'sum_in_range'

    def calculate(self, upper_threshold):
        """
        Args:
            upper_threshold: numeric, time in seconds.

        Returns: DataFrame
        """

        results = {}
        focus_categories_list = list(self.focus_categories)
        column_names = ['sum_in_range_' + category for category in focus_categories_list]
        self.calculate_dests_in_range(upper_threshold)
        for source_id in self.get_all_source_ids():
            results[source_id] = []
            for category in focus_categories_list:
                sum_in_range = self.count_sum_in_range_by_categories(source_id,
                                                                                    category)
                results[source_id].append(sum_in_range)

        self.model_results = pd.DataFrame.from_dict(results, orient='index',
                                                    columns=column_names)
        for column in self.model_results.columns:
            self._aggregation_args[column] = 'mean'

        return self.model_results


class AccessModel(ModelData):
    """
    Build the Access model which captures the accessibility of 
    nonprofit services in urban environments.
    """

    def __init__(self, network_type, sources_filename=None, source_column_names=None,
                 destinations_filename=None, dest_column_names=None, transit_matrix_filename=None,
                 decay_function='linear', walk_speed=None, bike_speed=None, debug=False):
        """
        Args:
            network_type: string, one of {'walk', 'bike', 'drive', 'otp'}.
            sources_filename: string, csv filename.
            destinations_filename: string, csv filename.
            source_column_names: dictionary, map column names to expected values.
            dest_column_names: dictionary, map column names to expected values.
            walk_speed: numeric, override default walking speed (km/hr).
            bike_speed: numeric, override default walking speed (km/hr).
            debug: boolean, enable to see more detailed logging output.
            decay_function: lambda or string
            transit_matrix_filename: string, optional
        """
        self.decay_function = None
        self.set_decay_function(decay_function)
        super().__init__(network_type=network_type,
                         sources_filename=sources_filename,
                         destinations_filename=destinations_filename,
                         source_column_names=source_column_names,
                         dest_column_names=dest_column_names,
                         walk_speed=walk_speed,
                         bike_speed=bike_speed,
                         debug=debug)
        self.load_transit_matrix(transit_matrix_filename)
        self._result_column_names = 'score'

    def set_decay_function(self, decay_function):
        """
        Args:
            decay_function: 'linear', 'root', 'logit', or a lambda of
            the form f(x, y) -> z. Range should be the nonnegative
            integer space.

        Raises:
            UnrecognizedDecayFunctionException: Illegal decay function.
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
        elif isinstance(decay_function, type(lambda: x)):
            try:
                x = decay_function(1, 2)
                assert isinstance(x, int) or isinstance(x, float)
            except (TypeError, AssertionError):
                raise UnrecognizedDecayFunctionException('lambda sbould have form:f(x, y) -> z')
            self.decay_function = decay_function
        else:
            message = "Decay function should be either a string: ['linear', 'root', 'logit'], or a lamda"
            raise UnrecognizedDecayFunctionException(message)

    @staticmethod
    def _test_category_weight_dict(category_weight_dict):
        """
        Ensure category_weight_dict has the expected form.
        Args:
            category_weight_dict: dictionary of {category : [numeric weights]}
        Raises:
            IncompleteCategoryDictException: category_weight_dict does
                not have the expected format.
        """
        if not isinstance(category_weight_dict, dict):
            raise IncompleteCategoryDictException('category_weight_dict should be a dictionary')

        for value in category_weight_dict.values():
            if not isinstance(value, list):
                raise IncompleteCategoryDictException('category_weight_dict values should be arrays')

    def _log_category_weight_dict(self, category_weight_dict):
        """
        Log the category_weight_dict in a useful format.
        Args:
            category_weight_dict: dictionary of arrays.
        """
        presented_weight_dict = {key : "No decay" for key in self.all_categories}
        presented_weight_dict = {**presented_weight_dict, **category_weight_dict}
        self.logger.info("Using weights: {}".format(presented_weight_dict))

    def calculate(self, category_weight_dict, upper_threshold,
                  normalize=True, normalize_type='linear'):
        """
        Args:
            category_weight_dict: category_weight_dict: dictionary of {category : [numeric weights]}
            upper_threshold: time in seconds.
            normalize: boolean. If true, results will be normalized
                from 0 to 100.
            normalize_type: 'linear' or 'z_score'.
        Returns: DataFrame.
        Raises:
            UnexpectedNormalizeColumnsException
        """
        self._test_category_weight_dict(category_weight_dict)

        # create a quick reference for the number of times to include a dest in each category
        max_category_occurances = {category: len(weights) for category, weights in category_weight_dict.items()}

        # order the user's weights in ascending order so the highest one gets used
        # first, for the closest dest of that category
        category_weight_dict = {category: sorted(weights, reverse=True)
                                for category, weights in category_weight_dict.items()}

        self._log_category_weight_dict(category_weight_dict)

        # reserve results dict for each column
        num_columns = len(self.all_categories) + 1
        results = {source_id: [0] * num_columns for source_id in self.get_all_source_ids()}

        # map of column names
        category_to_index_map = {}
        column_names = ['all_categories_score']
        index = 1
        for category in self.all_categories:
            column_names.append(category + '_score')
            category_to_index_map[category] = index
            index += 1

        # calculate score for each source_id
        for source_id in self.get_all_source_ids():
            category_encounters = {category: 0 for category in self.all_categories}
            for dest_id, time in self.get_values_by_source(source_id, sort=True):
                decayed_time = self.decay_function(time, upper_threshold)
                category = self.get_category(dest_id)
                category_occurances = category_encounters[category]
                # no weights supplied for this category; so don't decay
                if category not in category_weight_dict:
                    results[source_id][0] += decayed_time
                    results[source_id][category_to_index_map[category]] += decayed_time
                # weights supplied for this category, still haven't been used up
                elif category_occurances < max_category_occurances[category]:
                    decayed_category_weight = category_weight_dict[category][category_occurances]
                    category_encounters[category] += 1
                    score_contribution = decayed_time * decayed_category_weight
                    results[source_id][0] += score_contribution
                    results[source_id][category_to_index_map[category]] += score_contribution
                # weights for this category have been used up
                else:
                    continue

        self.model_results = pd.DataFrame.from_dict(results, orient='index',
                                                    columns=column_names)

        if isinstance(normalize, list):
            for column in normalize:
                column_key = column + '_score'
                self._normalize(column_key, normalize_type)
        elif normalize is True:
            for column in self.model_results.columns:
                self._normalize(column, normalize_type)
        elif normalize is False:
            pass
        else:
            raise UnexpectedNormalizeColumnsException('Argument ({}) is not of expected type: boolean, list'
                                                      .format(normalize))

        for column in self.model_results.columns:
            self._aggregation_args[column] = 'mean'

        return self.model_results

    def _normalize(self, column, normalize_type):
        """
        Normalize results.
        Args:
            column: which column to normalize.
            normalize_type: 'linear' or 'z-score'

        Raises:
            UnexpectedEmptyColumnException
            UnexpectedNormalizeTypeException
        """
        if normalize_type == 'linear':
            max_score = self.model_results[column].max()
            self.model_results[column] = (self.model_results[column] / max_score) * 100.0
        elif normalize_type == 'z_score':
            try:
                self.model_results[column] = (self.model_results[column]
                                              - self.model_results[column].mean()) / self.model_results[column].std()
            except ZeroDivisionError:
                raise UnexpectedEmptyColumnException(column)
        else:
            raise UnexpectedNormalizeTypeException(normalize_type)

