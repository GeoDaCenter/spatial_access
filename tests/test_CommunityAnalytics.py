# pylint: skip-file
from spatial_access.CommunityAnalytics import Coverage
from spatial_access.SpatialAccessExceptions import UnrecognizedCategoriesException

# TODO add coverage for each model

class TestClass():
    """Suite of tests for the Community Analytics Package"""

    def test_1(self):
        """
        Test the CoverageModel through instantiation and
        calculate.
        """
        coverage_model = Coverage('drive',
                                       sources_filename='tests/test_data/sources.csv',
                                       destinations_filename='tests/test_data/dests.csv',
                                       source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                            'population': 'pop'},
                                       dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                          'target': 'targ', 'category': 'cat'},
                                       upper_threshold=600)
        coverage_model.calculate()

        assert True

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
                                           upper_threshold=600,
                                           categories=['A', 'C'])
            coverage_model.calculate()
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
                                       sources_filename='tests/test_data/sources.csv',
                                       destinations_filename='tests/test_data/dests.csv',
                                       source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                            'population': 'pop'},
                                       dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                          'target': 'targ', 'category': 'cat'},
                                       upper_threshold=600,
                                       categories=['A'])
        coverage_model.calculate()
        assert True


