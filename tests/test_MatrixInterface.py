from transitMatrixAdapter import pyTransitMatrix

    # // lmnoel::transitMatrix matrix(5);
    # // matrix.addEdgeToGraph(0, 1, 5, true);
    # // matrix.addEdgeToGraph(1, 2, 6, true);
    # // matrix.addEdgeToGraph(2, 3, 2, true);
    # // matrix.addEdgeToGraph(2, 4, 4, false);
    # // matrix.addEdgeToGraph(3, 4, 3, true);

    # // matrix.addToUserSourceDataContainer(1, "A", 1, true);
    # // matrix.addToUserSourceDataContainer(0, "B", 2, true);
    # // matrix.addToUserSourceDataContainer(4, "C", 3, true);
    # // matrix.addToUserSourceDataContainer(1, "D", 7, true);

    # // std::cout << "dest data" << std::endl;
    # // matrix.userDestDataContainer.print();

    # // matrix.compute(1, 3);
    # // matrix.writeCSV("outfile.csv");
class TestClass():

    def test_1(self):
        '''
        Tests that single-thread loading a graph with
        edges and calling compute does not crash and
        produces the expected result.
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

        matrix.compute(1);

        matrix.printDataFrame();

        assert matrix.get(b"A",b"A") == 0
        assert matrix.get(b"A",b"B") == 8
        assert matrix.get(b"D",b"C") == 20

        matrix.writeCSV(b"test_outfile.csv");

        assert True

    def test_2(self):

        matrix = pyTransitMatrix(infile=b"test_outfile.csv")

        assert matrix.get(b"A",b"A") == 0
        assert matrix.get(b"A",b"B") == 8
        assert matrix.get(b"D",b"C") == 20