# pylint: skip-file
from spatial_access.MatrixInterface import MatrixInterface

from spatial_access.SpatialAccessExceptions import ReadTMXFailedException
from spatial_access.SpatialAccessExceptions import ReadCSVFailedException
from spatial_access.SpatialAccessExceptions import WriteTMXFailedException
from spatial_access.SpatialAccessExceptions import WriteCSVFailedException
from spatial_access.SpatialAccessExceptions import IndecesNotFoundException

import os
import shutil


class TestClass():

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

    def test_1(self):
        """
        Tests computing a graph with single thread,
        writing to and reading from csv.
        """
        interface = MatrixInterface()
        interface.prepare_matrix(5, isSymmetric=False)

        interface.add_edge_to_graph(0, 1, 5, True)
        interface.add_edge_to_graph(1, 2, 6, True)
        interface.add_edge_to_graph(2, 3, 2, True)
        interface.add_edge_to_graph(2, 4, 4, False)
        interface.add_edge_to_graph(3, 4, 5, True)

        interface.add_user_source_data(1, 11, 1, False)
        interface.add_user_source_data(0, 12, 2, False)
        interface.add_user_dest_data(4, 13, 3)
        interface.add_user_dest_data(1, 14, 7)

        interface.build_matrix()

        assert interface.get_value(11, 13) == 14
        assert interface.get_value(11, 14) == 8
        assert interface.get_value(12, 13) == 20
        assert interface.get_value(12, 14) == 14
        interface.write_to_csv(self.datapath + "test_outfile_1.csv");

        interface2 = MatrixInterface()
        interface2.read_from_csv(self.datapath + "test_outfile_1.csv")

        assert interface2.get_value(11, 13) == 14
        assert interface2.get_value(11, 14) == 8
        assert interface2.get_value(12, 13) == 20
        assert interface2.get_value(12, 14) == 14

        assert True


    def test_2(self):
        """
        Tests that the interface can accept string user
        labels and converts them into int ids successfully.
        """

        interface = MatrixInterface()
        interface.prepare_matrix(5, isSymmetric=True)

        interface.add_edge_to_graph(0, 1, 5, True)
        interface.add_edge_to_graph(1, 2, 6, True)
        interface.add_edge_to_graph(2, 3, 2, True)
        interface.add_edge_to_graph(2, 4, 4, True)
        interface.add_edge_to_graph(3, 4, 3, True)

        interface.add_user_source_data(1, "agency_a", 1, True)
        interface.add_user_source_data(0, "agency_b", 2, True)
        interface.add_user_source_data(4, "agency_c", 3, True)
        interface.add_user_source_data(1, "agency_d", 7, True)

        interface.build_matrix()

        source_id_remap = interface.get_source_id_remap()

    
        assert interface.get_value(source_id_remap["agency_a"], source_id_remap["agency_a"]) == 0
        assert interface.get_value(source_id_remap["agency_a"], source_id_remap["agency_d"]) == 8
        assert interface.get_value(source_id_remap["agency_a"], source_id_remap["agency_b"]) == 8
        assert interface.get_value(source_id_remap["agency_d"] , source_id_remap["agency_c"]) == 20

        assert True

    def test_3(self):
        """
        Tests that the symmetric interface can be written to file 
        and read successfully.
        """

        interface = MatrixInterface()
        interface.prepare_matrix(5, isSymmetric=True)

        interface.add_edge_to_graph(0, 1, 5, True)
        interface.add_edge_to_graph(1, 2, 6, True)
        interface.add_edge_to_graph(2, 3, 2, True)
        interface.add_edge_to_graph(2, 4, 4, True)
        interface.add_edge_to_graph(3, 4, 3, True)

        interface.add_user_source_data(1, 11, 1, True)
        interface.add_user_source_data(0, 12, 2, True)
        interface.add_user_source_data(4, 13, 3, True)
        interface.add_user_source_data(1, 14, 7, True)

        interface.build_matrix()
    
        assert interface.get_value(11, 11) == 0
        assert interface.get_value(11, 14) == 8
        assert interface.get_value(11, 12) == 8
        assert interface.get_value(12, 11) == 8
        assert interface.get_value(14, 13) == 20
        assert interface.get_value(13, 14) == 20
        assert interface.get_value(14, 14) == 0

        interface.write_to_csv(self.datapath + 'test_outfile_2.csv')

        interface2 = MatrixInterface()
        interface2.read_from_csv(self.datapath + 'test_outfile_2.csv')

        assert interface2.get_value(11, 11) == 0
        assert interface2.get_value(11, 14) == 8
        assert interface2.get_value(11, 12) == 8
        assert interface2.get_value(12, 11) == 8
        assert interface2.get_value(14, 13) == 20
        assert interface2.get_value(13, 14) == 20
        assert interface2.get_value(14, 14) == 0

        assert True

    def test_4(self):
        """
        Tests computing a graph with single thread,
        writing to and reading from tmx.
        """
        interface = MatrixInterface()
        interface.prepare_matrix(5, isSymmetric=False)

        interface.add_edge_to_graph(0, 1, 5, True)
        interface.add_edge_to_graph(1, 2, 6, True)
        interface.add_edge_to_graph(2, 3, 2, True)
        interface.add_edge_to_graph(2, 4, 4, False)
        interface.add_edge_to_graph(3, 4, 5, True)

        interface.add_user_source_data(1, 11, 1, False)
        interface.add_user_source_data(0, 12, 2, False)
        interface.add_user_dest_data(4, 13, 3)
        interface.add_user_dest_data(1, 14, 7)

        interface.build_matrix()

        assert interface.get_value(11, 13) == 14
        assert interface.get_value(11, 14) == 8
        assert interface.get_value(12, 13) == 20
        assert interface.get_value(12, 14) == 14

        interface.write_to_tmx(self.datapath + "test_outfile_1");

        interface2 = MatrixInterface()
        interface2.read_from_tmx(self.datapath + "test_outfile_1")


        assert interface2.get_value(11, 13) == 14
        assert interface2.get_value(11, 14) == 8
        assert interface2.get_value(12, 13) == 20
        assert interface2.get_value(12, 14) == 14

    def test_5(self):
        """
        Tests throws IndecesNotFoundException. 
        """
        interface = MatrixInterface()
        interface.prepare_matrix(5, isSymmetric=False)

        interface.add_edge_to_graph(0, 1, 5, True)
        interface.add_edge_to_graph(1, 2, 6, True)
        interface.add_edge_to_graph(2, 3, 2, True)
        interface.add_edge_to_graph(2, 4, 4, False)
        interface.add_edge_to_graph(3, 4, 5, True)

        interface.add_user_source_data(1, 11, 1, False)
        interface.add_user_source_data(0, 12, 2, False)
        interface.add_user_dest_data(4, 13, 3)
        interface.add_user_dest_data(1, 14, 7)

        interface.build_matrix()

        try:
            interface.get_value(43643, 2353209)
        except IndecesNotFoundException:
            assert True
            return
        assert False

    def test_5(self):
        """
        Tests throws ReadTMXFailedException. 
        """
        interface = MatrixInterface()
        try:
            interface.read_from_tmx(self.datapath + "non_existant_file")
        except ReadTMXFailedException:
            assert True
            return
        assert False

    def test_6(self):
        """
        Tests throws ReadCSVFailedException. 
        """
        interface = MatrixInterface()
        try:
            interface.read_from_csv(self.datapath + "non_existant_file.csv")
        except ReadCSVFailedException:
            assert True
            return
        assert False


    def test_7(self):
        """
        Tests throws WriteTMXFailedException. 
        """
        interface = MatrixInterface()
        try:
            interface.write_to_tmx(self.datapath + "other_non_existant_file")
        except WriteTMXFailedException:
            assert True
            return
        assert False


    def test_8(self):
        """
        Tests throws WriteCSVFailedException. 
        """
        interface = MatrixInterface()
        try:
            interface.write_to_csv(self.datapath + "other_non_existant_file.csv")
        except WriteCSVFailedException:
            assert True
            return
        assert False
