# pylint: skip-file

from spatial_access.ScoreModel import ModelData
from spatial_access.SpatialAccessExceptions import SourceDataNotFoundException
from spatial_access.SpatialAccessExceptions import DestDataNotFoundException
from spatial_access.SpatialAccessExceptions import SourceDataNotParsableException
from spatial_access.SpatialAccessExceptions import DestDataNotParsableException


class TestClass():
    """
    Suite of tests for ScoreModel
    """

    def test_1(self):
        """
        Test instantiating ModelData
        instance and calling load_sp_matrix with
        complete source_column_names and dest_column_names,
        and no precomputed sp_matrix.
        """
        model_data = ModelData('drive',sources_filename="tests/test_data/sources.csv",
                               destinations_filename="tests/test_data/dests.csv",
                               source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                    'population': 'pop'},
                               dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                  'target': 'targ', 'category': 'cat'})
        model_data.load_sp_matrix()

        model_data._sp_matrix.write_tmx('tests/test_data/score_model_test_1')

        assert True

    def test_2(self):
        """
        Test instantiating ModelData
        instance and calling load_sp_matrix with
        complete source_column_names and dest_column_names,
        but with a precomputed sp matrix.
        """
        model_data = ModelData('drive', sources_filename="tests/test_data/sources.csv",
                               destinations_filename="tests/test_data/dests.csv",
                               source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                    'population': 'pop'},
                               dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                  'target': 'targ', 'category': 'cat'})
        model_data.load_sp_matrix("tests/test_data/score_model_test_1")

        assert True

    def test_3(self):
        """
        Tests that SourceDataNotFoundException is thrown
        when source data does not exist
        """
        try:
            model_data = ModelData('drive', sources_filename="tests/test_data/nonexistant.csv",
                                   destinations_filename="tests/test_data/dests.csv",
                                   source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                        'population': 'pop'},
                                   dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                      'target': 'targ', 'category': 'cat'})
            model_data.load_sp_matrix()
        except SourceDataNotFoundException:
            assert True
            return
        assert False

    def test_4(self):
        """
        Tests that DestDataNotFoundException is thrown
        when dest data does not exist
        """
        try:
            model_data = ModelData('drive', sources_filename="tests/test_data/sources.csv",
                                   destinations_filename="tests/test_data/nonexistant.csv",
                                   source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                        'population': 'pop'},
                                   dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                      'target': 'targ', 'category': 'cat'})
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
                                   source_column_names={'idx': 'wrong_value', 'lat': 'y', 'lon': 'x',
                                                        'population': 'pop'},
                                   dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                      'target': 'targ', 'category': 'cat'})
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
                                   source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                        'population': 'pop'},
                                   dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                      'wrong_key': 'targ', 'category': 'cat'})
            model_data.load_sp_matrix('tests/test_data/score_model_test_1')
        except DestDataNotParsableException:
            assert True
            return
        assert False



    def test_7(self):
        """
        Test instantiating and processing ModelData
        instance.
        """
        model_data = ModelData('drive',sources_filename="tests/test_data/sources.csv",
                               destinations_filename="tests/test_data/dests.csv",
                               source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                    'population': 'pop'},
                               dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                  'target': 'targ', 'category': 'cat'})
        model_data.load_sp_matrix("tests/test_data/score_model_test_1")

        model_data.calculate_dests_in_range(600)
        model_data.calculate_sources_in_range(600)

        assert model_data.dests_in_range == {3: [],
                                                   4: [1, 2],
                                                   5: [1, 2],
                                                   6: [2]}

        assert model_data.sources_in_range == {0: [],
                                                     1: [4, 5],
                                                     2: [4, 5, 6]

        }

        assert model_data.get_values_by_source(3, True) == [(2, 601), (1, 714), (0, 768)]
        assert model_data.get_values_by_dest(1, True) == [(4, 7), (5, 21), (6, 682), (3, 714)]

    def test_8(self):
        """
        Test instantiating  ModelData
        instance, destination data has string indeces.
        Including reading a transit matrix from
        file with string indeces.
        """
        model_data = ModelData('drive',sources_filename="tests/test_data/sources.csv",
                               destinations_filename="tests/test_data/dests_a.csv",
                               source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                    'population': 'pop'},
                               dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                  'target': 'targ', 'category': 'cat'})
        model_data.load_sp_matrix()
        model_data._sp_matrix.write_tmx('tests/test_data/score_model_test_8')

        model_data.calculate_dests_in_range(600)
        model_data.calculate_sources_in_range(600)

        remapped_dests = model_data._sp_matrix.matrix_interface.get_dest_id_remap()
        assert model_data.get_sources_in_range_of_dest(remapped_dests['place_b']) == [4, 5]
        assert model_data.get_sources_in_range_of_dest(remapped_dests['place_c']) == [4, 5, 6]

        model_data2 = ModelData('drive', sources_filename="tests/test_data/sources.csv",
                                destinations_filename="tests/test_data/dests_a.csv",
                                source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                     'population': 'pop'},
                                dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                   'target': 'targ', 'category': 'cat'})

        model_data2.load_sp_matrix('tests/test_data/score_model_test_8')

        model_data2.calculate_dests_in_range(600)
        model_data2.calculate_sources_in_range(600)

        remapped_dests2 = model_data2._sp_matrix.matrix_interface.get_dest_id_remap()
        assert model_data2.get_sources_in_range_of_dest(remapped_dests2['place_b']) == [4, 5]
        assert model_data2.get_sources_in_range_of_dest(remapped_dests2['place_c']) == [4, 5, 6]

    def test_9(self):
        """
        Test get_population_in_range method
        """
        model_data = ModelData('drive', sources_filename="tests/test_data/sources.csv",
                               destinations_filename="tests/test_data/dests_a.csv",
                               source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                    'population': 'pop'},
                               dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                  'target': 'targ', 'category': 'cat'})
        model_data.load_sp_matrix()
        model_data.calculate_sources_in_range(600)

        remapped_dests = model_data._sp_matrix.matrix_interface.get_dest_id_remap()
        model_data._sp_matrix.matrix_interface.print_data_frame()
        assert model_data.get_population_in_range(remapped_dests['place_c'], 600) == 121
