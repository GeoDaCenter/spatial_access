# pylint: skip-file

from spatial_access.BaseModel import ModelData
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
        self.datapath = 'test_score_model_temp/'
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
        Test instantiating ModelData
        instance and calling load_transit_matrix with
        complete source_column_names and dest_column_names.
        """
        model_data = ModelData('drive', sources_filename="tests/test_data/sources.csv",
                               destinations_filename="tests/test_data/dests.csv",
                               source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                    'population': 'pop'},
                               dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                  'capacity': 'capacity', 'category': 'cat'})
        model_data.load_transit_matrix()
        filename = self.datapath + 'score_model_test_1.tmx'
        filename2 = self.datapath + 'score_model_test_1.csv'
        model_data.write_transit_matrix_to_tmx(filename)
        model_data.write_transit_matrix_to_csv(filename2)

        model_data_2 = ModelData('drive', sources_filename="tests/test_data/sources.csv",
                               destinations_filename="tests/test_data/dests.csv",
                               source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                    'population': 'pop'},
                               dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                  'capacity': 'capacity', 'category': 'cat'})
        model_data_2.load_transit_matrix(filename)

        assert True

    def test_2(self):
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
            model_data.load_transit_matrix()
        except SourceDataNotFoundException:
            assert True
            return
        assert False

    def test_3(self):
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
            model_data.load_transit_matrix()
        except DestDataNotFoundException:
            assert True
            return
        assert False

    def test_4(self):
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
            model_data.load_transit_matrix(read_from_file=self.datapath + "score_model_test_1.tmx")
        except SourceDataNotParsableException:
            assert True
            return
        assert False

    def test_5(self):
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
            model_data.load_transit_matrix(read_from_file=self.datapath + "score_model_test_1.tmx")
        except DestDataNotParsableException:
            assert True
            return
        assert False

    def test_7(self):
        """
        Test sources/dests in range.
        """
        model_data = ModelData('drive', sources_filename="tests/test_data/sources_a.csv",
                               destinations_filename="tests/test_data/dests_b.csv",
                               source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                    'population': 'pop'},
                               dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',

                                                  'capacity': 'capacity', 'category': 'cat'})
        model_data.load_transit_matrix()
        model_data.transit_matrix = self.mock_transit_matrix_values(model_data.transit_matrix)
        model_data.calculate_dests_in_range(400)
        model_data.calculate_sources_in_range(400)

        assert model_data.dests_in_range == {3: ["place_a", "place_b", "place_c", "place_d", "place_e", "place_f"],
                                             4: ["place_a", "place_b", "place_c", "place_d", "place_e", "place_f"],
                                             5: ["place_a", "place_b", "place_c", "place_d", "place_e", "place_f"],
                                             6: ["place_a", "place_b", "place_c", "place_d", "place_e", "place_f"],
                                             7: [],
                                             8:[]}

        assert model_data.sources_in_range == {"place_a": [3, 4, 5 ,6],
                                               "place_b": [3, 4, 5 ,6],
                                               "place_c": [3, 4, 5, 6],
                                               "place_d": [3, 4, 5, 6],
                                               "place_e": [3, 4, 5, 6],
                                               "place_f": [3, 4, 5, 6]
                                               }

    def test_9(self):
        """
        Test get_population_in_range method
        """
        model_data = ModelData('drive', sources_filename="tests/test_data/sources_a.csv",
                               destinations_filename="tests/test_data/dests_b.csv",
                               source_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',
                                                    'population': 'pop'},
                               dest_column_names={'idx': 'name', 'lat': 'y', 'lon': 'x',

                                                  'capacity': 'capacity', 'category': 'cat'})
        model_data.load_transit_matrix()
        model_data.transit_matrix = self.mock_transit_matrix_values(model_data.transit_matrix)
        model_data.calculate_sources_in_range(400)

        assert model_data.get_population_in_range('place_a') == 166
        assert model_data.get_population_in_range('place_b') == 166
        assert model_data.get_population_in_range('place_c') == 166
        assert model_data.get_population_in_range('place_d') == 166
        assert model_data.get_population_in_range('place_e') == 166
        assert model_data.get_population_in_range('place_f') == 166

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
        model_data.load_transit_matrix()

        spatial_joined_sources = model_data._spatial_join_community_index(model_data.sources)
        assert spatial_joined_sources is not None
