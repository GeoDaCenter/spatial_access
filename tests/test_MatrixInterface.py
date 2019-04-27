from spatial_access.MatrixInterface import MatrixInterface

from spatial_access.SpatialAccessExceptions import ReadTMXFailedException
from spatial_access.SpatialAccessExceptions import IndecesNotFoundException
from spatial_access.SpatialAccessExceptions import FileNotFoundException
from spatial_access.SpatialAccessExceptions import UnexpectedShapeException

class TestClass:
    def setup_class(self):
        import os
        self.datapath = 'test_matrix_interface_temp/'
        if not os.path.exists(self.datapath):
            os.mkdir(self.datapath)

    def teardown_class(self):
        import os
        if os.path.exists(self.datapath):
            import shutil
            shutil.rmtree(self.datapath)

    def test_01(self):
        """
        Tests asymmetric int x int matrix
        writing to and reading from tmx.
        """

        interface = MatrixInterface()
        interface.prepare_matrix(is_symmetric=False,
                                 is_compressible=False,
                                 rows=3,
                                 columns=2,
                                 network_vertices=4)
        from_column = [0, 1, 0, 3, 0]
        to_column = [1, 0, 3, 2, 2]
        weight_column = [3, 4, 5, 7, 2]
        is_bidirectional_column =[False, False, False, False, True]
        interface.add_edges_to_graph(from_column=from_column,
                                     to_column=to_column,
                                     edge_weight_column=weight_column,
                                     is_bidirectional_column=is_bidirectional_column)

        interface.add_user_source_data(2, 10, 5, False)
        interface.add_user_source_data(1, 11, 4, False)
        interface.add_user_source_data(0, 12, 1, False)

        interface.add_user_dest_data(0, 21, 4)
        interface.add_user_dest_data(3, 20, 6)

        interface.build_matrix()

        interface.add_to_category_map(20, "a")
        interface.add_to_category_map(21, "b")

        assert interface.get_dests_in_range(100) == {10:[21, 20],
                                                       11:[21, 20],
                                                       12:[21, 20]}

        filename = self.datapath + "test_1.tmx"
        interface.write_tmx(filename)

        interface2 = MatrixInterface()
        interface2.read_file(filename)

        interface2.add_to_category_map(20, "a")
        interface2.add_to_category_map(21, "b")

        assert interface.get_dests_in_range(100) == {10: [21, 20],
                                                       11: [21, 20],
                                                       12: [21, 20]}
        interface2.write_csv(self.datapath + "test_1.csv")

    def test_2(self):
        """
        Tests asymmetric string x string matrix
        writing to and reading from .tmx.
        """

        interface = MatrixInterface()
        interface.primary_ids_are_string = True
        interface.secondary_ids_are_string = True
        interface.prepare_matrix(is_symmetric=False,
                                 is_compressible=False,
                                 rows=3,
                                 columns=2,
                                 network_vertices=4)
        from_column = [0, 1, 0, 3, 0]
        to_column = [1, 0, 3, 2, 2]
        weight_column = [3, 4, 5, 7, 2]
        is_bidirectional_column = [False, False, False, False, True]
        interface.add_edges_to_graph(from_column=from_column,
                                     to_column=to_column,
                                     edge_weight_column=weight_column,
                                     is_bidirectional_column=is_bidirectional_column)

        interface.add_user_source_data(2, "a", 5, False)
        interface.add_user_source_data(1, "b", 4, False)
        interface.add_user_source_data(0, "c", 1, False)

        interface.add_user_dest_data(0, "d", 4)
        interface.add_user_dest_data(3, "e", 6)

        interface.build_matrix()

        interface.add_to_category_map("d", "cat_a")
        interface.add_to_category_map("e", "cat_b")

        assert interface.get_dests_in_range(100) == {"a": ["d", "e"],
                                                      "b": ["d", "e"],
                                                      "c": ["d", "e"]}

        filename = self.datapath + "test_1.tmx"
        interface.write_tmx(filename)

        interface2 = MatrixInterface()
        interface2.read_file(filename)

        interface2.add_to_category_map("d", "cat_a")
        interface2.add_to_category_map("e", "cat_b")

        assert interface2.get_dests_in_range(100) == {"a": ["d", "e"],
                                                     "b": ["d", "e"],
                                                     "c": ["d", "e"]}
        interface2.write_csv(self.datapath + "test_2.csv")

    def test_3(self):
        """
        Tests throws ReadTMXFailedException
        """
        interface = MatrixInterface()
        try:
            interface.read_file(self.datapath + "nonexistant_filename.tmx")
        except FileNotFoundError:
            return
        assert False


    def test_4(self):
        """
        Tests throws IndecesNotFoundException. 
        """
        interface = MatrixInterface()
        interface.primary_ids_are_string = True
        interface.prepare_matrix(is_symmetric=True,
                                 is_compressible=True,
                                 rows=3,
                                 columns=3, network_vertices=5)

        from_column = [0, 1, 0, 3, 0]
        to_column = [1, 0, 3, 2, 2]
        weight_column = [3, 4, 5, 7, 2]
        is_bidirectional_column = [False, False, False, False, True]
        interface.add_edges_to_graph(from_column=from_column,
                                     to_column=to_column,
                                     edge_weight_column=weight_column,
                                     is_bidirectional_column=is_bidirectional_column)

        interface.add_user_source_data(1, "a", 1, True)
        interface.add_user_source_data(4, "b", 2, True)
        interface.add_user_source_data(3, "c", 3, True)

        try:
            interface._get_value_by_id(43643, 2353209)
        except IndecesNotFoundException:
            return
        assert False

    def test_5(self):
        """
        Tests throws UnexpectedShapeException.
        """
        interface = MatrixInterface()
        try:
            interface.prepare_matrix(is_symmetric=True, is_compressible=True,
                                     rows=3, columns=2,
                                     network_vertices=4)
        except UnexpectedShapeException:
            return
        assert False

    def test_6(self):
        """
        Test read otp csv
        """
        interface = MatrixInterface()
        interface.read_otp("tests/test_data/sample_otp.csv")

    def test_7(self):
        """
        Test write/read csv
        """
        interface = MatrixInterface()
        interface.prepare_matrix(is_symmetric=False,
                                 is_compressible=False,
                                 rows=3,
                                 columns=2,
                                 network_vertices=4)
        from_column = [0, 1, 0, 3, 0]
        to_column = [1, 0, 3, 2, 2]
        weight_column = [3, 4, 5, 7, 2]
        is_bidirectional_column = [False, False, False, False, True]
        interface.add_edges_to_graph(from_column=from_column,
                                     to_column=to_column,
                                     edge_weight_column=weight_column,
                                     is_bidirectional_column=is_bidirectional_column)

        interface.add_user_source_data(2, 10, 5, False)
        interface.add_user_source_data(1, 11, 4, False)
        interface.add_user_source_data(0, 12, 1, False)

        interface.add_user_dest_data(0, 21, 4)
        interface.add_user_dest_data(3, 20, 6)

        interface.build_matrix()
        filename = self.datapath + "test_7.csv"
        interface.write_csv(filename)
        interface.print_data_frame()
        interface2 = MatrixInterface()
        interface2.read_file(filename)
        interface2.print_data_frame()

