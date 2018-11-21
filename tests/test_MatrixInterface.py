# pylint: skip-file
from spatial_access.MatrixInterface import MatrixInterface
import os
import shutil

class TestClass():

    def test_1(self):
        '''
        Tests computing a graph with single thread,
        writing to and reading from csv.
        '''
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

        assert interface.get(11, 13) == 14
        assert interface.get(11, 14) == 8
        assert interface.get(12, 13) == 20
        assert interface.get(12, 14) == 14
        interface.write_to_csv("test_outfile_1.csv");

        interface2 = MatrixInterface()
        interface2.read_from_csv("test_outfile_1.csv")
        os.remove('test_outfile_1.csv')

        assert interface2.get(11, 13) == 14
        assert interface2.get(11, 14) == 8
        assert interface2.get(12, 13) == 20
        assert interface2.get(12, 14) == 14

        assert True


    def test_2(self):
        '''
        Tests that the interface can accept string user
        labels and converts them into int ids successfully.
        '''

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
    
        assert interface.get("agency_a", "agency_a") == 0
        assert interface.get("agency_a", "agency_d") == 8    
        assert interface.get("agency_a", "agency_b") == 8
        assert interface.get("agency_d" , "agency_c") == 20

        assert True

    def test_3(self):
        '''
        Tests that the symmetric interface can be written to file 
        and read successfully.
        '''

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
    
        assert interface.get(11, 11) == 0
        assert interface.get(11, 14) == 8    
        assert interface.get(11, 12) == 8
        assert interface.get(12, 11) == 8
        assert interface.get(14, 13) == 20
        assert interface.get(13, 14) == 20
        assert interface.get(14, 14) == 0

        interface.write_to_csv('test_outfile_2.csv')

        interface2 = MatrixInterface()
        interface2.read_from_csv('test_outfile_2.csv')
        #os.remove('test_outfile_2.csv')

        assert interface2.get(11, 11) == 0
        assert interface2.get(11, 14) == 8    
        assert interface2.get(11, 12) == 8
        assert interface2.get(12, 11) == 8
        assert interface2.get(14, 13) == 20
        assert interface2.get(13, 14) == 20
        assert interface2.get(14, 14) == 0

        assert True

    def test_4(self):
        '''
        Tests computing a graph with single thread,
        writing to and reading from tmx.
        '''
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

        assert interface.get(11, 13) == 14
        assert interface.get(11, 14) == 8
        assert interface.get(12, 13) == 20
        assert interface.get(12, 14) == 14

        interface.write_to_tmx("test_outfile_1.tmx");

        interface2 = MatrixInterface()
        interface2.read_from_tmx("test_outfile_1.tmx")
        os.remove('test_outfile_1.tmx')

        assert interface2.get(11, 13) == 14
        assert interface2.get(11, 14) == 8
        assert interface2.get(12, 13) == 20
        assert interface2.get(12, 14) == 14

        assert True
