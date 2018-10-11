# pylint: skip-file
from transitMatrixAdapter import pyTransitMatrix
import os

class TestClass():

    def test_1(self):
        '''
        Test adding edges to graph, computing, retrieving
        values, writing to and reading from .csv.
        '''
        matrix = pyTransitMatrix(vertices=5)

        matrix.addEdgeToGraph(0, 1, 5, True)
        matrix.addEdgeToGraph(1, 2, 6, True)
        matrix.addEdgeToGraph(2, 3, 2, True)
        matrix.addEdgeToGraph(2, 4, 4, False)
        matrix.addEdgeToGraph(3, 4, 3, True)

        matrix.addToUserSourceDataContainer(1, 1, 1, True)
        matrix.addToUserSourceDataContainer(0, 2, 2, True)
        matrix.addToUserSourceDataContainer(4, 3, 3, True)
        matrix.addToUserSourceDataContainer(1, 4, 7, True)

        matrix.compute(1)

        assert matrix.get(1, 1) == 0
        assert matrix.get(1, 2) == 8
        assert matrix.get(4, 3) == 20
        assert matrix.get(2, 4) == 14
        os.mkdir('tmp/')
        matrix.writeCSV(b"tmp/test_1_outfile.csv")

        matrix2 = pyTransitMatrix(infile=b"tmp/test_1_outfile.csv")

        assert matrix2.get(1, 1) == 0
        assert matrix2.get(1, 2) == 8
        assert matrix2.get(4, 3) == 20
        assert matrix2.get(2, 4) == 14


    def test_2(self):
        '''
        Test multithreaded computation.
        '''
        matrix = pyTransitMatrix(vertices=5)

        matrix.addEdgeToGraph(0, 1, 5, True)
        matrix.addEdgeToGraph(1, 2, 6, True)
        matrix.addEdgeToGraph(2, 3, 2, True)
        matrix.addEdgeToGraph(2, 4, 4, False)
        matrix.addEdgeToGraph(3, 4, 3, True)

        matrix.addToUserSourceDataContainer(1, 1, 1, True)
        matrix.addToUserSourceDataContainer(0, 2, 2, True)
        matrix.addToUserSourceDataContainer(4, 3, 3, True)
        matrix.addToUserSourceDataContainer(1, 4, 7, True)

        matrix.compute(3)


        assert matrix.get(1, 1) == 0
        assert matrix.get(1, 2) == 8
        assert matrix.get(4, 3) == 20
        assert matrix.get(2, 4) == 14

    def test_3(self):
        '''
        Cleanup.
        '''
        try:
            import shutil
            shutil.rmtree('tmp/')
        except BaseException:
            pass

        assert True
     