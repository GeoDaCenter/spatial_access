# pylint: skip-file
from transitMatrixAdapter import pyTransitMatrix
import os

class TestClass():

    def test_1(self):
        '''
        Tests that single-thread loading a graph with
        edges and calling compute does not crash and
        produces the expected result.
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

        matrix.compute(1);

        matrix.printDataFrame();

        assert matrix.get(b"A",b"A") == 0
        assert matrix.get(b"A",b"B") == 8
        assert matrix.get(B"D",b"C") == 20
        os.mkdir('tmp/')
        matrix.writeCSV(b"tmp/test_outfile_1.csv");

        assert True

    def test_2(self):

        matrix = pyTransitMatrix(infile=b"tmp/test_outfile_1.csv")

        assert matrix.get(b"A",b"A") == 0
        assert matrix.get(b"A",b"B") == 8
        assert matrix.get(b"D",b"C") == 20

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