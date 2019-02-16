# pylint: skip-file

from spatial_access.ScoreModel import ModelData
from spatial_access.SpatialAccessExceptions import SourceDataNotFoundException
from spatial_access.SpatialAccessExceptions import DestDataNotFoundException
from spatial_access.SpatialAccessExceptions import SourceDataNotParsableException
from spatial_access.SpatialAccessExceptions import DestDataNotParsableException


class TestClass:
    """
    Suite of tests for ScoreModel
    """
    def setup_class(self):
        import os
        self.datapath = 'tests/test_score_model_temp/'
        if not os.path.exists(self.datapath):
            os.mkdir(self.datapath)

    def teardown_class(self):
        import os
        if os.path.exists(self.datapath):
            import shutil
            shutil.rmtree(self.datapath)

    def test_01(self):
        """
        Test instantiating ModelData
        instance and calling load_sp_matrix with
        complete source_column_names and dest_column_names,
        and no precomputed sp_matrix.
        """
        model_data = ModelData('drive', sources_filename="tests/test_data/sources.csv",
                               destinations_filename="tests/test_data/dests.csv",
                               source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                    'population': 'pop'},
                               dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                  'capacity': 'capacity', 'category': 'cat'})
        model_data.load_sp_matrix()

        model_data.write_shortest_path_matrix_to_h5(self.datapath + 'score_model_test_1.h5')

        assert True

    def test_02(self):
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
                                                  'capacity': 'capacity', 'category': 'cat'})
        model_data.load_sp_matrix(self.datapath + "score_model_test_1.h5")

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
                                                      'capacity': 'capacity', 'category': 'cat'})
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
                                                      'capacity': 'capacity', 'category': 'cat'})
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
                                                      'capacity': 'capacity', 'category': 'cat'})
            model_data.load_sp_matrix(self.datapath + 'score_model_test_1.h5')
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
                                                      'wrong_key': 'capacity', 'category': 'cat'})
            model_data.load_sp_matrix(self.datapath + 'score_model_test_1.h5')
        except DestDataNotParsableException:
            assert True
            return
        assert False

    def test_7(self):
        """
        Test instantiating and processing ModelData
        instance.
        """
        model_data = ModelData('drive', sources_filename="tests/test_data/sources.csv",
                               destinations_filename="tests/test_data/dests.csv",
                               source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                    'population': 'pop'},
                               dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                  'capacity': 'capacity', 'category': 'cat'})
        model_data.load_sp_matrix()

        model_data.calculate_dests_in_range(100)
        model_data.calculate_sources_in_range(100)

        assert model_data.dests_in_range == {3: [0, 1, 2],
                                             4: [0, 1, 2],
                                             5: [2],
                                             6: [2]}

        assert model_data.sources_in_range == {0: [3, 4],
                                               1: [3, 4],
                                               2: [3, 4, 5, 6]

                                               }

        assert model_data.get_values_by_source(3, True) == [(2, 42), (1, 79), (0, 89)]
        assert model_data.get_values_by_dest(1, True) == [(4, 7), (3, 79), (6, 106), (5, 136)]

    def test_8(self):
        """
        Test instantiating  ModelData
        instance, destination data has string indeces.
        Including reading a transit matrix from
        file with string indeces.
        """
        model_data = ModelData('drive', sources_filename="tests/test_data/sources.csv",
                               destinations_filename="tests/test_data/dests_a.csv",
                               source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                    'population': 'pop'},
                               dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                  'capacity': 'capacity', 'category': 'cat'})

        model_data.load_sp_matrix()
        model_data.write_shortest_path_matrix_to_h5(self.datapath + 'score_model_test_8.h5')

        model_data.calculate_dests_in_range(125)
        model_data.calculate_sources_in_range(125)


        assert model_data.get_sources_in_range_of_dest('place_b') == [3, 4, 6]
        assert model_data.get_sources_in_range_of_dest('place_c') == [3, 4, 5, 6]

        model_data2 = ModelData('drive', sources_filename="tests/test_data/sources.csv",
                                destinations_filename="tests/test_data/dests_a.csv",
                                source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                     'population': 'pop'},
                                dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                   'capacity': 'capacity', 'category': 'cat'})


        model_data2.load_sp_matrix(self.datapath + 'score_model_test_8.h5')

        model_data2.calculate_dests_in_range(125)
        model_data2.calculate_sources_in_range(125)

        assert model_data2.get_sources_in_range_of_dest('place_b') == [3, 4, 6]
        assert model_data2.get_sources_in_range_of_dest('place_c') == [3, 4, 5, 6]

    def test_9(self):
        """
        Test get_population_in_range method
        """
        model_data = ModelData('drive', sources_filename="tests/test_data/sources.csv",
                               destinations_filename="tests/test_data/dests_a.csv",
                               source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                    'population': 'pop'},
                               dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                  'capacity': 'capacity', 'category': 'cat'})
        model_data.load_sp_matrix()
        model_data.calculate_sources_in_range(50)

        assert model_data.get_population_in_range('place_a') == 0
        assert model_data.get_population_in_range('place_b') == 31
        assert model_data.get_population_in_range('place_c') == 76

    def test_10(self):
        """
        Test _spatial_join_community_index
        """
        model_data = ModelData('drive', sources_filename="tests/test_data/sources.csv",
                               destinations_filename="tests/test_data/dests_a.csv",
                               source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                    'population': 'pop'},
                               dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                  'capacity': 'capacity', 'category': 'cat'})
        model_data.load_sp_matrix()

        spatial_joined_sources = model_data._spatial_join_community_index(model_data.sources)
        assert spatial_joined_sources is not None
