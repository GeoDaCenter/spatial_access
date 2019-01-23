# pylint: skip-file
from transitMatrixAdapter import pyTransitMatrix
import os

class TestClass():

    def test_1(self):
        '''
        Test adding edges to graph, computing, retrieving
        values, writing to and reading from .csv.
        '''
        matrix = pyTransitMatrix(vertices=5, isSymmetric=False)

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
        if not os.path.exists('tmp/'):
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
        Test getSourcesInRange and getDestsInRange (including INF points)
        '''
        matrix = pyTransitMatrix(vertices=5, isSymmetric=False)

        matrix.addEdgeToGraph(0, 1, 5, True)
        matrix.addEdgeToGraph(1, 2, 6, False)
        matrix.addEdgeToGraph(2, 3, 2, True)
        matrix.addEdgeToGraph(2, 4, 4, True)
        matrix.addEdgeToGraph(3, 4, 3, True)

        matrix.addToUserSourceDataContainer(1, 1, 1, True)
        matrix.addToUserSourceDataContainer(0, 2, 2, True)
        matrix.addToUserSourceDataContainer(3, 3, 3, True)
        matrix.addToUserSourceDataContainer(1, 4, 7, True)

        matrix.compute(3)

        sources_in_range = matrix.getSourcesInRange(12, 3)
        dests_in_range = matrix.getDestsInRange(12, 3)

        assert sources_in_range == {4: [1], 3: [1], 1: [2, 4], 2: [1]}
        assert dests_in_range == {4: [1], 3: [], 1: [2, 3, 4], 2: [1]}


    def test_5(self):
        '''
        Test getValuesBySource and getValuesByDest (with sorting)
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

        assert matrix.getValuesByDest(1, True) == [(1, 0), (2, 8), (4, 8), (3, 14)]
        assert matrix.getValuesByDest(2, True) ==  [(2, 0), (1, 8), (4, 14), (3, 20)]
        assert matrix.getValuesByDest(3, True) ==  [(3, 0), (1, 14), (2, 20), (4, 20)]
        assert matrix.getValuesByDest(4, True) == [(4, 0), (1, 8), (2, 14), (3, 20)]
        assert matrix.getValuesBySource(1, True) == [(1, 0), (2, 8), (4, 8), (3, 14)]
        assert matrix.getValuesBySource(2, True) == [(2, 0), (1, 8), (4, 14), (3, 20)]
        assert matrix.getValuesBySource(3, True) == [(3, 0), (1, 14), (2, 20), (4, 20)]
        assert matrix.getValuesBySource(4, True) == [(4, 0), (1, 8), (2, 14), (3, 20)]

    def test_6(self):
        '''
        Cleanup.
        '''
        try:
            import shutil
            shutil.rmtree('tmp/')
        except BaseException:
            pass

        assert True
     