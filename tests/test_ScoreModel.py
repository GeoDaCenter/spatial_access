# pylint: skip-file

from spatial_access.ScoreModel import ModelData
from spatial_access.SpatialAccessExceptions import SourceDataNotFoundException
from spatial_access.SpatialAccessExceptions import DestDataNotFoundException
from spatial_access.SpatialAccessExceptions import SourceDataNotParsableException
from spatial_access.SpatialAccessExceptions import DestDataNotParsableException

# TODO debug these tests


class TestClass():
    """
    Suite of tests for ScoreModel
    """

    def test_1(self):
        """
        Test instantiating and processing ModelData
        instance and calling load_sp_matrix with
        complete source_column_names and dest_column_names,
        and no precomputed sp_matrix.
        """
        modelData = ModelData('drive',sources_filename="tests/test_data/sources.csv",
                              destinations_filename="tests/test_data/dests.csv",
                              source_column_names={'idx':'name', 'ycol':'lat', 'xcol':'lon',
                                                   'population':'pop'},
                              dest_column_names={'idx': 'name', 'ycol': 'lat', 'xcol': 'lon',
                                                 'target':'targ', 'category':'cat'},
                              upper_threshold=100)
        modelData.load_sp_matrix()

        modelData.sp_matrix.write_tmx('tests/test_data/score_model_test_1')

        assert True

    def test_2(self):
        """
        Test instantiating and processing ModelData
        instance and calling load_sp_matrix with
        complete source_column_names and dest_column_names,
        but with a precomputed sp matrix.
        """
        modelData = ModelData('drive', sources_filename="tests/test_data/sources.csv",
                              destinations_filename="tests/test_data/dests.csv",
                              source_column_names={'idx': 'name', 'ycol': 'lat', 'xcol': 'lon',
                                                   'population': 'skip'},
                              dest_column_names={'idx': 'name', 'ycol': 'lat', 'xcol': 'lon',
                                                 'target': 'skip', 'category': 'skip'},
                              upper_threshold=100)
        modelData.load_sp_matrix("tests/test_data/score_model_test_1")

        assert True

    def test_3(self):
        """
        Tests that SourceDataNotFoundException is thrown
        when source data does not exist
        """
        try:
            model_data = ModelData('drive', sources_filename="tests/test_data/nonexistant.csv",
                                   destinations_filename="tests/test_data/dests.csv",
                                   source_column_names={'idx': 'name', 'ycol': 'lat', 'xcol': 'lon',
                                                        'population': 'skip'},
                                   dest_column_names={'idx': 'name', 'ycol': 'lat', 'xcol': 'lon',
                                                      'target': 'skip', 'category': 'skip'},
                                   upper_threshold=100)
            model_data.load_sp_matrix()
        except SourceDataNotFoundException:
            assert True
            return
        assert False

    def test_4(self):
        """
        Tests that DestDataNotFoundException is thrown
        when source data does not exist
        """
        try:
            model_data = ModelData('drive', sources_filename="tests/test_data/sources.csv",
                                   destinations_filename="tests/test_data/nonexistant.csv",
                                   source_column_names={'idx': 'name', 'ycol': 'lat', 'xcol': 'lon',
                                                        'population': 'skip'},
                                   dest_column_names={'idx': 'name', 'ycol': 'lat', 'xcol': 'lon',
                                                      'target': 'skip', 'category': 'skip'},
                                   upper_threshold=100)
            model_data.load_sp_matrix()
        except DestDataNotFoundException:
            assert True
            return
        assert False

    def test_5(self):
        """
        Tests that SourceDataNotParsableException is thrown
        when source_column_names is not accurate
        """
        try:
            model_data = ModelData('drive', sources_filename="tests/test_data/sources.csv",
                                   destinations_filename="tests/test_data/dests.csv",
                                   source_column_names={'idx': 'nonexistant', 'ycol': 'lat', 'xcol': 'lon',
                                                        'population': 'skip'},
                                   dest_column_names={'idx': 'name', 'ycol': 'lat', 'xcol': 'lon',
                                                      'target': 'skip', 'category': 'skip'},
                                   upper_threshold=100)
            model_data.load_sp_matrix('tests/test_data/score_model_test_1')
        except SourceDataNotParsableException:
            assert True
            return
        assert False

    def test_6(self):
        """
        Tests that DestDataNotParsableException is thrown
        when dest_column_names is not accurate
        """
        try:
            model_data = ModelData('drive', sources_filename="tests/test_data/sources.csv",
                                   destinations_filename="tests/test_data/dests.csv",
                                   source_column_names={'idx': 'name', 'ycol': 'lat', 'xcol': 'lon',
                                                        'population': 'skip'},
                                   dest_column_names={'idx': 'name', 'ycol': 'unrecognized', 'xcol': 'lon',
                                                      'target': 'skip', 'category': 'skip'},
                                   upper_threshold=100)
            model_data.load_sp_matrix('tests/test_data/score_model_test_1')
        except DestDataNotParsableException:
            assert True
            return
        assert False

