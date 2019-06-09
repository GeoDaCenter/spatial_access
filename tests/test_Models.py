# pylint: skip-file
from spatial_access.Models import Coverage
from spatial_access.Models import TSFCA
from spatial_access.Models import AccessTime
from spatial_access.Models import AccessCount
from spatial_access.Models import AccessModel
from spatial_access.Models import AccessSum
from spatial_access.Models import DestSum
from spatial_access.SpatialAccessExceptions import UnrecognizedCategoriesException
from spatial_access.SpatialAccessExceptions import UnrecognizedDecayFunctionException
from spatial_access.SpatialAccessExceptions import IncompleteCategoryDictException
from spatial_access.SpatialAccessExceptions import UnexpectedAggregationTypeException
from spatial_access.SpatialAccessExceptions import UnexpectedPlotColumnException

import json

def almost_equal(a, b):
    return abs(a - b) < 0.001

class TestClass:
    """Suite of tests for the Community Analytics Package"""

    def setup_class(self):
        import os
        self.datapath = 'test_community_analytics_temp/'
        if not os.path.exists(self.datapath):
            os.mkdir(self.datapath)

    def teardown_class(self):
        import os
        if os.path.exists(self.datapath):
            import shutil
            shutil.rmtree(self.datapath)

    def mock_transit_matrix_values(self, transit_matrix):
        source_ids = [3, 4, 5, 6, 7, 8]
        dest_ids = ['place_a', 'place_b', 'place_c', 'place_d', 'place_e', 'place_f']
        dataset = [[100, 100, 100, 100, 100, 100],
                   [200, 200, 200, 200, 200, 200],
                   [300, 300, 300, 300, 300, 300],
                   [400, 400, 400, 400, 400, 400],
                   [500, 500, 500, 500, 500, 500],
                   [600, 600, 600, 600, 600, 600]]

        transit_matrix.matrix_interface._set_mock_data_frame(dataset, source_ids, dest_ids)

        return transit_matrix

    def test_01(self):
        """
        Test the Coverage model through instantiation and
        calculate.
        """
        coverage_model = Coverage('drive',
                                  sources_filename='tests/test_data/sources_a.csv',
                                  destinations_filename='tests/test_data/dests_b.csv',
                                  source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                        'population': 'pop'},
                                  dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                      'capacity': 'capacity', 'category': 'cat'})
        coverage_model.transit_matrix = self.mock_transit_matrix_values(coverage_model.transit_matrix)
        coverage_model.calculate(400)

        for row in coverage_model.model_results.itertuples():
            assert row[1] == 166

    def test_02(self):
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
        coverage_model = Coverage('drive',
                                  sources_filename='tests/test_data/sources_a.csv',
                                  destinations_filename='tests/test_data/dests_b.csv',
                                  source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                        'population': 'pop'},
                                  dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                      'capacity': 'capacity', 'category': 'cat'},
                                  categories=['A', 'C'])
        coverage_model.calculate(600)


        assert set(coverage_model.model_results.index) == {'place_a',
                                                           'place_c',
                                                           'place_d',
                                                           'place_e',
                                                           'place_f'}

    def test_4(self):
        """
        Test TSFCA through instantiation and
        calculate.
        """
        accesspop_model = TSFCA('drive',
                                sources_filename='tests/test_data/sources_a.csv',
                                destinations_filename='tests/test_data/dests_b.csv',
                                source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                             'population': 'pop'},
                                dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                           'capacity': 'capacity', 'category': 'cat'})
        accesspop_model.transit_matrix = self.mock_transit_matrix_values(accesspop_model.transit_matrix)
        accesspop_model.calculate(300)

        for i in range(3, 6):
            assert almost_equal(accesspop_model.model_results.loc[i]['percap_spend_D'], 0.2771)
            assert almost_equal(accesspop_model.model_results.loc[i]['percap_spend_C'], 3.4457)
            assert almost_equal(accesspop_model.model_results.loc[i]['percap_spend_A'], 5.8915)

        for i in range(6, 9):
            assert almost_equal(accesspop_model.model_results.loc[i]['percap_spend_D'], 0)
            assert almost_equal(accesspop_model.model_results.loc[i]['percap_spend_C'], 0)
            assert almost_equal(accesspop_model.model_results.loc[i]['percap_spend_A'], 0)

    def test_5(self):
        """
        Expects UnrecognizedCategoriesException to
        throw because the user supplies categories
        which are not present in the data
        """
        try:
            accesspop_model = TSFCA('drive',
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
        Test TSFCA through instantiation and
        calculate, with categories specified.
        """
        categories = ['A', 'C']
        accesspop_model = TSFCA('drive',
                                sources_filename='tests/test_data/sources_a.csv',
                                destinations_filename='tests/test_data/dests_b.csv',
                                source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                             'population': 'pop'},
                                dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                           'capacity': 'capacity', 'category': 'cat'},
                                categories=categories)
        accesspop_model.transit_matrix = self.mock_transit_matrix_values(accesspop_model.transit_matrix)
        accesspop_model.calculate(200)

        for i in range(3, 5):
            assert almost_equal(accesspop_model.model_results.loc[i, 'percap_spend_A'], 12.8684)
            assert almost_equal(accesspop_model.model_results.loc[i, 'percap_spend_C'], 7.5262)

        for i in range(5, 9):
            assert almost_equal(accesspop_model.model_results.loc[i, 'percap_spend_A'], 0.0)
            assert almost_equal(accesspop_model.model_results.loc[i, 'percap_spend_C'], 0.0)


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
        accesstime_model.transit_matrix = self.mock_transit_matrix_values(accesstime_model.transit_matrix)
        accesstime_model.calculate()


        assert accesstime_model.model_results.loc[3]['time_to_nearest_A'] == 100
        assert accesstime_model.model_results.loc[4]['time_to_nearest_A'] == 200
        assert accesstime_model.model_results.loc[5]['time_to_nearest_A'] == 300
        assert accesstime_model.model_results.loc[6]['time_to_nearest_A'] == 400
        assert accesstime_model.model_results.loc[7]['time_to_nearest_A'] == 500
        assert accesstime_model.model_results.loc[8]['time_to_nearest_A'] == 600

        assert accesstime_model.model_results.loc[3]['time_to_nearest_D'] == 100
        assert accesstime_model.model_results.loc[4]['time_to_nearest_D'] == 200
        assert accesstime_model.model_results.loc[5]['time_to_nearest_D'] == 300
        assert accesstime_model.model_results.loc[6]['time_to_nearest_D'] == 400
        assert accesstime_model.model_results.loc[7]['time_to_nearest_D'] == 500
        assert accesstime_model.model_results.loc[8]['time_to_nearest_D'] == 600

        assert accesstime_model.model_results.loc[3]['time_to_nearest_C'] == 100
        assert accesstime_model.model_results.loc[4]['time_to_nearest_C'] == 200
        assert accesstime_model.model_results.loc[5]['time_to_nearest_C'] == 300
        assert accesstime_model.model_results.loc[6]['time_to_nearest_C'] == 400
        assert accesstime_model.model_results.loc[7]['time_to_nearest_C'] == 500
        assert accesstime_model.model_results.loc[8]['time_to_nearest_C'] == 600

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
        accesstime_model.transit_matrix = self.mock_transit_matrix_values(accesstime_model.transit_matrix)
        accesstime_model.calculate()

        assert accesstime_model.model_results.loc[3]['time_to_nearest_A'] == 100
        assert accesstime_model.model_results.loc[4]['time_to_nearest_A'] == 200
        assert accesstime_model.model_results.loc[5]['time_to_nearest_A'] == 300
        assert accesstime_model.model_results.loc[6]['time_to_nearest_A'] == 400
        assert accesstime_model.model_results.loc[7]['time_to_nearest_A'] == 500
        assert accesstime_model.model_results.loc[8]['time_to_nearest_A'] == 600

        assert accesstime_model.model_results.loc[3]['time_to_nearest_C'] == 100
        assert accesstime_model.model_results.loc[4]['time_to_nearest_C'] == 200
        assert accesstime_model.model_results.loc[5]['time_to_nearest_C'] == 300
        assert accesstime_model.model_results.loc[6]['time_to_nearest_C'] == 400
        assert accesstime_model.model_results.loc[7]['time_to_nearest_C'] == 500
        assert accesstime_model.model_results.loc[8]['time_to_nearest_C'] == 600

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
            return
        assert False

    def test_12(self):
        """
        Test AccessCount through instantiation and
        calculate, with categories specified.
        """
        categories = ['A']
        accesscount_model = AccessCount('drive',
                                        sources_filename='tests/test_data/sources_a.csv',
                                        destinations_filename='tests/test_data/dests_b.csv',
                                        source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                             'population': 'pop'},
                                        dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                           'capacity': 'capacity', 'category': 'cat'},
                                        categories=categories)
        accesscount_model.transit_matrix = self.mock_transit_matrix_values(
            accesscount_model.transit_matrix)
        accesscount_model.calculate(400)

        assert accesscount_model.model_results.loc[3]['count_in_range_A'] == 3
        assert accesscount_model.model_results.loc[4]['count_in_range_A'] == 3
        assert accesscount_model.model_results.loc[5]['count_in_range_A'] == 3
        assert accesscount_model.model_results.loc[6]['count_in_range_A'] == 3
        assert accesscount_model.model_results.loc[7]['count_in_range_A'] == 0
        assert accesscount_model.model_results.loc[8]['count_in_range_A'] == 0

        assert set(accesscount_model.model_results.columns) == {'count_in_range_A', 'count_in_range_all_categories'}

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
            access_model.calculate(category_weight_dict=category_weight_dict, upper_threshold=200)
            assert False
        except IncompleteCategoryDictException:
            assert True

        try:
            category_weight_dict = {'A': [1, 2, 3, 4], 'D': 4, 'C': [5, 6, 8, 5, 3]}
            access_model.calculate(category_weight_dict=category_weight_dict, upper_threshold=200)
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
        coverage_model.transit_matrix = self.mock_transit_matrix_values(coverage_model.transit_matrix)
        coverage_model.calculate(category_weight_dict=category_weight_dict, upper_threshold=700, normalize=True,
                                 normalize_type='z_score')

        assert almost_equal(coverage_model.model_results['all_categories_score'].max(), 1.336)
        assert almost_equal(coverage_model.model_results['all_categories_score'].min(), -1.336)

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
        coverage_model.transit_matrix = self.mock_transit_matrix_values(coverage_model.transit_matrix)
        coverage_model.calculate(category_weight_dict=category_weight_dict, upper_threshold=200, normalize=False)

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
        coverage_model.transit_matrix = self.mock_transit_matrix_values(coverage_model.transit_matrix)
        coverage_model.calculate(category_weight_dict=category_weight_dict, upper_threshold=200, normalize=['A'],
                                 normalize_type='z_score')

        assert almost_equal(coverage_model.model_results['A_score'].max(), 2.041)
        assert almost_equal(coverage_model.model_results['A_score'].min(), -0.408)

        coverage_model.calculate(category_weight_dict=category_weight_dict, upper_threshold=200, normalize=True,
                                 normalize_type='minmax')
        assert almost_equal(coverage_model.model_results['A_score'].max(), 1.0)
        assert almost_equal(coverage_model.model_results['A_score'].min(), 0.0)
        assert almost_equal(coverage_model.model_results['D_score'].max(), 1.0)
        assert almost_equal(coverage_model.model_results['D_score'].min(), 0.0)


    def test_19(self):
        """
        Test the DestFloatingCatchmentAreaModel aggregation.
        """
        coverage_model = Coverage('drive',
                                  sources_filename='tests/test_data/sources_a.csv',
                                  destinations_filename='tests/test_data/dests_b.csv',
                                  source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                        'population': 'pop'},
                                  dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                      'capacity': 'capacity', 'category': 'cat'},
                                  categories=['A','C'])
        coverage_model.transit_matrix = self.mock_transit_matrix_values(
            coverage_model.transit_matrix)
        coverage_model.calculate(600)

        aggregate_df = coverage_model.aggregate()
        coverage_model.write_aggregated_results(self.datapath + 'test_19.json')
        with open(self.datapath + 'test_19.json', 'r') as file:
            aggregate_data = json.load(file)

        assert(aggregate_df.loc['HYDE PARK', 'percap_spending'] == aggregate_data['HYDE PARK']['percap_spending'])

        coverage_model.plot_cdf('percap_spending', filename=self.datapath + "test_19_a.png")
        coverage_model.plot_choropleth(column='percap_spending', filename=self.datapath + "test_19_b.png")

    def test_20(self):
        """
        Test TSFCA aggregation.
        """
        categories = ['A', 'C']
        accesspop_model = TSFCA('drive',
                                sources_filename='tests/test_data/sources_a.csv',
                                destinations_filename='tests/test_data/dests_b.csv',
                                source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                             'population': 'pop'},
                                dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                           'capacity': 'capacity', 'category': 'cat'},
                                categories=categories)
        accesspop_model.transit_matrix = self.mock_transit_matrix_values(
            accesspop_model.transit_matrix)
        accesspop_model.calculate(600)
        accesspop_model.aggregate()
        accesspop_model.plot_cdf('percap_spend', filename=self.datapath + 'test_20_a.png')
        accesspop_model.plot_choropleth(column='percap_spend_A', include_destinations=False,
                                        filename=self.datapath + 'test_20_b.png')

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
        accesstime_model.transit_matrix = self.mock_transit_matrix_values(
            accesstime_model.transit_matrix)
        accesstime_model.calculate()
        accesstime_model.aggregate(aggregation_type='mean')
        accesstime_model.aggregate(aggregation_type='min')
        accesstime_model.aggregate(aggregation_type='max')
        accesstime_model.plot_cdf(plot_type='time_to_nearest',filename=self.datapath + 'test_21_a.png')
        accesstime_model.plot_choropleth(column='time_to_nearest_C', include_destinations=True,
                                         filename=self.datapath + 'test_21_b.png')
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
        accesscount_model.transit_matrix = self.mock_transit_matrix_values(
            accesscount_model.transit_matrix)
        accesscount_model.calculate(200)
        accesscount_model.aggregate()
        accesscount_model.plot_cdf( filename=self.datapath + 'test_22_a.png')
        accesscount_model.plot_choropleth('count_in_range_C', filename=self.datapath + 'test_22_b.png')

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
        coverage_model.transit_matrix = self.mock_transit_matrix_values(
            coverage_model.transit_matrix)
        coverage_model.calculate(category_weight_dict=category_weight_dict, upper_threshold=700, normalize=True)
        coverage_model.aggregate()
        coverage_model.plot_cdf(filename=self.datapath + 'test_23_a.png')
        coverage_model.plot_choropleth('C_score', filename=self.datapath + 'test_23_d.png')


    def test_24(self):
        """
        Test AccessModel with aggregation and only some
        category weights specified.
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
                                'C': [1]}
        coverage_model.transit_matrix = self.mock_transit_matrix_values(
            coverage_model.transit_matrix)
        coverage_model.calculate(category_weight_dict=category_weight_dict, upper_threshold=700, normalize=True)
        coverage_model.aggregate()
        coverage_model.plot_cdf(filename=self.datapath + 'test_23_a.png')
        coverage_model.plot_choropleth('C_score', filename=self.datapath + 'test_23_d.png')

    def test_25(self):
        """
        Test get_results method
        """
        coverage_model = Coverage('drive',
                                  sources_filename='tests/test_data/sources_a.csv',
                                  destinations_filename='tests/test_data/dests_b.csv',
                                  source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                        'population': 'pop'},
                                  dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                      'capacity': 'capacity', 'category': 'cat'})
        coverage_model.transit_matrix = self.mock_transit_matrix_values(
            coverage_model.transit_matrix)
        results = coverage_model.calculate(100)


        assert set(results.index) == {'place_a',
                                       'place_b',
                                       'place_c',
                                       'place_d',
                                       'place_e',
                                       'place_f'}

    def test_26(self):
        """
        Test get_results
        """
        categories = ['A', 'C']
        accesspop_model = TSFCA('drive',
                                sources_filename='tests/test_data/sources_a.csv',
                                destinations_filename='tests/test_data/dests_b.csv',
                                source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                             'population': 'pop'},
                                dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                                           'capacity': 'capacity', 'category': 'cat'},
                                categories=categories)
        accesspop_model.transit_matrix = self.mock_transit_matrix_values(
            accesspop_model.transit_matrix)
        results = accesspop_model.calculate(200)

        assert list(results.index) == [3, 4, 5, 6, 7, 8]

    def test_27(self):
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
        coverage_model.transit_matrix = self.mock_transit_matrix_values(
            coverage_model.transit_matrix)
        results = coverage_model.calculate(category_weight_dict=category_weight_dict, upper_threshold=700, normalize=True)

        assert list(results.index) == [3, 4, 5, 6, 7, 8]

    def test_28(self):
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
        accesstime_model.transit_matrix = self.mock_transit_matrix_values(
            accesstime_model.transit_matrix)
        results = accesstime_model.calculate()

        assert list(results.index) == [3, 4, 5, 6, 7, 8]

    def test_29(self):
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
        accesscount_model.transit_matrix = self.mock_transit_matrix_values(accesscount_model.transit_matrix)
        results = accesscount_model.calculate(200)

        assert list(results.index) == [3, 4, 5, 6, 7, 8]

    def test_30(self):
        """
        Test AccessSum calculate and aggregate
        """

        categories = ['A', 'D']
        access_sum_model = AccessSum('drive',
                                     sources_filename='tests/test_data/sources_a.csv',
                                     destinations_filename='tests/test_data/dests_b.csv',
                                     source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                          'population': 'pop'},
                                     dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                        'capacity': 'capacity', 'category': 'cat'},
                                     categories=categories)
        access_sum_model.transit_matrix = self.mock_transit_matrix_values(access_sum_model.transit_matrix)
        access_sum_model.calculate(100)

        access_sum_model.aggregate()

        access_sum_model.plot_cdf(filename=self.datapath + 'test_29_a.png')

        access_sum_model.plot_choropleth(column='sum_in_range_A', filename=self.datapath + 'test_29_b.png')

        try:
            access_sum_model.plot_choropleth(column='not_a_column', filename=self.datapath + 'test_29_b.png')
            assert False
        except UnexpectedPlotColumnException:
            pass

        assert set(access_sum_model.aggregated_results.columns.values) == {'sum_in_range_A', 'sum_in_range_D',
                                                                           'sum_in_range_all_categories'}
        assert almost_equal(access_sum_model.aggregated_results.loc["HYDE PARK", "sum_in_range_A"], 163)
        assert almost_equal(access_sum_model.aggregated_results.loc["HYDE PARK", "sum_in_range_D"], 7.666)

        assert access_sum_model.model_results.loc[3]['sum_in_range_A'] == 978
        assert access_sum_model.model_results.loc[3]['sum_in_range_D'] == 46

        for i in range(4, 9):
            assert access_sum_model.model_results.loc[i]['sum_in_range_A'] == 0
            assert access_sum_model.model_results.loc[i]['sum_in_range_D'] == 0


    def test_31(self):
        """
        Test DestSum calculation and aggregation.
        """

        dest_sum_model = DestSum('drive',
                                   sources_filename='tests/test_data/sources_a.csv',
                                   destinations_filename='tests/test_data/dests_b.csv',
                                   source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                        'population': 'pop'},
                                   dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                      'capacity': 'capacity', 'category': 'cat'})
        model_results = dest_sum_model.calculate()
        dest_sum_model.plot_choropleth(column='A_per_capita', filename=self.datapath + 'test_30_a.png')
        assert almost_equal(model_results.loc["HYDE PARK", 'A'], 978.0)
        assert almost_equal(model_results.loc["HYDE PARK", 'D'] , 46.0)
        assert almost_equal(model_results.loc["HYDE PARK", 'C'], 572.0)
        assert almost_equal(model_results.loc["HYDE PARK", 'all_categories'], 1596.0)
        assert almost_equal(model_results.loc["HYDE PARK", 'A_per_capita'], 2.0853)
        assert almost_equal(model_results.loc["HYDE PARK", 'D_per_capita'], 0.099)
        assert almost_equal(model_results.loc["HYDE PARK", 'C_per_capita'], 1.2197)
        assert almost_equal(model_results.loc["HYDE PARK", 'all_categories_per_capita'], 3.403)

    def test_32(self):
        coverage_model = AccessModel('drive',
                                     sources_filename='tests/test_data/sources_a.csv',
                                     destinations_filename='tests/test_data/dests_b.csv',
                                     source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                          'population': 'pop'},
                                     dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                        'capacity': 'capacity', 'category': 'cat'},
                                     decay_function='linear')


        coverage_model.transit_matrix = self.mock_transit_matrix_values(
            coverage_model.transit_matrix)
        results = coverage_model.calculate(upper_threshold=700, normalize=True)

        assert list(results.index) == [3, 4, 5, 6, 7, 8]