# pylint: skip-file
from spatial_access.CommunityAnalytics import Coverage
from spatial_access.CommunityAnalytics import AccessPop
from spatial_access.CommunityAnalytics import AccessTime
from spatial_access.CommunityAnalytics import AccessCount
from spatial_access.CommunityAnalytics import AccessModel
from spatial_access.SpatialAccessExceptions import UnrecognizedCategoriesException
from spatial_access.SpatialAccessExceptions import UnrecognizedDecayFunctionException
from spatial_access.SpatialAccessExceptions import IncompleteCategoryDictException

# TODO add coverage for each model


class TestClass():
    """Suite of tests for the Community Analytics Package"""

    def test_1(self):
        """
        Test the CoverageModel through instantiation and
        calculate.
        """
        coverage_model = Coverage('drive',
                                  sources_filename='tests/test_data/sources_a.csv',
                                  destinations_filename='tests/test_data/dests_b.csv',
                                  source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                       'population': 'pop'},
                                  dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                     'target': 'targ', 'category': 'cat'})
        coverage_model.calculate(600)

        assert coverage_model.model_results.loc[0]['service_pop'] == 0
        assert coverage_model.model_results.loc[1]['service_pop'] == 244
        assert coverage_model.model_results.loc[2]['service_pop'] == 424
        assert coverage_model.model_results.loc[3]['service_pop'] == 0
        assert coverage_model.model_results.loc[4]['service_pop'] == 244
        assert coverage_model.model_results.loc[5]['service_pop'] == 424

        assert coverage_model.model_results.loc[0]['percap_spending'] <= 0.000
        assert coverage_model.model_results.loc[1]['percap_spending'] <= 0.189
        assert coverage_model.model_results.loc[2]['percap_spending'] <= 0.817
        assert coverage_model.model_results.loc[3]['percap_spending'] <= 0.000
        assert coverage_model.model_results.loc[4]['percap_spending'] <= 1.640
        assert coverage_model.model_results.loc[5]['percap_spending'] <= 1.338

        assert coverage_model.model_results.loc[0]['percap_spending'] >= 0.000
        assert coverage_model.model_results.loc[1]['percap_spending'] >= 0.188
        assert coverage_model.model_results.loc[2]['percap_spending'] >= 0.816
        assert coverage_model.model_results.loc[3]['percap_spending'] >= 0.000
        assert coverage_model.model_results.loc[4]['percap_spending'] >= 1.639
        assert coverage_model.model_results.loc[5]['percap_spending'] >= 1.337

    def test_2(self):
        """
        Expects UnrecognizedCategoriesException to
        throw because the user supplies categories
        which are not present in the data
        """
        try:
            coverage_model = Coverage('drive',
                                           sources_filename='tests/test_data/sources.csv',
                                           destinations_filename='tests/test_data/dests.csv',
                                           source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                'population': 'pop'},
                                           dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                              'target': 'targ', 'category': 'cat'},
                                           categories=['A', 'C'])
            coverage_model.calculate(600)
        except UnrecognizedCategoriesException:
            assert True
            return
        assert False

    def test_3(self):
        """
        Test the CoverageModel through instantiation and
        calculate, with categories specified.
        """
        coverage_model = Coverage('drive',
                                  sources_filename='tests/test_data/sources_a.csv',
                                  destinations_filename='tests/test_data/dests_b.csv',
                                  source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                       'population': 'pop'},
                                  dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                     'target': 'targ', 'category': 'cat'},
                                  categories=['A','C'])
        coverage_model.calculate(600)

        remapped_dests = coverage_model.model_data.get_remapped_dest_ids()

        assert set(coverage_model.model_results.index) == set([remapped_dests['place_a'],
                                                              remapped_dests['place_c'],
                                                              remapped_dests['place_d'],
                                                              remapped_dests['place_e'],
                                                              remapped_dests['place_f']])

    def test_4(self):
        """
        Test AccessPop through instantiation and
        calculate.
        """
        accesspop_model = AccessPop('drive',
                                   sources_filename='tests/test_data/sources_a.csv',
                                   destinations_filename='tests/test_data/dests_b.csv',
                                   source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                        'population': 'pop'},
                                   dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                      'target': 'targ', 'category': 'cat'})
        accesspop_model.calculate(600)

        assert accesspop_model.model_results.loc[3]['percap_spend_all_categories'] >= 0.000
        assert accesspop_model.model_results.loc[4]['percap_spend_all_categories'] >= 3.981
        assert accesspop_model.model_results.loc[5]['percap_spend_all_categories'] >= 3.981
        assert accesspop_model.model_results.loc[6]['percap_spend_all_categories'] >= 0
        assert accesspop_model.model_results.loc[7]['percap_spend_all_categories'] >= 2.153
        assert accesspop_model.model_results.loc[8]['percap_spend_all_categories'] >= 3.981

        assert accesspop_model.model_results['total_spend_all_categories'].sum() <= accesspop_model.model_data.dests['target'].sum()

    def test_5(self):
        """
        Expects UnrecognizedCategoriesException to
        throw because the user supplies categories
        which are not present in the data
        """
        try:
            accesspop_model = AccessPop('drive',
                                       sources_filename='tests/test_data/sources.csv',
                                       destinations_filename='tests/test_data/dests.csv',
                                       source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                            'population': 'pop'},
                                       dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                          'target': 'targ', 'category': 'cat'},
                                       categories=['A', 'E'])
            accesspop_model.calculate(600)
        except UnrecognizedCategoriesException:
            assert True
            return
        assert False

    def test_6(self):
        """
        Test AccessPop through instantiation and
        calculate, with categories specified.
        """
        categories = ['A', 'C']
        accesspop_model = AccessPop('drive',
                                   sources_filename='tests/test_data/sources_a.csv',
                                   destinations_filename='tests/test_data/dests_b.csv',
                                   source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                        'population': 'pop'},
                                   dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                      'target': 'targ', 'category': 'cat'},
                                   categories=categories)
        accesspop_model.calculate(600)

        assert len(accesspop_model.model_results.columns) == len(categories) * 2
        cat_a_dests = accesspop_model.model_data.dests[accesspop_model.model_data.dests['category'] == 'A']
        cat_c_dests = accesspop_model.model_data.dests[accesspop_model.model_data.dests['category'] == 'C']

        assert accesspop_model.model_results['total_spend_A'].sum() <= cat_a_dests['target'].sum()
        assert accesspop_model.model_results['total_spend_C'].sum() <= cat_c_dests['target'].sum()


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
                                                      'target': 'targ', 'category': 'cat'})
        accesstime_model.calculate()

        assert accesstime_model.model_results.loc[3]['time_to_nearest_all_categories'] == 601
        assert accesstime_model.model_results.loc[4]['time_to_nearest_all_categories'] == 7
        assert accesstime_model.model_results.loc[5]['time_to_nearest_all_categories'] == 21
        assert accesstime_model.model_results.loc[6]['time_to_nearest_all_categories'] == 569
        assert accesstime_model.model_results.loc[7]['time_to_nearest_all_categories'] == 570
        assert accesstime_model.model_results.loc[8]['time_to_nearest_all_categories'] == 22

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
                                                          'target': 'targ', 'category': 'cat'},
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
                                                      'target': 'targ', 'category': 'cat'},
                                   categories=categories)
        accesstime_model.calculate()




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
                                                      'target': 'targ', 'category': 'cat'})
        accesscount_model.calculate(700)

        assert accesscount_model.model_results.loc[3]['count_in_range_all_categories'] == 2
        assert accesscount_model.model_results.loc[4]['count_in_range_all_categories'] == 4
        assert accesscount_model.model_results.loc[5]['count_in_range_all_categories'] == 4
        assert accesscount_model.model_results.loc[6]['count_in_range_all_categories'] == 4
        assert accesscount_model.model_results.loc[7]['count_in_range_all_categories'] == 4
        assert accesscount_model.model_results.loc[8]['count_in_range_all_categories'] == 4

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
                                                          'target': 'targ', 'category': 'cat'},
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
                                                      'target': 'targ', 'category': 'cat'},
                                   categories=categories)
        accesscount_model.calculate(200)

        assert accesscount_model.model_results.loc[3]['count_in_range_A'] == 0
        assert accesscount_model.model_results.loc[4]['count_in_range_A'] == 1
        assert accesscount_model.model_results.loc[5]['count_in_range_A'] == 1
        assert accesscount_model.model_results.loc[6]['count_in_range_A'] == 0
        assert accesscount_model.model_results.loc[7]['count_in_range_A'] == 0
        assert accesscount_model.model_results.loc[8]['count_in_range_A'] == 1

        assert accesscount_model.model_results.loc[3]['count_in_range_C'] == 0
        assert accesscount_model.model_results.loc[4]['count_in_range_C'] == 0
        assert accesscount_model.model_results.loc[5]['count_in_range_C'] == 0
        assert accesscount_model.model_results.loc[6]['count_in_range_C'] == 0
        assert accesscount_model.model_results.loc[7]['count_in_range_C'] == 0
        assert accesscount_model.model_results.loc[8]['count_in_range_C'] == 0

        assert accesscount_model.model_results.loc[3]['count_in_range_D'] == 0
        assert accesscount_model.model_results.loc[4]['count_in_range_D'] == 1
        assert accesscount_model.model_results.loc[5]['count_in_range_D'] == 1
        assert accesscount_model.model_results.loc[6]['count_in_range_D'] == 0
        assert accesscount_model.model_results.loc[7]['count_in_range_D'] == 0
        assert accesscount_model.model_results.loc[8]['count_in_range_D'] == 1

        accesscount_model.calculate(700)

        assert accesscount_model.model_results.loc[3]['count_in_range_A'] == 1
        assert accesscount_model.model_results.loc[4]['count_in_range_A'] == 2
        assert accesscount_model.model_results.loc[5]['count_in_range_A'] == 2
        assert accesscount_model.model_results.loc[6]['count_in_range_A'] == 2
        assert accesscount_model.model_results.loc[7]['count_in_range_A'] == 2
        assert accesscount_model.model_results.loc[8]['count_in_range_A'] == 2

        assert accesscount_model.model_results.loc[3]['count_in_range_C'] == 1
        assert accesscount_model.model_results.loc[4]['count_in_range_C'] == 1
        assert accesscount_model.model_results.loc[5]['count_in_range_C'] == 1
        assert accesscount_model.model_results.loc[6]['count_in_range_C'] == 1
        assert accesscount_model.model_results.loc[7]['count_in_range_C'] == 1
        assert accesscount_model.model_results.loc[8]['count_in_range_C'] == 1

        assert accesscount_model.model_results.loc[3]['count_in_range_D'] == 0
        assert accesscount_model.model_results.loc[4]['count_in_range_D'] == 1
        assert accesscount_model.model_results.loc[5]['count_in_range_D'] == 1
        assert accesscount_model.model_results.loc[6]['count_in_range_D'] == 1
        assert accesscount_model.model_results.loc[7]['count_in_range_D'] == 1
        assert accesscount_model.model_results.loc[8]['count_in_range_D'] == 1

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
                                                      'target': 'targ', 'category': 'cat'},
                                   decay_function='quadratic')
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
                                                      'target': 'targ', 'category': 'cat'},
                                   decay_function=lambda x : x ** 2)
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
                                                      'target': 'targ', 'category': 'cat'},
                                   decay_function='linear')
        try:
            category_weight_dict = [1, 2, 4, 5]
            access_model.calculate(category_weight_dict, upper_threshold=200)
            assert False
        except IncompleteCategoryDictException:
            assert True

        try:
            category_weight_dict = {'A':[1, 2, 3, 4], 'D':4, 'C':[5,6,8,5,3]}
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
                                                        'target': 'targ', 'category': 'cat'},
                                     decay_function='linear')
        coverage_model.model_data._print_data_frame()
        category_weight_dict = {'A': [5, 4, 3, 2, 1],
                                'D': [4, 3, 1],
                                'C': [1]}
        coverage_model.calculate(category_weight_dict, upper_threshold=700, normalize=True)

        assert coverage_model.model_results['score'].max() == 100
        assert coverage_model.model_results['score'].min() >= 0

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
                                                        'target': 'targ', 'category': 'cat'},
                                     decay_function='linear')
        coverage_model.model_data._print_data_frame()
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
                                                        'target': 'targ', 'category': 'cat'},
                                     decay_function=decay_function)
        coverage_model.model_data._print_data_frame()
        category_weight_dict = {'A': [5, 4, 3, 2, 1],
                                'D': [4, 3, 1]}
        coverage_model.calculate(category_weight_dict, upper_threshold=200, normalize=True)

        assert coverage_model.model_results['score'].max() == 100
        assert coverage_model.model_results['score'].min() >= 0