# pylint: skip-file
import transitMatrixAdapterIxI
import transitMatrixAdapterSxI
import transitMatrixAdapterIxS
import transitMatrixAdapterSxS

class TestClass():

    def setup_class(self):
        pass

    def teardown_class(self):
        pass

    def test_1(self):
        """
        Test symmetric int/int transitMatrix with computed values.
        """
        matrix = transitMatrixAdapterIxI.pyTransitMatrix(True, 3, 3)
        matrix.prepareGraphWithVertices(5)

        matrix.addEdgeToGraph(0, 1, 2, True)
        matrix.addEdgeToGraph(1, 2, 1, True)
        matrix.addEdgeToGraph(2, 3, 3, True)
        matrix.addEdgeToGraph(3, 4, 4, True)
        matrix.addEdgeToGraph(2, 4, 1, True)
        matrix.addEdgeToGraph(4, 0, 1, True)

        matrix.addToUserSourceDataContainer(1, 10, 1)
        matrix.addToUserSourceDataContainer(4, 11, 2)
        matrix.addToUserSourceDataContainer(3, 12, 3)

        matrix.addToUserDestDataContainer(1, 10, 1)
        matrix.addToUserDestDataContainer(4, 11, 2)
        matrix.addToUserDestDataContainer(3, 12, 3)

        matrix.compute(1)

        dests_in_range = matrix.getDestsInRange(5, 1)

        assert dests_in_range == {10:[10, 11],
                                  11:[10, 11],
                                  12:[12]}

        sources_in_range = matrix.getSourcesInRange(8, 1)

        assert sources_in_range == {10:[10, 11, 12],
                                    11:[10, 11],
                                    12:[10, 12]}
        values_by_source_10 = matrix.getValuesBySource(10, True)

        assert values_by_source_10 == [(10, 0), (11,5), (12, 8)]

        values_by_source_11 = matrix.getValuesBySource(11, False)

        assert values_by_source_11 == [(10, 5), (11, 0), (12, 9)]

        values_by_dest_10 = matrix.getValuesByDest(10, False)

        assert values_by_dest_10 == [(10, 0), (11, 5), (12, 8)]

        values_by_dest_11 = matrix.getValuesByDest(11, True)

        assert values_by_dest_11 == [(11, 0), (10, 5), (12, 9)]

        time_to_nearest = matrix.timeToNearestDest(12)

        assert time_to_nearest == 0

        count_dests_in_range_10 = matrix.countDestsInRange(10, 7)

        assert count_dests_in_range_10 == 2

        matrix.addToCategoryMap(10, b"a")
        matrix.addToCategoryMap(11, b"a")
        matrix.addToCategoryMap(12, b"b")

        time_to_nearest_by_cat = matrix.timeToNearestDestPerCategory(10, b"b")

        assert time_to_nearest_by_cat == 8

        count_dests_in_range_by_cat = matrix.countDestsInRangePerCategory(10, b"a", 7)

        assert count_dests_in_range_by_cat == 2

        primary_dataset_ids = matrix.getPrimaryDatasetIds()

        assert primary_dataset_ids == [10, 11, 12]

        secondary_dataset_ids = matrix.getSecondaryDatasetIds()

        assert secondary_dataset_ids == [10, 11, 12]
        is_symmetric = matrix.getIsSymmetric()

        assert is_symmetric

        dataset = matrix.getDataset()

        assert dataset == [[0, 5, 8, 0, 9, 0]]

    def test_2(self):
        """
        Test asymmetric int/int transitMatrix with computed values.
        """
        pass

    def test_3(self):
        """
        Test symmetric int/int transitMatrix with set values.
        """
        pass

    def test_4(self):
        """
        Test asymmetric int/int transitMatrix with set values.
        """
        pass