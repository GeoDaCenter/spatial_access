# pylint: disable
from transitMatrixAdapter import pyTransitMatrix

class TestClass():

    @staticmethod

    def test_1(self):
        '''
        Test adding edges to graph, computing, retrieving
        values and writing to .csv.
        '''
        matrix = pyTransitMatrix(vertices=5)

        matrix.addEdgeToGraph(0, 1, 5, True)
        matrix.addEdgeToGraph(1, 2, 6, True)
        matrix.addEdgeToGraph(2, 3, 2, True)
        matrix.addEdgeToGraph(2, 4, 4, False)
        matrix.addEdgeToGraph(3, 4, 3, True)

        matrix.addToUserSourceDataContainer(1, b"A", 1, True)
        matrix.addToUserSourceDataContainer(0, b"B", 2, True)
        matrix.addToUserSourceDataContainer(4, b"C", 3, True)
        matrix.addToUserSourceDataContainer(1, b"D", 7, True)

        matrix.compute(1)

        assert matrix.get(b"A", b"A") == 0
        assert matrix.get(b"A", b"B") == 8
        assert matrix.get(b"D", b"C") == 20
        assert matrix.get(b"B", b"D") == 14
     
        matrix.writeCSV(b"test_1_outfile.csv")

    def test_2(self):
        '''
        Test reading from csv and retrieving values.
        '''

        matrix = pyTransitMatrix(infile=b"test_1_outfile.csv")

        assert matrix.get(b"A", b"A") == 0
        assert matrix.get(b"A", b"B") == 8
        assert matrix.get(b"D", b"C") == 20
        assert matrix.get(b"B", b"D") == 14


    def test_3(self):
        '''
        Test multithreaded computation.
        '''
        matrix = pyTransitMatrix(vertices=5)

        matrix.addEdgeToGraph(0, 1, 5, True);
        matrix.addEdgeToGraph(1, 2, 6, True);
        matrix.addEdgeToGraph(2, 3, 2, True);
        matrix.addEdgeToGraph(2, 4, 4, False);
        matrix.addEdgeToGraph(3, 4, 3, True);

        matrix.addToUserSourceDataContainer(1, b"A", 1, True);
        matrix.addToUserSourceDataContainer(0, b"B", 2, True);
        matrix.addToUserSourceDataContainer(4, b"C", 3, True);
        matrix.addToUserSourceDataContainer(1, b"D", 7, True);

        matrix.compute(3)


        assert matrix.get(b"A", b"A") == 0
        assert matrix.get(b"A", b"B") == 8
        assert matrix.get(b"D", b"C") == 20
        assert matrix.get(b"B", b"D") == 14
     