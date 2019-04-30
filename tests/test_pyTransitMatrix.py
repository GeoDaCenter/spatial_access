import _p2pExtension


class TestClass:

    def setup_class(self):
        import os
        self.datapath = 'tests/test_py_transit_matrix_temp/'
        if not os.path.exists(self.datapath):
            os.mkdir(self.datapath)

    def teardown_class(self):
        import os
        if os.path.exists(self.datapath):
            import shutil
            shutil.rmtree(self.datapath)

    asymmetric_edges = [[0, 1, 0, 3, 0],
                        [1, 0, 3, 2, 2],
                        [3, 4, 5, 7, 2],
                        [False, False, False, False, True]]

    symmetric_edges = [[0, 1, 2, 3, 2, 4],
                       [1, 2, 3, 4, 4, 0],
                       [2, 1, 3, 4, 1, 1],
                       [True, True, True, True, True, True]]

    source_data_int = [(1, 10, 1), (0, 11, 2), (3, 12, 3)]

    dest_data_int = [(0, 21, 4), (3, 20, 6)]

    int_to_string_map = {10:b"a", 11:b"b", 12:b"c", 20:b"d", 21:b"e"}

    def _prepare_transit_matrix(self, use_symmetric_edges, is_compressible, is_symmetric, source_is_string,
                                dest_is_string, is_extended=False):
        # prep input data
        edges = TestClass.symmetric_edges if use_symmetric_edges else TestClass.asymmetric_edges
        source_data = TestClass.source_data_int
        dest_data = TestClass.source_data_int if is_symmetric else TestClass.dest_data_int
        if source_is_string:
            source_data = [(i[0], TestClass.int_to_string_map[i[1]], i[2]) for i in source_data]
        if dest_is_string:
            dest_data = [(i[0], TestClass.int_to_string_map[i[1]], i[2]) for i in dest_data]

        # prep transit matrix
        if is_extended:
            if source_is_string and dest_is_string:
                transit_matrix = _p2pExtension.pyTransitMatrixSxSxUI(isCompressible=is_compressible,
                                                                     isSymmetric=is_symmetric,
                                                                     rows=len(source_data),
                                                                     columns=len(dest_data))
            elif source_is_string and not dest_is_string:
                transit_matrix = _p2pExtension.pyTransitMatrixSxIxUI(isCompressible=is_compressible,
                                                                     isSymmetric=is_symmetric,
                                                                     rows=len(source_data),
                                                                     columns=len(dest_data))
            elif not source_is_string and dest_is_string:
                transit_matrix = _p2pExtension.pyTransitMatrixIxSxUI(isCompressible=is_compressible,
                                                                     isSymmetric=is_symmetric,
                                                                     rows=len(source_data),
                                                                     columns=len(dest_data))
            elif not source_is_string and not dest_is_string:
                transit_matrix = _p2pExtension.pyTransitMatrixIxIxUI(isCompressible=is_compressible,
                                                                     isSymmetric=is_symmetric,
                                                                     rows=len(source_data),
                                                                     columns=len(dest_data))
        else:
            if source_is_string and dest_is_string:
                transit_matrix = _p2pExtension.pyTransitMatrixSxSxUS(isCompressible=is_compressible,
                                                                         isSymmetric=is_symmetric,
                                                                         rows=len(source_data),
                                                                         columns=len(dest_data))
            elif source_is_string and not dest_is_string:
                transit_matrix = _p2pExtension.pyTransitMatrixSxIxUS(isCompressible=is_compressible,
                                                                         isSymmetric=is_symmetric,
                                                                         rows=len(source_data),
                                                                         columns=len(dest_data))
            elif not source_is_string and dest_is_string:
                transit_matrix = _p2pExtension.pyTransitMatrixIxSxUS(isCompressible=is_compressible,
                                                                         isSymmetric=is_symmetric,
                                                                         rows=len(source_data),
                                                                         columns=len(dest_data))
            elif not source_is_string and not dest_is_string:
                transit_matrix = _p2pExtension.pyTransitMatrixIxIxUS(isCompressible=is_compressible,
                                                                         isSymmetric=is_symmetric,
                                                                         rows=len(source_data),
                                                                         columns=len(dest_data))


        transit_matrix.prepareGraphWithVertices(len(edges[0]))

        if is_extended:
            edges[2] = [item + 100000 for item in edges[2]]

        transit_matrix.addEdgesToGraph(edges[0], edges[1], edges[2], edges[3])

        for source in source_data:
            transit_matrix.addToUserSourceDataContainer(source[0], source[1], source[2])
        for dest in dest_data:
            transit_matrix.addToUserDestDataContainer(dest[0], dest[1], dest[2])
        return transit_matrix

    def test_1(self):
        """
        Test symmetric int/int transitMatrix.
        """

        matrix = self._prepare_transit_matrix(use_symmetric_edges=True,
                                              is_compressible=True,
                                              is_symmetric=True,
                                              source_is_string=False,
                                              dest_is_string=False)

        matrix.compute(1)

        assert matrix.getDestsInRange(5) == {10:[10, 11],
                                              11:[10, 11],
                                              12:[12]}


        assert matrix.getSourcesInRange(8) == {10:[10, 11, 12],
                                    11:[10, 11],
                                    12:[10, 12]}

        assert matrix.getValuesBySource(10, True) == [(10, 0), (11,5), (12, 8)]

        assert matrix.getValuesBySource(11, False) == [(10, 5), (11, 0), (12, 10)]

        assert matrix.getValuesByDest(10, False) == [(10, 0), (11, 5), (12, 8)]

        assert matrix.getValuesByDest(11, True) == [(11, 0), (10, 5), (12, 10)]

        assert matrix.timeToNearestDest(12) == 0

        assert matrix.countDestsInRange(10, 7) == 2

        filename = self.datapath + 'test_1.tmx'
        matrix.writeTMX(filename.encode('utf-8'))

        matrix2 = _p2pExtension.pyTransitMatrixIxIxUS()
        matrix2.readTMX(filename.encode('utf-8'))

        assert matrix2.getDestsInRange(5) == {10: [10, 11],
                                             11: [10, 11],
                                             12: [12]}

        assert matrix2.getSourcesInRange(8) == {10: [10, 11, 12],
                                               11: [10, 11],
                                               12: [10, 12]}

        assert matrix2.getValuesBySource(10, True) == [(10, 0), (11, 5), (12, 8)]

        assert matrix2.getValuesBySource(11, False) == [(10, 5), (11, 0), (12, 10)]

        assert matrix2.getValuesByDest(10, False) == [(10, 0), (11, 5), (12, 8)]

        assert matrix2.getValuesByDest(11, True) == [(11, 0), (10, 5), (12, 10)]

        assert matrix2.timeToNearestDest(12) == 0

        assert matrix2.countDestsInRange(10, 7) == 2

    def test_2(self):
        """
        Test asymmetric int/int transitMatrix with computed values.
        """

        matrix = self._prepare_transit_matrix(use_symmetric_edges=False,
                                              is_compressible=False,
                                              is_symmetric=False,
                                              source_is_string=False,
                                              dest_is_string=False)
        matrix.compute(1)

        assert matrix.getDestsInRange(12) == {10: [21],
                                  11: [21],
                                  12: [20]}

        assert matrix.getSourcesInRange(8) == {20: [],
                                    21: [11]}

        assert matrix.getValuesBySource(10, True) == [(21, 9), (20, 16)]

        assert matrix.getValuesBySource(11, False) == [(21, 6), (20, 13)]

        assert matrix.getValuesByDest(21, False) == [(10, 9), (11, 6), (12, 16)]

        assert matrix.getValuesByDest(20, True) == [(12, 9), (11, 13), (10, 16)]

        assert matrix.timeToNearestDest(12) == 9

        assert matrix.countDestsInRange(10, 10) == 1

        filename = self.datapath + 'test_2.tmx'
        matrix.writeTMX(filename.encode('utf-8'))

        matrix2 = _p2pExtension.pyTransitMatrixIxIxUS()
        matrix2.readTMX(filename.encode('utf-8'))

        assert matrix2.getDestsInRange(12) == {10: [21],
                                              11: [21],
                                              12: [20]}

        assert matrix2.getSourcesInRange(8) == {20: [],
                                               21: [11]}

        assert matrix2.getValuesBySource(10, True) == [(21, 9), (20, 16)]

        assert matrix2.getValuesBySource(11, False) == [(21, 6), (20, 13)]

        assert matrix2.getValuesByDest(21, False) == [(10, 9), (11, 6), (12, 16)]

        assert matrix2.getValuesByDest(20, True) == [(12, 9), (11, 13), (10, 16)]

        assert matrix2.timeToNearestDest(12) == 9

        assert matrix2.countDestsInRange(10, 10) == 1

    def test_3(self):
        """
        Test symmetric string/string transitMatrix.
        """

        matrix = self._prepare_transit_matrix(use_symmetric_edges=True,
                                              is_compressible=True,
                                              is_symmetric=True,
                                              source_is_string=True,
                                              dest_is_string=True)

        matrix.compute(1)

        assert matrix.getDestsInRange(5) == {b"a": [b"a", b"b"],
                                             b"b": [b"a", b"b"],
                                             b"c": [b"c"]}

        assert matrix.getSourcesInRange(8) == {b"a": [b"a", b"b", b"c"],
                                               b"b": [b"a", b"b"],
                                               b"c": [b"a", b"c"]}

        assert matrix.getValuesBySource(b"a", True) == [(b"a", 0), (b"b", 5), (b"c", 8)]

        assert matrix.getValuesBySource(b"b", False) == [(b"a", 5), (b"b", 0), (b"c", 10)]

        assert matrix.getValuesByDest(b"a", False) == [(b"a", 0), (b"b", 5), (b"c", 8)]

        assert matrix.getValuesByDest(b"b", True) == [(b"b", 0), (b"a", 5), (b"c", 10)]

        assert matrix.timeToNearestDest(b"c") == 0

        assert matrix.countDestsInRange(b"a", 7) == 2

        filename = self.datapath + 'test_2.tmx'
        matrix.writeTMX(filename.encode('utf-8'))

        matrix2 = _p2pExtension.pyTransitMatrixSxSxUS()
        matrix2.readTMX(filename.encode('utf-8'))

        assert matrix2.getDestsInRange(5) == {b"a": [b"a", b"b"],
                                              b"b": [b"a", b"b"],
                                              b"c": [b"c"]}

        assert matrix2.getSourcesInRange(8) == {b"a": [b"a", b"b", b"c"],
                                                b"b": [b"a", b"b"],
                                                b"c": [b"a", b"c"]}

        assert matrix2.getValuesBySource(b"a", True) == [(b"a", 0), (b"b", 5), (b"c", 8)]

        assert matrix2.getValuesBySource(b"b", False) == [(b"a", 5), (b"b", 0), (b"c", 10)]

        assert matrix2.getValuesByDest(b"a", False) == [(b"a", 0), (b"b", 5), (b"c", 8)]

        assert matrix2.getValuesByDest(b"b", True) == [(b"b", 0), (b"a", 5), (b"c", 10)]

        assert matrix2.timeToNearestDest(b"c") == 0

        assert matrix2.countDestsInRange(b"a", 7) == 2

    def test_4(self):
        """
        Test asymmetric string/string transitMatrix with computed values.
        """

        matrix = self._prepare_transit_matrix(use_symmetric_edges=False,
                                              is_compressible=False,
                                              is_symmetric=False,
                                              source_is_string=True,
                                              dest_is_string=True)
        matrix.compute(1)

        assert matrix.getDestsInRange(12) == {b"a": [b"e"],
                                              b"b": [b"e"],
                                              b"c": [b"d"]}

        assert matrix.getSourcesInRange(8) == {b"d": [],
                                               b"e": [b"b"]}

        assert matrix.getValuesBySource(b"a", True) == [(b"e", 9), (b"d", 16)]

        assert matrix.getValuesBySource(b"b", False) == [(b"e", 6), (b"d", 13)]

        assert matrix.getValuesByDest(b"e", False) == [(b"a", 9), (b"b", 6), (b"c", 16)]

        assert matrix.getValuesByDest(b"d", True) == [(b"c", 9), (b"b", 13), (b"a", 16)]

        assert matrix.timeToNearestDest(b"c") == 9

        assert matrix.countDestsInRange(b"a", 10) == 1

        filename = self.datapath + 'test_4.tmx'
        matrix.writeTMX(filename.encode('utf-8'))

        matrix2 = _p2pExtension.pyTransitMatrixSxSxUS()
        matrix2.readTMX(filename.encode('utf-8'))

        assert matrix2.getDestsInRange(12) == {b"a": [b"e"],
                                               b"b": [b"e"],
                                               b"c": [b"d"]}

        assert matrix2.getSourcesInRange(8) == {b"d": [],
                                                b"e": [b"b"]}

        assert matrix2.getValuesBySource(b"a", True) == [(b"e", 9), (b"d", 16)]

        assert matrix2.getValuesBySource(b"b", False) == [(b"e", 6), (b"d", 13)]

        assert matrix2.getValuesByDest(b"e", False) == [(b"a", 9), (b"b", 6), (b"c", 16)]

        assert matrix2.getValuesByDest(b"d", True) == [(b"c", 9), (b"b", 13), (b"a", 16)]

        assert matrix2.timeToNearestDest(b"c") == 9

        assert matrix2.countDestsInRange(b"a", 10) == 1

    def test_5(self):
        """
        Test asymmetric int/string transitMatrix with computed values.
        """

        matrix = self._prepare_transit_matrix(use_symmetric_edges=False,
                                              is_compressible=False,
                                              is_symmetric=False,
                                              source_is_string=False,
                                              dest_is_string=True)
        matrix.compute(1)

        assert matrix.getDestsInRange(12) == {10: [b"e"],
                                              11: [b"e"],
                                              12: [b"d"]}

        assert matrix.getSourcesInRange(8) == {b"d": [],
                                               b"e": [11]}

        assert matrix.getValuesBySource(10, True) == [(b"e", 9), (b"d", 16)]

        assert matrix.getValuesBySource(11, False) == [(b"e", 6), (b"d", 13)]

        assert matrix.getValuesByDest(b"e", False) == [(10, 9), (11, 6), (12, 16)]

        assert matrix.getValuesByDest(b"d", True) == [(12, 9), (11, 13), (10, 16)]

        assert matrix.timeToNearestDest(12) == 9

        assert matrix.countDestsInRange(10, 10) == 1

        filename = self.datapath + 'test_5.tmx'
        matrix.writeTMX(filename.encode('utf-8'))

        matrix2 = _p2pExtension.pyTransitMatrixIxSxUS()
        matrix2.readTMX(filename.encode('utf-8'))

        assert matrix2.getDestsInRange(12) == {10: [b"e"],
                                               11: [b"e"],
                                               12: [b"d"]}

        assert matrix2.getSourcesInRange(8) == {b"d": [],
                                                b"e": [11]}

        assert matrix2.getValuesBySource(10, True) == [(b"e", 9), (b"d", 16)]

        assert matrix2.getValuesBySource(11, False) == [(b"e", 6), (b"d", 13)]

        assert matrix2.getValuesByDest(b"e", False) == [(10, 9), (11, 6), (12, 16)]

        assert matrix2.getValuesByDest(b"d", True) == [(12, 9), (11, 13), (10, 16)]

        assert matrix2.timeToNearestDest(12) == 9

        assert matrix2.countDestsInRange(10, 10) == 1

    def test_6(self):
        """
        Test asymmetric string/int transitMatrix with computed values.
        """

        matrix = self._prepare_transit_matrix(use_symmetric_edges=False,
                                              is_compressible=False,
                                              is_symmetric=False,
                                              source_is_string=True,
                                              dest_is_string=False)
        matrix.compute(1)

        assert matrix.getDestsInRange(12) == {b"a": [21],
                                              b"b": [21],
                                              b"c": [20]}

        assert matrix.getSourcesInRange(8) == {20: [],
                                               21: [b"b"]}

        assert matrix.getValuesBySource(b"a", True) == [(21, 9), (20, 16)]

        assert matrix.getValuesBySource(b"b", False) == [(21, 6), (20, 13)]

        assert matrix.getValuesByDest(21, False) == [(b"a", 9), (b"b", 6), (b"c", 16)]

        assert matrix.getValuesByDest(20, True) == [(b"c", 9), (b"b", 13), (b"a", 16)]

        assert matrix.timeToNearestDest(b"c") == 9

        assert matrix.countDestsInRange(b"a", 10) == 1

        filename = self.datapath + 'test_6.tmx'
        matrix.writeTMX(filename.encode('utf-8'))

        matrix2 = _p2pExtension.pyTransitMatrixSxIxUS()
        matrix2.readTMX(filename.encode('utf-8'))

        assert matrix2.getDestsInRange(12) == {b"a": [21],
                                               b"b": [21],
                                               b"c": [20]}

        assert matrix2.getSourcesInRange(8) == {20: [],
                                                21: [b"b"]}

        assert matrix2.getValuesBySource(b"a", True) == [(21, 9), (20, 16)]

        assert matrix2.getValuesBySource(b"b", False) == [(21, 6), (20, 13)]

        assert matrix2.getValuesByDest(21, False) == [(b"a", 9), (b"b", 6), (b"c", 16)]

        assert matrix2.getValuesByDest(20, True) == [(b"c", 9), (b"b", 13), (b"a", 16)]

        assert matrix2.timeToNearestDest(b"c") == 9

        assert matrix2.countDestsInRange(b"a", 10) == 1

    def test_7(self):
        """
        Test extended (unsigned int) value type
        """

        matrix = self._prepare_transit_matrix(use_symmetric_edges=False,
                                              is_compressible=False,
                                              is_symmetric=False,
                                              source_is_string=True,
                                              dest_is_string=False,
                                              is_extended=True)
        matrix.compute(1)


        filename = self.datapath + 'test_7.tmx'
        filename_csv = self.datapath + 'test_7.csv'
        matrix.printDataFrame()
        matrix.writeTMX(filename.encode('utf-8'))

        matrix.writeCSV(filename_csv.encode('utf-8'))

        matrix2 = _p2pExtension.pyTransitMatrixSxIxUI()
        matrix2.readTMX(filename.encode('utf-8'))
        matrix2.printDataFrame()

        matrix3 = _p2pExtension.pyTransitMatrixSxIxUI()
        matrix3.readCSV(filename_csv.encode('utf-8'))
        matrix3.printDataFrame()

