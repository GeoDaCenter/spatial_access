# pylint: skip-file
from transitMatrixAdapter import pyTransitMatrix
import os

class TestClass():

    def test_1(self):
        '''
        Test adding edges to graph, computing, retrieving
        values, writing to and reading from .csv.
        '''
        matrix = pyTransitMatrix(vertices=4, isSymmetric=False)

        matrix.addEdgeToGraph(0, 1, 1, True)
        matrix.addEdgeToGraph(1, 2, 6, True)
        matrix.addEdgeToGraph(0, 3, 5, True)
        matrix.addEdgeToGraph(1, 3, 2, True)


        matrix.addToUserSourceDataContainer(1, 0, 4, False)
        matrix.addToUserSourceDataContainer(0, 1, 2, False)
        matrix.addToUserDestDataContainer(0, 2, 3)
        matrix.addToUserDestDataContainer(2, 3, 8)

        matrix.compute(1)

        assert matrix.get(0, 2) == 8
        assert matrix.get(1, 2) == 5
        assert matrix.get(0, 3) == 18
        assert matrix.get(1, 3) == 17
        os.mkdir('tmp/')
        matrix.writeCSV(b"tmp/test_1_outfile.csv")

        matrix2 = pyTransitMatrix(infile=b"tmp/test_1_outfile.csv")

        assert matrix.get(0, 2) == 8
        assert matrix.get(1, 2) == 5
        assert matrix.get(0, 3) == 18
        assert matrix.get(1, 3) == 17


    def test_2(self):
        '''
        Test multithreaded computation.
        '''
        matrix = pyTransitMatrix(vertices=4, isSymmetric=False)

        matrix.addEdgeToGraph(0, 1, 1, True)
        matrix.addEdgeToGraph(1, 2, 6, True)
        matrix.addEdgeToGraph(0, 3, 5, True)
        matrix.addEdgeToGraph(1, 3, 2, True)


        matrix.addToUserSourceDataContainer(1, 0, 4, False)
        matrix.addToUserSourceDataContainer(0, 1, 2, False)
        matrix.addToUserDestDataContainer(0, 2, 3)
        matrix.addToUserDestDataContainer(2, 3, 8)

        matrix.compute(3)

        assert matrix.get(0, 2) == 8
        assert matrix.get(1, 2) == 5
        assert matrix.get(0, 3) == 18
        assert matrix.get(1, 3) == 17


    def test_3(self):
        '''
        Test symmetric matrix optimization
        '''
        matrix = pyTransitMatrix(vertices=5, isSymmetric=True)

        matrix.addEdgeToGraph(0, 1, 5, True)
        matrix.addEdgeToGraph(1, 2, 6, True)
        matrix.addEdgeToGraph(2, 3, 2, True)
        matrix.addEdgeToGraph(2, 4, 4, True)
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
        assert matrix.get(4, 2) == 14
        assert matrix.get(4, 4) == 0



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
     