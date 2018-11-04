# pylint: skip-file
from spatial_access.MatrixInterface import MatrixInterface
import os

class TestClass():

    def test_1(self):
        '''
        Tests that single-thread loading a graph with
        edges and calling compute does not crash and
        produces the expected result.
        '''
        interface = MatrixInterface()
        interface.prepare_matrix(5, isSymmetric=True)

        interface.add_edge_to_graph(0, 1, 5, True)
        interface.add_edge_to_graph(1, 2, 6, True)
        interface.add_edge_to_graph(2, 3, 2, True)
        interface.add_edge_to_graph(2, 4, 4, False)
        interface.add_edge_to_graph(3, 4, 3, True)

        interface.add_user_source_data(1, 11, 1, True)
        interface.add_user_source_data(0, 12, 2, True)
        interface.add_user_source_data(4, 13, 3, True)
        interface.add_user_source_data(1, 14, 7, True)

        interface.build_matrix()

        assert interface.get(11, 11) == 0
        assert interface.get(11, 12) == 8
        assert interface.get(14 , 13) == 20

        os.mkdir('tmp/')
        interface.write_to_csv("tmp/test_outfile_1.csv");

        assert True

    def test_2(self):
        '''
        Tests that a matrix can be read from file.
        '''
        interface = MatrixInterface()
        interface.read_from_csv("tmp/test_outfile_1.csv")

        assert interface.get(11, 11) == 0
        assert interface.get(11, 12) == 8
        assert interface.get(14 , 13) == 20

    def test_3(self):
        '''
        Tests that the interface can accept string user
        labels and converts them into int ids successfully.
        '''

        interface = MatrixInterface()
        interface.prepare_matrix(5, isSymmetric=True)

        interface.add_edge_to_graph(0, 1, 5, True)
        interface.add_edge_to_graph(1, 2, 6, True)
        interface.add_edge_to_graph(2, 3, 2, True)
        interface.add_edge_to_graph(2, 4, 4, False)
        interface.add_edge_to_graph(3, 4, 3, True)

        interface.add_user_source_data(1, "agency_a", 1, True)
        interface.add_user_source_data(0, "agency_b", 2, True)
        interface.add_user_source_data(4, "agency_c", 3, True)
        interface.add_user_source_data(1, "agency_d", 7, True)

        interface.build_matrix()

        val_1 =  interface.get("agency_a", "agency_a")
        
        assert interface.get("agency_a", "agency_b") == 8
        assert interface.get("agency_d" , "agency_c") == 20

        assert True


    def test_4(self):
        '''
        Cleanup.
        '''
        try:
            import shutil
            shutil.rmtree('tmp/')
        except BaseException:
            pass

        assert True