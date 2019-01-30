# pylint: skip-file
from transitMatrixAdapter import pyTransitMatrix

class TestClass():

    def setup(self):
        import os
        self.datapath = 'tests/test_pytransitmatrix_temp/'
        if not os.path.exists(self.datapath):
            os.mkdir(self.datapath)

    def teardown(self):
        import os
        if os.path.exists(self.datapath):
            import shutil
            shutil.rmtree(self.datapath)


    def test_1(self):
        """
        Test adding edges to graph, computing, retrieving
        values, writing to and reading from .csv.
        """
        matrix = pyTransitMatrix(vertices=5, isSymmetric=False)

        matrix.addEdgeToGraph(0, 1, 1, True)
        matrix.addEdgeToGraph(1, 2, 6, True)
        matrix.addEdgeToGraph(0, 3, 5, True)
        matrix.addEdgeToGraph(1, 3, 2, True)

        matrix.addToUserSourceDataContainerInt(1, 0, 4, False)
        matrix.addToUserSourceDataContainerInt(0, 1, 2, False)
        matrix.addToUserDestDataContainerInt(0, 2, 3)
        matrix.addToUserDestDataContainerInt(2, 3, 8)

        matrix.compute(1)

        assert matrix.get(0, 2) == 8
        assert matrix.get(1, 2) == 5
        assert matrix.get(0, 3) == 18
        assert matrix.get(1, 3) == 17
        filename = self.datapath + 'test_1_outfile.csv'
        matrix.writeCSV(bytes(filename, 'utf-8'))

        matrix2 = pyTransitMatrix(infile=bytes(filename, 'utf-8'))

        assert matrix2.get(0, 2) == 8
        assert matrix2.get(1, 2) == 5
        assert matrix2.get(0, 3) == 18
        assert matrix2.get(1, 3) == 17

    def test_2(self):
        """
        Test multithreaded computation.
        """
        matrix = pyTransitMatrix(vertices=4, isSymmetric=False)

        matrix.addEdgeToGraph(0, 1, 1, True)
        matrix.addEdgeToGraph(1, 2, 6, True)
        matrix.addEdgeToGraph(0, 3, 5, True)
        matrix.addEdgeToGraph(1, 3, 2, True)

        matrix.addToUserSourceDataContainerInt(1, 0, 4, False)
        matrix.addToUserSourceDataContainerInt(0, 1, 2, False)
        matrix.addToUserDestDataContainerInt(0, 2, 3)
        matrix.addToUserDestDataContainerInt(2, 3, 8)

        matrix.compute(3)

        assert matrix.get(0, 2) == 8
        assert matrix.get(1, 2) == 5
        assert matrix.get(0, 3) == 18
        assert matrix.get(1, 3) == 17

    def test_3(self):
        """
        Test symmetric matrix optimization
        """
                
        matrix = pyTransitMatrix(vertices=5, isSymmetric=True)

        matrix.addEdgeToGraph(0, 1, 5, True)
        matrix.addEdgeToGraph(1, 2, 6, True)
        matrix.addEdgeToGraph(2, 3, 2, True)
        matrix.addEdgeToGraph(2, 4, 4, True)
        matrix.addEdgeToGraph(3, 4, 3, True)

        matrix.addToUserSourceDataContainerInt(1, 1, 1, True)
        matrix.addToUserSourceDataContainerInt(0, 2, 2, True)
        matrix.addToUserSourceDataContainerInt(4, 3, 3, True)
        matrix.addToUserSourceDataContainerInt(1, 4, 7, True)

        matrix.compute(3)

        assert matrix.get(1, 1) == 0
        assert matrix.get(1, 2) == 8
        assert matrix.get(4, 3) == 20
        assert matrix.get(2, 4) == 14
        assert matrix.get(4, 2) == 14
        assert matrix.get(4, 4) == 0

    def test_4(self):
        """
        Test getSourcesInRange and getDestsInRange (including INF points)
        """
        matrix = pyTransitMatrix(vertices=5, isSymmetric=False)

        matrix.addEdgeToGraph(0, 1, 5, True)
        matrix.addEdgeToGraph(1, 2, 6, False)
        matrix.addEdgeToGraph(2, 3, 2, True)
        matrix.addEdgeToGraph(2, 4, 4, True)
        matrix.addEdgeToGraph(3, 4, 3, True)

        matrix.addToUserSourceDataContainerInt(1, 1, 1, True)
        matrix.addToUserSourceDataContainerInt(0, 2, 2, True)
        matrix.addToUserSourceDataContainerInt(3, 3, 3, True)
        matrix.addToUserSourceDataContainerInt(1, 4, 7, True)

        matrix.compute(3)

        sources_in_range = matrix.getSourcesInRange(12, 3)
        dests_in_range = matrix.getDestsInRange(12, 3)

        assert sources_in_range == {4: [1], 3: [1, 3], 1: [1, 2, 4], 2: [1, 2]}
        assert dests_in_range == {4: [1], 3: [3], 1: [1, 2, 3, 4], 2: [1, 2]}

    def test_5(self):
        """
        Test getValuesBySource and getValuesByDest (with sorting)
        """
                
        matrix = pyTransitMatrix(vertices=5, isSymmetric=True)

        matrix.addEdgeToGraph(0, 1, 5, True)
        matrix.addEdgeToGraph(1, 2, 6, True)
        matrix.addEdgeToGraph(2, 3, 2, True)
        matrix.addEdgeToGraph(2, 4, 4, True)
        matrix.addEdgeToGraph(3, 4, 3, True)

        matrix.addToUserSourceDataContainerInt(1, 1, 1, True)
        matrix.addToUserSourceDataContainerInt(0, 2, 2, True)
        matrix.addToUserSourceDataContainerInt(4, 3, 3, True)
        matrix.addToUserSourceDataContainerInt(1, 4, 7, True)

        matrix.compute(3)

        assert matrix.getValuesByDest(1, True) == [(1, 0), (2, 8), (4, 8), (3, 14)]
        assert matrix.getValuesByDest(2, True) == [(2, 0), (1, 8), (4, 14), (3, 20)]
        assert matrix.getValuesByDest(3, True) == [(3, 0), (1, 14), (2, 20), (4, 20)]
        assert matrix.getValuesByDest(4, True) == [(4, 0), (1, 8), (2, 14), (3, 20)]
        assert matrix.getValuesBySource(1, True) == [(1, 0), (2, 8), (4, 8), (3, 14)]
        assert matrix.getValuesBySource(2, True) == [(2, 0), (1, 8), (4, 14), (3, 20)]
        assert matrix.getValuesBySource(3, True) == [(3, 0), (1, 14), (2, 20), (4, 20)]
        assert matrix.getValuesBySource(4, True) == [(4, 0), (1, 8), (2, 14), (3, 20)]

    def test_6(self):
        """
        Test giving strings as source and dest data ids.
        """
        matrix = pyTransitMatrix(vertices=5, isSymmetric=False)

        matrix.addEdgeToGraph(0, 1, 1, True)
        matrix.addEdgeToGraph(1, 2, 6, True)
        matrix.addEdgeToGraph(0, 3, 5, True)
        matrix.addEdgeToGraph(1, 3, 2, True)

        matrix.addToUserSourceDataContainerString(1, b"a", 4, False)
        matrix.addToUserSourceDataContainerString(0, b"b", 2, False)
        matrix.addToUserDestDataContainerString(0, b"c", 3)
        matrix.addToUserDestDataContainerString(2, b"d", 8)

        matrix.compute(1)

        row_id_cache = matrix.getUserRowIdCache()
        assert row_id_cache == {b"a":0, b"b":1}
        col_id_cache = matrix.getUserColIdCache()
        assert col_id_cache == {b"c":0, b"d":1}

        assert matrix.get(row_id_cache[b"a"], col_id_cache[b"c"]) == 8
        assert matrix.get(row_id_cache[b"b"], col_id_cache[b"c"]) == 5
        assert matrix.get(row_id_cache[b"a"], col_id_cache[b"d"]) == 18
        assert matrix.get(row_id_cache[b"b"], col_id_cache[b"d"]) == 17

    def test_7(self):
        """
        Test time_to_nearest_dest--both with and
        without category
        """

        matrix = pyTransitMatrix(vertices=5, isSymmetric=True)

        matrix.addEdgeToGraph(0, 1, 5, True)
        matrix.addEdgeToGraph(1, 2, 6, True)
        matrix.addEdgeToGraph(2, 3, 2, True)
        matrix.addEdgeToGraph(2, 4, 4, True)
        matrix.addEdgeToGraph(3, 4, 3, True)

        matrix.addToUserSourceDataContainerInt(1, 1, 1, True)
        matrix.addToUserSourceDataContainerInt(0, 2, 2, True)
        matrix.addToUserSourceDataContainerInt(4, 3, 3, True)
        matrix.addToUserSourceDataContainerInt(1, 4, 7, True)

        matrix.compute(3)

        matrix.addToCategoryMap(1, b"a")
        matrix.addToCategoryMap(2, b"a")
        matrix.addToCategoryMap(3, b"c")
        matrix.addToCategoryMap(4, b"c")

        assert matrix.countDestsInRange(1, 15) == 4
        assert matrix.countDestsInRangePerCategory(1, b"c", 15) == 2
        assert matrix.countDestsInRange(2, 10) == 2
        assert matrix.countDestsInRangePerCategory(2, b"c", 10) == 0

    def test_8(self):
        """
        Test count_dests_in_range--both with and
        without category
        """
        matrix = pyTransitMatrix(vertices=5, isSymmetric=True)

        matrix.addEdgeToGraph(0, 1, 5, True)
        matrix.addEdgeToGraph(1, 2, 6, True)
        matrix.addEdgeToGraph(2, 3, 2, True)
        matrix.addEdgeToGraph(2, 4, 4, True)
        matrix.addEdgeToGraph(3, 4, 3, True)

        matrix.addToUserSourceDataContainerInt(1, 1, 1, True)
        matrix.addToUserSourceDataContainerInt(0, 2, 2, True)
        matrix.addToUserSourceDataContainerInt(4, 3, 3, True)
        matrix.addToUserSourceDataContainerInt(1, 4, 7, True)

        matrix.compute(3)

        matrix.addToCategoryMap(1, b"a")
        matrix.addToCategoryMap(2, b"a")
        matrix.addToCategoryMap(3, b"c")
        matrix.addToCategoryMap(4, b"c")

        assert matrix.timeToNearestDest(1) == 0
        assert matrix.timeToNearestDestPerCategory(1, b"c") == 8
        assert matrix.timeToNearestDest(3) == 0
        assert matrix.timeToNearestDestPerCategory(3, b"a") == 14
     