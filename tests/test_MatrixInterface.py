# pylint: skip-file
from spatial_access.MatrixInterface import MatrixInterface

from spatial_access.SpatialAccessExceptions import WriteH5FailedException
from spatial_access.SpatialAccessExceptions import IndecesNotFoundException
from spatial_access.SpatialAccessExceptions import FileNotFoundException
from spatial_access.SpatialAccessExceptions import UnexpectedShapeException
from spatial_access.SpatialAccessExceptions import InvalidIdTypeException


class TestClass:

    def setup_class(self):
        import os
        self.datapath = 'tests/test_matrix_interface_temp/'
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
        writing to and reading from .h5.
        """

        interface = MatrixInterface()
        interface.prepare_matrix(is_symmetric=False, rows=3, columns=2, network_vertices=4)
        interface.primary_ids_name = "row_ids"
        interface.secondary_ids_name = "col_ids"
        interface.dataset_name = "test_dataset"

        interface.add_edge_to_graph(0, 1, 3, False)
        interface.add_edge_to_graph(1, 0, 4, False)
        interface.add_edge_to_graph(0, 3, 5, False)
        interface.add_edge_to_graph(3, 2, 7, False)
        interface.add_edge_to_graph(0, 2, 2, True)

        interface.add_user_source_data(2, 10, 5, False)
        interface.add_user_source_data(1, 11, 4, False)
        interface.add_user_source_data(0, 12, 1, False)

        interface.add_user_dest_data(0, 21, 4)
        interface.add_user_dest_data(3, 20, 6)

        interface.build_matrix()

        interface.add_to_category_map(20, "a")
        interface.add_to_category_map(21, "b")

        assert interface.get_value_by_id(10, 21) == 11
        assert interface.get_value_by_id(12, 20) == 12
        assert interface.get_dests_in_range(100) == {10:[21, 20],
                                                       11:[21, 20],
                                                       12:[21, 20]}

        interface.write_h5(self.datapath + "test_01.hdf5")

        interface2 = MatrixInterface()
        interface2.read_h5(self.datapath + "test_01.hdf5")

        interface2.add_to_category_map(20, "a")
        interface2.add_to_category_map(21, "b")

        assert interface2.get_value_by_id(10, 21) == 11
        assert interface2.get_value_by_id(12, 20) == 12
        assert interface.get_dests_in_range(100) == {10: [21, 20],
                                                       11: [21, 20],
                                                       12: [21, 20]}
        assert interface.transit_matrix.getDataset() == interface2.transit_matrix.getDataset()
        assert interface.transit_matrix.getPrimaryDatasetIds() == interface2.transit_matrix.getPrimaryDatasetIds()
        assert interface.transit_matrix.getSecondaryDatasetIds() == interface2.transit_matrix.getSecondaryDatasetIds()

        assert interface.time_to_nearest_dest(10, "a") == interface2.time_to_nearest_dest(10, "a")

        assert True

    def test_2(self):
        """
        Tests symmetric int x int matrix
        writing to and reading from .h5.
        """

        interface = MatrixInterface()
        interface.prepare_matrix(is_symmetric=True, rows=3, columns=3, network_vertices=5)
        interface.primary_ids_name = "row_ids"

        interface.dataset_name = "test_dataset"

        interface.add_edge_to_graph(0, 1, 2, True)
        interface.add_edge_to_graph(1, 2, 1, True)
        interface.add_edge_to_graph(2, 3, 3, True)
        interface.add_edge_to_graph(3, 4, 4, True)
        interface.add_edge_to_graph(2, 4, 1, True)
        interface.add_edge_to_graph(4, 0, 1, True)

        interface.add_user_source_data(1, 10, 1, True)
        interface.add_user_source_data(4, 11, 2, True)
        interface.add_user_source_data(3, 12, 3, True)

        interface.build_matrix()

        interface.write_h5(self.datapath + 'test_02.hdf5')
        interface.write_csv(self.datapath + 'test_02.csv')

        interface2 = MatrixInterface()
        interface2.read_h5(self.datapath + "test_02.hdf5")

        assert interface.transit_matrix.getDataset() == interface2.transit_matrix.getDataset()
        assert interface.transit_matrix.getPrimaryDatasetIds() == interface2.transit_matrix.getPrimaryDatasetIds()
        assert interface.transit_matrix.getSecondaryDatasetIds() == interface2.transit_matrix.getSecondaryDatasetIds()

        assert True

    def test_3(self):
        """
        Tests symmetric str x str matrix
        writing to and reading from .h5.
        """

        interface = MatrixInterface()
        interface.primary_ids_are_string = True
        interface.prepare_matrix(is_symmetric=True, rows=3, columns=3, network_vertices=5)
        interface.primary_ids_name = "row_ids"
        interface.dataset_name = "test_dataset"

        interface.add_edge_to_graph(0, 1, 2, True)
        interface.add_edge_to_graph(1, 2, 1, True)
        interface.add_edge_to_graph(2, 3, 3, True)
        interface.add_edge_to_graph(3, 4, 4, True)
        interface.add_edge_to_graph(2, 4, 1, True)
        interface.add_edge_to_graph(4, 0, 1, True)

        interface.add_user_source_data(1, "a", 1, True)
        interface.add_user_source_data(4, "b", 2, True)
        interface.add_user_source_data(3, "c", 3, True)

        interface.build_matrix()

        interface.write_h5(self.datapath + 'test_03.hdf5')
        interface.write_csv(self.datapath + 'test_03.csv')

        interface2 = MatrixInterface()
        interface2.read_h5(self.datapath + "test_03.hdf5")

        assert interface.transit_matrix.getDataset() == interface2.transit_matrix.getDataset()
        assert interface.transit_matrix.getPrimaryDatasetIds() == interface2.transit_matrix.getPrimaryDatasetIds()
        assert interface.transit_matrix.getSecondaryDatasetIds() == interface2.transit_matrix.getSecondaryDatasetIds()

        assert True

    def test_4(self):
        """
        Tests throws FileNotFoundException
        """
        interface = MatrixInterface()
        interface.prepare_matrix(is_symmetric=True, rows=3, columns=3, network_vertices=5)
        try:
            interface.read_h5("nonexistant_filename.hdf5")
        except FileNotFoundException:
            assert True
            return
        assert False


    def test_5(self):
        """
        Tests throws IndecesNotFoundException. 
        """
        interface = MatrixInterface()
        interface.primary_ids_are_string = True
        interface.prepare_matrix(is_symmetric=True, rows=3, columns=3, network_vertices=5)
        interface.primary_ids_name = "row_ids"
        interface.dataset_name = "test_dataset"

        interface.add_edge_to_graph(0, 1, 2, True)
        interface.add_edge_to_graph(1, 2, 1, True)
        interface.add_edge_to_graph(2, 3, 3, True)
        interface.add_edge_to_graph(3, 4, 4, True)
        interface.add_edge_to_graph(2, 4, 1, True)
        interface.add_edge_to_graph(4, 0, 1, True)

        interface.add_user_source_data(1, "a", 1, True)
        interface.add_user_source_data(4, "b", 2, True)
        interface.add_user_source_data(3, "c", 3, True)

        try:
            interface.get_value_by_id(43643, 2353209)
        except IndecesNotFoundException:
            assert True
            return
        assert False

    def test_6(self):
        """
        Tests throws WriteH5FailedException.
        """
        interface = MatrixInterface()
        interface.primary_ids_are_string = True
        interface.prepare_matrix(is_symmetric=False, rows=3, columns=2, network_vertices=4)
        interface.primary_ids_name = "rows"
        interface.secondary_ids_name = "col_ids"
        interface.dataset_name = "test_dataset"

        interface.add_edge_to_graph(0, 1, 3, False)
        interface.add_edge_to_graph(1, 0, 4, False)
        interface.add_edge_to_graph(0, 3, 5, False)
        interface.add_edge_to_graph(3, 2, 7, False)
        interface.add_edge_to_graph(0, 2, 2, True)

        interface.add_user_source_data(2, "a", 5, False)
        interface.add_user_source_data(1, "b", 4, False)
        interface.add_user_source_data(0, "c", 1, False)

        interface.add_user_dest_data(0, 21, 4)
        interface.add_user_dest_data(3, 20, 6)

        try:
            interface.write_h5(self.datapath + "test_5.hdf5")
        except WriteH5FailedException:
            assert True
            return
        assert False

    def test_7(self):
        """
        Tests throws UnexpectedShapeException.
        """
        interface = MatrixInterface()
        try:
            interface.prepare_matrix(is_symmetric=True, rows=3, columns=2,
                                     network_vertices=4)
        except UnexpectedShapeException:
            assert True
            return
        assert False

    def test_8(self):
        """
        Tests throws InvalidIdTypeException.
        """
        interface = MatrixInterface()
        interface.primary_ids_are_string = True
        interface.prepare_matrix(is_symmetric=False, rows=3, columns=2, network_vertices=4)

        interface.add_edge_to_graph(0, 1, 3, False)
        interface.add_edge_to_graph(1, 0, 4, False)
        interface.add_edge_to_graph(0, 3, 5, False)
        interface.add_edge_to_graph(3, 2, 7, False)
        interface.add_edge_to_graph(0, 2, 2, True)
        try:
            interface.add_user_source_data(2, 1, 5, False)
        except InvalidIdTypeException:
            assert True
            return False
        assert False