# pylint: skip-file
from spatial_access.CommunityAnalytics import DestFloatingCatchmentArea
from spatial_access.CommunityAnalytics import TwoStageFloatingCatchmentArea
from spatial_access.CommunityAnalytics import AccessTime
from spatial_access.CommunityAnalytics import AccessCount
from spatial_access.CommunityAnalytics import AccessModel
from spatial_access.SpatialAccessExceptions import UnrecognizedCategoriesException
from spatial_access.SpatialAccessExceptions import UnrecognizedDecayFunctionException
from spatial_access.SpatialAccessExceptions import IncompleteCategoryDictException
from spatial_access.SpatialAccessExceptions import UnexpectedAggregationTypeException

import json


class TestClass:
    """Suite of tests for the Community Analytics Package"""

    def setup_class(self):
        import os
        self.datapath = 'tests/test_community_analytics_temp/'
        if not os.path.exists(self.datapath):
            os.mkdir(self.datapath)

    def teardown_class(self):
        import os
        if os.path.exists(self.datapath):
            import shutil
            shutil.rmtree(self.datapath)

    def test_01(self):
        """
        Test the DestFloatingCatchmentArea model through instantiation and
        calculate.
        """
        coverage_model = DestFloatingCatchmentArea('drive',
                                                   sources_filename='tests/test_data/sources_a.csv',
                                                   destinations_filename='tests/test_data/dests_b.csv',
                                                   source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                        'population': 'pop'},
                                                   dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                      'capacity': 'capacity', 'category': 'cat'})
        coverage_model.calculate(100)

        assert coverage_model.model_results.loc[0]['service_pop'] == 76
        assert coverage_model.model_results.loc[1]['service_pop'] == 76
        assert coverage_model.model_results.loc[2]['service_pop'] == 469
        assert coverage_model.model_results.loc[3]['service_pop'] == 76
        assert coverage_model.model_results.loc[4]['service_pop'] == 76
        assert coverage_model.model_results.loc[5]['service_pop'] == 469

        assert coverage_model.model_results.loc[0]['percap_spending'] <= 0.066
        assert coverage_model.model_results.loc[1]['percap_spending'] <= 0.606
        assert coverage_model.model_results.loc[2]['percap_spending'] <= 0.738
        assert coverage_model.model_results.loc[3]['percap_spending'] <= 3.053
        assert coverage_model.model_results.loc[4]['percap_spending'] <= 5.264
        assert coverage_model.model_results.loc[5]['percap_spending'] <= 1.210

        assert coverage_model.model_results.loc[0]['percap_spending'] >= 0.065
        assert coverage_model.model_results.loc[1]['percap_spending'] >= 0.605
        assert coverage_model.model_results.loc[2]['percap_spending'] >= 0.737
        assert coverage_model.model_results.loc[3]['percap_spending'] >= 3.052
        assert coverage_model.model_results.loc[4]['percap_spending'] >= 5.263
        assert coverage_model.model_results.loc[5]['percap_spending'] >= 1.208

    def test_02(self):
        """
        Expects UnrecognizedCategoriesException to
        throw because the user supplies categories
        which are not present in the data
        """
        try:
            coverage_model = DestFloatingCatchmentArea('drive',
                                                       sources_filename='tests/test_data/sources.csv',
                                                       destinations_filename='tests/test_data/dests.csv',
                                                       source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                            'population': 'pop'},
                                                       dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                          'capacity': 'capacity', 'category': 'cat'},
                                                       categories=['A', 'C'])
            coverage_model.calculate(600)
        except UnrecognizedCategoriesException:
            assert True
            return
        assert False

    def test_03(self):
        """
        Test the DestFloatingCatchmentAreaModel through instantiation and
        calculate, with categories specified.
        """
        coverage_model = DestFloatingCatchmentArea('drive',
                                                   sources_filename='tests/test_data/sources_a.csv',
                                                   destinations_filename='tests/test_data/dests_b.csv',
                                                   source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                        'population': 'pop'},
                                                   dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                      'capacity': 'capacity', 'category': 'cat'},
                                                   categories=['A', 'C'])
        coverage_model.calculate(600)

        remapped_dests = coverage_model.model_data.get_remapped_dest_ids()

        assert set(coverage_model.model_results.index) == {remapped_dests['place_a'],
                                                           remapped_dests['place_c'],
                                                           remapped_dests['place_d'],
                                                           remapped_dests['place_e'],
                                                           remapped_dests['place_f']}

    def test_4(self):
        """
        Test TwoStageFloatingCatchmentArea through instantiation and
        calculate.
        """
        accesspop_model = TwoStageFloatingCatchmentArea('drive',
                                                        sources_filename='tests/test_data/sources_a.csv',
                                                        destinations_filename='tests/test_data/dests_b.csv',
                                                        source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                             'population': 'pop'},
                                                        dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                           'capacity': 'capacity', 'category': 'cat'})
        accesspop_model.calculate(100)

        assert accesspop_model.model_results.loc[3]['percap_spend_all_categories'] >= 10.933
        assert accesspop_model.model_results.loc[4]['percap_spend_all_categories'] >= 10.933
        assert accesspop_model.model_results.loc[5]['percap_spend_all_categories'] >= 1.946
        assert accesspop_model.model_results.loc[6]['percap_spend_all_categories'] >= 1.946
        assert accesspop_model.model_results.loc[7]['percap_spend_all_categories'] >= 1.946
        assert accesspop_model.model_results.loc[8]['percap_spend_all_categories'] >= 1.946

        assert accesspop_model.model_results.loc[3]['percap_spend_all_categories'] <= 10.934
        assert accesspop_model.model_results.loc[4]['percap_spend_all_categories'] <= 10.934
        assert accesspop_model.model_results.loc[5]['percap_spend_all_categories'] <= 1.947
        assert accesspop_model.model_results.loc[6]['percap_spend_all_categories'] <= 1.947
        assert accesspop_model.model_results.loc[7]['percap_spend_all_categories'] <= 1.947
        assert accesspop_model.model_results.loc[8]['percap_spend_all_categories'] <= 1.947

    def test_5(self):
        """
        Expects UnrecognizedCategoriesException to
        throw because the user supplies categories
        which are not present in the data
        """
        try:
            accesspop_model = TwoStageFloatingCatchmentArea('drive',
                                                            sources_filename='tests/test_data/sources.csv',
                                                            destinations_filename='tests/test_data/dests.csv',
                                                            source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                                 'population': 'pop'},
                                                            dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                               'capacity': 'capacity',
                                                                               'category': 'cat'},
                                                            categories=['A', 'E'])
            accesspop_model.calculate(600)
        except UnrecognizedCategoriesException:
            assert True
            return
        assert False

    def test_6(self):
        """
        Test TwoStageFloatingCatchmentArea through instantiation and
        calculate, with categories specified.
        """
        categories = ['A', 'C']
        accesspop_model = TwoStageFloatingCatchmentArea('drive',
                                                        sources_filename='tests/test_data/sources_a.csv',
                                                        destinations_filename='tests/test_data/dests_b.csv',
                                                        source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                             'population': 'pop'},
                                                        dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                           'capacity': 'capacity', 'category': 'cat'},
                                                        categories=categories)
        accesspop_model.calculate(100)

        assert len(accesspop_model.model_results.columns) == len(categories)
        assert accesspop_model.model_results.loc[3, 'percap_spend_A'] <= 9.054
        assert accesspop_model.model_results.loc[4, 'percap_spend_A'] <= 9.054
        assert accesspop_model.model_results.loc[5, 'percap_spend_A'] <= 0.738
        assert accesspop_model.model_results.loc[6, 'percap_spend_A'] <= 0.738
        assert accesspop_model.model_results.loc[7, 'percap_spend_A'] <= 0.738
        assert accesspop_model.model_results.loc[8, 'percap_spend_A'] <= 0.738

        assert accesspop_model.model_results.loc[3, 'percap_spend_C'] <= 1.275
        assert accesspop_model.model_results.loc[4, 'percap_spend_C'] <= 1.275
        assert accesspop_model.model_results.loc[5, 'percap_spend_C'] <= 1.209
        assert accesspop_model.model_results.loc[6, 'percap_spend_C'] <= 1.209
        assert accesspop_model.model_results.loc[7, 'percap_spend_C'] <= 1.209
        assert accesspop_model.model_results.loc[8, 'percap_spend_C'] <= 1.209

        assert accesspop_model.model_results.loc[3, 'percap_spend_A'] >= 9.053
        assert accesspop_model.model_results.loc[4, 'percap_spend_A'] >= 9.053
        assert accesspop_model.model_results.loc[5, 'percap_spend_A'] >= 0.737
        assert accesspop_model.model_results.loc[6, 'percap_spend_A'] >= 0.737
        assert accesspop_model.model_results.loc[7, 'percap_spend_A'] >= 0.737
        assert accesspop_model.model_results.loc[8, 'percap_spend_A'] >= 0.737

        assert accesspop_model.model_results.loc[3, 'percap_spend_C'] >= 1.274
        assert accesspop_model.model_results.loc[4, 'percap_spend_C'] >= 1.274
        assert accesspop_model.model_results.loc[5, 'percap_spend_C'] >= 1.208
        assert accesspop_model.model_results.loc[6, 'percap_spend_C'] >= 1.208
        assert accesspop_model.model_results.loc[7, 'percap_spend_C'] >= 1.208
        assert accesspop_model.model_results.loc[8, 'percap_spend_C'] >= 1.208

    def test_7(self):
        """
        Test AccessTime through instantiation and
        calculate.
        """
        accesstime_model = AccessTime('drive',
                                      sources_filename='tests/test_data/sources_a.csv',
                                      destinations_filename='tests/test_data/dests_b.csv',
                                      source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                           'population': 'pop'},
                                      dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                         'capacity': 'capacity', 'category': 'cat'})
        accesstime_model.calculate()

        assert accesstime_model.model_results.loc[3]['time_to_nearest_all_categories'] == 42
        assert accesstime_model.model_results.loc[4]['time_to_nearest_all_categories'] == 7
        assert accesstime_model.model_results.loc[5]['time_to_nearest_all_categories'] == 99
        assert accesstime_model.model_results.loc[6]['time_to_nearest_all_categories'] == 69
        assert accesstime_model.model_results.loc[7]['time_to_nearest_all_categories'] == 70
        assert accesstime_model.model_results.loc[8]['time_to_nearest_all_categories'] == 100

    def test_8(self):
        """
        Expects UnrecognizedCategoriesException to
        throw because the user supplies categories
        which are not present in the data
        """
        try:
            accesstime_model = AccessTime('drive',
                                          sources_filename='tests/test_data/sources.csv',
                                          destinations_filename='tests/test_data/dests.csv',
                                          source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                               'population': 'pop'},
                                          dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                             'capacity': 'capacity', 'category': 'cat'},
                                          categories=['A', 'E'])
            accesstime_model.calculate()
        except UnrecognizedCategoriesException:
            assert True
            return
        assert False

    def test_9(self):
        """
        Test AccessTime through instantiation and
        calculate, with categories specified.
        """
        categories = ['A', 'C']
        accesstime_model = AccessTime('drive',
                                      sources_filename='tests/test_data/sources_a.csv',
                                      destinations_filename='tests/test_data/dests_b.csv',
                                      source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                           'population': 'pop'},
                                      dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                         'capacity': 'capacity', 'category': 'cat'},
                                      categories=categories)
        accesstime_model.calculate()

        assert accesstime_model.model_results.loc[3]['time_to_nearest_A'] == 42
        assert accesstime_model.model_results.loc[4]['time_to_nearest_A'] == 7
        assert accesstime_model.model_results.loc[5]['time_to_nearest_A'] == 99
        assert accesstime_model.model_results.loc[6]['time_to_nearest_A'] == 69
        assert accesstime_model.model_results.loc[7]['time_to_nearest_A'] == 70
        assert accesstime_model.model_results.loc[8]['time_to_nearest_A'] == 100

        assert accesstime_model.model_results.loc[3]['time_to_nearest_C'] == 42
        assert accesstime_model.model_results.loc[4]['time_to_nearest_C'] == 44
        assert accesstime_model.model_results.loc[5]['time_to_nearest_C'] == 99
        assert accesstime_model.model_results.loc[6]['time_to_nearest_C'] == 69
        assert accesstime_model.model_results.loc[7]['time_to_nearest_C'] == 70
        assert accesstime_model.model_results.loc[8]['time_to_nearest_C'] == 100

    def test_10(self):
        """
        Test AccessCount through instantiation and
        calculate.
        """
        accesscount_model = AccessCount('drive',
                                        sources_filename='tests/test_data/sources_a.csv',
                                        destinations_filename='tests/test_data/dests_b.csv',
                                        source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                             'population': 'pop'},
                                        dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                           'capacity': 'capacity', 'category': 'cat'})
        accesscount_model.calculate(100)

        assert accesscount_model.model_results.loc[3]['count_in_range_all_categories'] == 6
        assert accesscount_model.model_results.loc[4]['count_in_range_all_categories'] == 6
        assert accesscount_model.model_results.loc[5]['count_in_range_all_categories'] == 2
        assert accesscount_model.model_results.loc[6]['count_in_range_all_categories'] == 2
        assert accesscount_model.model_results.loc[7]['count_in_range_all_categories'] == 2
        assert accesscount_model.model_results.loc[8]['count_in_range_all_categories'] == 2

    def test_11(self):
        """
        Expects UnrecognizedCategoriesException to
        throw because the user supplies categories
        which are not present in the data
        """
        try:
            accesscount_model = AccessCount('drive',
                                            sources_filename='tests/test_data/sources.csv',
                                            destinations_filename='tests/test_data/dests.csv',
                                            source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                 'population': 'pop'},
                                            dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                               'capacity': 'capacity', 'category': 'cat'},
                                            categories=['A', 'E'])
            accesscount_model.calculate(200)
        except UnrecognizedCategoriesException:
            assert True
            return
        assert False

    def test_12(self):
        """
        Test AccessCount through instantiation and
        calculate, with categories specified.
        """
        categories = ['A', 'C', 'D']
        accesscount_model = AccessCount('drive',
                                        sources_filename='tests/test_data/sources_a.csv',
                                        destinations_filename='tests/test_data/dests_b.csv',
                                        source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                             'population': 'pop'},
                                        dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                           'capacity': 'capacity', 'category': 'cat'},
                                        categories=categories)
        accesscount_model.calculate(100)

        assert accesscount_model.model_results.loc[3]['count_in_range_A'] == 3
        assert accesscount_model.model_results.loc[4]['count_in_range_A'] == 3
        assert accesscount_model.model_results.loc[5]['count_in_range_A'] == 1
        assert accesscount_model.model_results.loc[6]['count_in_range_A'] == 1
        assert accesscount_model.model_results.loc[7]['count_in_range_A'] == 1
        assert accesscount_model.model_results.loc[8]['count_in_range_A'] == 1

        assert accesscount_model.model_results.loc[3]['count_in_range_C'] == 2
        assert accesscount_model.model_results.loc[4]['count_in_range_C'] == 2
        assert accesscount_model.model_results.loc[5]['count_in_range_C'] == 1
        assert accesscount_model.model_results.loc[6]['count_in_range_C'] == 1
        assert accesscount_model.model_results.loc[7]['count_in_range_C'] == 1
        assert accesscount_model.model_results.loc[8]['count_in_range_C'] == 1

        assert accesscount_model.model_results.loc[3]['count_in_range_D'] == 1
        assert accesscount_model.model_results.loc[4]['count_in_range_D'] == 1
        assert accesscount_model.model_results.loc[5]['count_in_range_D'] == 0
        assert accesscount_model.model_results.loc[6]['count_in_range_D'] == 0
        assert accesscount_model.model_results.loc[7]['count_in_range_D'] == 0
        assert accesscount_model.model_results.loc[8]['count_in_range_D'] == 0

    def test_13(self):
        """
        Test AccessModel. Expects throw of UnrecognizedDecayFunctionException
        """

        try:
            access_model = AccessModel('drive',
                                       sources_filename='tests/test_data/sources_a.csv',
                                       destinations_filename='tests/test_data/dests_b.csv',
                                       source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                            'population': 'pop'},
                                       dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                          'capacity': 'capacity', 'category': 'cat'},
                                       decay_function='quadratic')
            access_model.calculate({}, 200)
        except UnrecognizedDecayFunctionException:
            assert True
            return
        assert False

    def test_14(self):
        """
        Test AccessModel. Expects throw of UnrecognizedDecayFunctionException
        because decay function lambda is improper form.
        """

        try:
            access_model = AccessModel('drive',
                                       sources_filename='tests/test_data/sources_a.csv',
                                       destinations_filename='tests/test_data/dests_b.csv',
                                       source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                            'population': 'pop'},
                                       dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                          'capacity': 'capacity', 'category': 'cat'},
                                       decay_function=lambda x: x ** 2)
            access_model.calculate({}, 200)
        except UnrecognizedDecayFunctionException:
            assert True
            return
        assert False

    def test_15(self):
        """
        Test AccessModel. Expects throw of IncompleteCategoryDictException
        because category_weight_dict takes several incorrect forms.
        """
        access_model = AccessModel('drive',
                                   sources_filename='tests/test_data/sources_a.csv',
                                   destinations_filename='tests/test_data/dests_b.csv',
                                   source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                        'population': 'pop'},
                                   dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                      'capacity': 'capacity', 'category': 'cat'},
                                   decay_function='linear')
        try:
            category_weight_dict = [1, 2, 4, 5]
            access_model.calculate(category_weight_dict, upper_threshold=200)
            assert False
        except IncompleteCategoryDictException:
            assert True

        try:
            category_weight_dict = {'A': [1, 2, 3, 4], 'D': 4, 'C': [5, 6, 8, 5, 3]}
            access_model.calculate(category_weight_dict, upper_threshold=200)
            assert False
        except IncompleteCategoryDictException:
            assert True

    def test_16(self):
        """
        Test AccessModel with normalization
        """
        coverage_model = AccessModel('drive',
                                     sources_filename='tests/test_data/sources_a.csv',
                                     destinations_filename='tests/test_data/dests_b.csv',
                                     source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                          'population': 'pop'},
                                     dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                        'capacity': 'capacity', 'category': 'cat'},
                                     decay_function='linear')

        category_weight_dict = {'A': [5, 4, 3, 2, 1],
                                'D': [4, 3, 1],
                                'C': [1]}
        coverage_model.calculate(category_weight_dict, upper_threshold=700, normalize=True)

        assert coverage_model.model_results['all_categories_score'].max() == 100
        assert coverage_model.model_results['all_categories_score'].min() >= 0

    def test_17(self):
        """
        Test AccessModel with not all categories represented
        in category_weight_dict
        """
        coverage_model = AccessModel('drive',
                                     sources_filename='tests/test_data/sources_a.csv',
                                     destinations_filename='tests/test_data/dests_b.csv',
                                     source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                          'population': 'pop'},
                                     dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                        'capacity': 'capacity', 'category': 'cat'},
                                     decay_function='linear')

        category_weight_dict = {'A': [5, 4, 3, 2, 1],
                                'D': [4, 3, 1]}
        coverage_model.calculate(category_weight_dict, upper_threshold=200, normalize=False)

    def test_18(self):
        """
        Test AccessModel with custom lambda decay function
        """
        decay_function = lambda x, y: max((y - x) / y, 0)
        coverage_model = AccessModel('drive',
                                     sources_filename='tests/test_data/sources_a.csv',
                                     destinations_filename='tests/test_data/dests_b.csv',
                                     source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                          'population': 'pop'},
                                     dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                        'capacity': 'capacity', 'category': 'cat'},
                                     decay_function=decay_function)

        category_weight_dict = {'A': [5, 4, 3, 2, 1],
                                'D': [4, 3, 1]}
        coverage_model.calculate(category_weight_dict, upper_threshold=200, normalize=['A'])

        assert coverage_model.model_results['A_score'].max() == 100
        assert coverage_model.model_results['A_score'].min() >= 0

    def test_19(self):
        """
        Test the DestFloatingCatchmentAreaModel aggregation.
        """
        coverage_model = DestFloatingCatchmentArea('drive',
                                                   sources_filename='tests/test_data/sources_a.csv',
                                                   destinations_filename='tests/test_data/dests_b.csv',
                                                   source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                        'population': 'pop'},
                                                   dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                      'capacity': 'capacity', 'category': 'cat'},
                                                   categories=['A','C'])
        coverage_model.calculate(600)

        aggregate_df = coverage_model.aggregate(output_filename=self.datapath + 'test_19.json')
        with open(self.datapath + 'test_19.json', 'r') as file:
            aggregate_data = json.load(file)

        assert(aggregate_df.loc['HYDE PARK', 'percap_spending'] == aggregate_data['HYDE PARK']['percap_spending'])

        coverage_model.plot_cdf('percap_spending')
        coverage_model.plot_choropleth(column='percap_spending')

    def test_20(self):
        """
        Test TwoStageFloatingCatchmentArea aggregation.
        """
        categories = ['A', 'C']
        accesspop_model = TwoStageFloatingCatchmentArea('drive',
                                                        sources_filename='tests/test_data/sources_a.csv',
                                                        destinations_filename='tests/test_data/dests_b.csv',
                                                        source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                             'population': 'pop'},
                                                        dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                           'capacity': 'capacity', 'category': 'cat'},
                                                        categories=categories)
        accesspop_model.calculate(600)
        accesspop_model.aggregate()
        accesspop_model.plot_cdf('percap_spend')
        accesspop_model.plot_choropleth(column='percap_spend_A', include_destinations=False)

    def test_21(self):
        """
        Test AccessTime aggregation
        """
        categories = ['A', 'C']
        accesstime_model = AccessTime('drive',
                                      sources_filename='tests/test_data/sources_a.csv',
                                      destinations_filename='tests/test_data/dests_b.csv',
                                      source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                           'population': 'pop'},
                                      dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                         'capacity': 'capacity', 'category': 'cat'},
                                      categories=categories)
        accesstime_model.calculate()
        accesstime_model.aggregate('mean')
        accesstime_model.aggregate('min')
        accesstime_model.aggregate('max')
        accesstime_model.plot_cdf()
        accesstime_model.plot_choropleth(column='time_to_nearest_C', include_destinations=True)
        try:
            accesstime_model.aggregate('blah')
        except UnexpectedAggregationTypeException:
            return
        assert False

    def test_22(self):
        """
        Test AccessCount aggregation
        """
        categories = ['A', 'C', 'D']
        accesscount_model = AccessCount('drive',
                                        sources_filename='tests/test_data/sources_a.csv',
                                        destinations_filename='tests/test_data/dests_b.csv',
                                        source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                             'population': 'pop'},
                                        dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                           'capacity': 'capacity', 'category': 'cat'},
                                        categories=categories)
        accesscount_model.calculate(200)
        accesscount_model.aggregate()
        accesscount_model.plot_cdf()
        accesscount_model.plot_choropleth('count_in_range_C')

    def test_23(self):
        """
        Test AccessModel with aggregation.
        """
        coverage_model = AccessModel('drive',
                                     sources_filename='tests/test_data/sources_a.csv',
                                     destinations_filename='tests/test_data/dests_b.csv',
                                     source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                          'population': 'pop'},
                                     dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                        'capacity': 'capacity', 'category': 'cat'},
                                     decay_function='linear')

        category_weight_dict = {'A': [5, 4, 3, 2, 1],
                                'D': [4, 3, 1],
                                'C': [1]}
        coverage_model.calculate(category_weight_dict, upper_threshold=700, normalize=True)
        coverage_model.aggregate()
        coverage_model.plot_cdf('score')
        coverage_model.plot_cdf('good_access')
        coverage_model.plot_choropleth('A_good_access')
        coverage_model.plot_choropleth('C_score')

    def test_24(self):
        """
        Test get_results method
        """
        coverage_model = DestFloatingCatchmentArea('drive',
                                                   sources_filename='tests/test_data/sources_a.csv',
                                                   destinations_filename='tests/test_data/dests_b.csv',
                                                   source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                        'population': 'pop'},
                                                   dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                      'capacity': 'capacity', 'category': 'cat'})
        coverage_model.calculate(100)

        results = coverage_model.get_results()

        assert list(results.index) == ['place_a',
                                       'place_b',
                                       'place_c',
                                       'place_d',
                                       'place_e',
                                       'place_f']

    def test_25(self):
        """
        Test get_results
        """
        categories = ['A', 'C']
        accesspop_model = TwoStageFloatingCatchmentArea('drive',
                                                        sources_filename='tests/test_data/sources_a.csv',
                                                        destinations_filename='tests/test_data/dests_b.csv',
                                                        source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                             'population': 'pop'},
                                                        dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                           'capacity': 'capacity', 'category': 'cat'},
                                                        categories=categories)
        accesspop_model.calculate(200)
        results = accesspop_model.get_results()
        assert list(results.index) == [3, 4, 5, 6, 7, 8]

    def test_26(self):
        """
        Test AccessModel get_results.
        """
        coverage_model = AccessModel('drive',
                                     sources_filename='tests/test_data/sources_a.csv',
                                     destinations_filename='tests/test_data/dests_b.csv',
                                     source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                          'population': 'pop'},
                                     dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                        'capacity': 'capacity', 'category': 'cat'},
                                     decay_function='linear')

        category_weight_dict = {'A': [5, 4, 3, 2, 1],
                                'D': [4, 3, 1],
                                'C': [1]}
        coverage_model.calculate(category_weight_dict, upper_threshold=700, normalize=True)
        results = coverage_model.get_results()
        assert list(results.index) == [3, 4, 5, 6, 7, 8]

    def test_27(self):
        """
        Test AccessTime get_results
        """
        categories = ['A', 'C']
        accesstime_model = AccessTime('drive',
                                      sources_filename='tests/test_data/sources_a.csv',
                                      destinations_filename='tests/test_data/dests_b.csv',
                                      source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                           'population': 'pop'},
                                      dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                         'capacity': 'capacity', 'category': 'cat'},
                                      categories=categories)
        accesstime_model.calculate()
        results = accesstime_model.get_results()
        assert list(results.index) == [3, 4, 5, 6, 7, 8]

    def test_28(self):
        """
        Test AccessCount get_results
        """
        categories = ['A', 'C']
        accesscount_model = AccessCount('drive',
                                        sources_filename='tests/test_data/sources_a.csv',
                                        destinations_filename='tests/test_data/dests_b.csv',
                                        source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                             'population': 'pop'},
                                        dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                           'capacity': 'capacity', 'category': 'cat'},
                                        categories=categories)
        accesscount_model.calculate(200)
        results = accesscount_model.get_results()
        assert list(results.index) == [3, 4, 5, 6, 7, 8]
