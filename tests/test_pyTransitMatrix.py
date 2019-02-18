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

        matrix.addToCategoryMap(10, "a")
        matrix.addToCategoryMap(11, "a")
        matrix.addToCategoryMap(12, "b")

        time_to_nearest_by_cat = matrix.timeToNearestDestPerCategory(10, "b")

        assert time_to_nearest_by_cat == 8

        count_dests_in_range_by_cat = matrix.countDestsInRangePerCategory(10, "a", 7)

        assert count_dests_in_range_by_cat == 2

        primary_dataset_ids = matrix.getPrimaryDatasetIds()

        assert primary_dataset_ids == [10, 11, 12]

        secondary_dataset_ids = matrix.getSecondaryDatasetIds()

        assert secondary_dataset_ids == [10, 11, 12]
        is_symmetric = matrix.getIsSymmetric()

        assert is_symmetric

        dataset = matrix.getDataset()

        assert dataset == [[0, 5, 8, 0, 9, 0]]

        assert matrix.getRows() == 3
        assert matrix.getCols() == 3

    def test_2(self):
        """
        Test asymmetric int/int transitMatrix with computed values.
        """
        matrix = transitMatrixAdapterIxI.pyTransitMatrix(False, 3, 2)
        matrix.prepareGraphWithVertices(4)
        matrix.addEdgeToGraph(0, 1, 3, False)
        matrix.addEdgeToGraph(1, 0, 4, False)
        matrix.addEdgeToGraph(0, 3, 5, False)
        matrix.addEdgeToGraph(3, 2, 7, False)
        matrix.addEdgeToGraph(0, 2, 2, True)

        matrix.addToUserSourceDataContainer(2, 10, 5)
        matrix.addToUserSourceDataContainer(1, 11, 4)
        matrix.addToUserSourceDataContainer(0, 12, 1)

        matrix.addToUserDestDataContainer(0, 21, 4)
        matrix.addToUserDestDataContainer(3, 20, 6)

        matrix.compute(1)

        dests_in_range = matrix.getDestsInRange(12, 1)

        assert dests_in_range == {10: [21],
                                  11: [21],
                                  12: [21, 20]}

        sources_in_range = matrix.getSourcesInRange(8, 1)

        assert sources_in_range == {20: [],
                                    21: [12]}

        values_by_source_10 = matrix.getValuesBySource(10, True)

        assert values_by_source_10 == [(21, 11), (20, 18)]

        values_by_source_11 = matrix.getValuesBySource(11, False)

        assert values_by_source_11 == [(21, 12), (20, 19)]

        values_by_dest_21 = matrix.getValuesByDest(21, False)

        assert values_by_dest_21 == [(10, 11), (11, 12), (12, 5)]

        values_by_dest_20 = matrix.getValuesByDest(20, True)

        assert values_by_dest_20 == [(12, 12), (10, 18), (11, 19)]

        time_to_nearest = matrix.timeToNearestDest(12)

        assert time_to_nearest == 5

        count_dests_in_range_10 = matrix.countDestsInRange(10, 7)

        assert count_dests_in_range_10 == 0

        matrix.addToCategoryMap(21, "a")
        matrix.addToCategoryMap(20, "b")

        time_to_nearest_by_cat = matrix.timeToNearestDestPerCategory(10, "b")

        assert time_to_nearest_by_cat == 18

        count_dests_in_range_by_cat = matrix.countDestsInRangePerCategory(10, "a", 20)

        assert count_dests_in_range_by_cat == 1

        primary_dataset_ids = matrix.getPrimaryDatasetIds()

        assert primary_dataset_ids == [10, 11, 12]

        secondary_dataset_ids = matrix.getSecondaryDatasetIds()

        assert secondary_dataset_ids == [21, 20]
        is_symmetric = matrix.getIsSymmetric()

        assert not is_symmetric

        dataset = matrix.getDataset()

        assert dataset == [[11, 18], [12, 19], [5, 12]]

        assert matrix.getRows() == 3
        assert matrix.getCols() == 2



    def test_3(self):
        """
        Test symmetric int/int transitMatrix with set values.
        """
        matrix = transitMatrixAdapterIxI.pyTransitMatrix(True, 3, 3)
        matrix.setPrimaryDatasetIds([10, 11, 12])
        matrix.setSecondaryDatasetIds([10, 11, 12])
        matrix.setDataset([[0, 5, 8, 0, 9, 0]])

        dests_in_range = matrix.getDestsInRange(5, 1)

        assert dests_in_range == {10: [10, 11],
                                  11: [10, 11],
                                  12: [12]}

        sources_in_range = matrix.getSourcesInRange(8, 1)

        assert sources_in_range == {10: [10, 11, 12],
                                    11: [10, 11],
                                    12: [10, 12]}
        values_by_source_10 = matrix.getValuesBySource(10, True)

        assert values_by_source_10 == [(10, 0), (11, 5), (12, 8)]

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

        matrix.addToCategoryMap(10, "a")
        matrix.addToCategoryMap(11, "a")
        matrix.addToCategoryMap(12, "b")

        time_to_nearest_by_cat = matrix.timeToNearestDestPerCategory(10, "b")

        assert time_to_nearest_by_cat == 8

        count_dests_in_range_by_cat = matrix.countDestsInRangePerCategory(10, "a", 7)

        assert count_dests_in_range_by_cat == 2

        primary_dataset_ids = matrix.getPrimaryDatasetIds()

        assert primary_dataset_ids == [10, 11, 12]

        secondary_dataset_ids = matrix.getSecondaryDatasetIds()

        assert secondary_dataset_ids == [10, 11, 12]
        is_symmetric = matrix.getIsSymmetric()

        assert is_symmetric

        dataset = matrix.getDataset()

        assert dataset == [[0, 5, 8, 0, 9, 0]]

        assert matrix.getRows() == 3
        assert matrix.getCols() == 3


    def test_4(self):
        """
        Test asymmetric int/int transitMatrix with set values.
        """
        matrix = transitMatrixAdapterIxI.pyTransitMatrix(False, 3, 2)
        matrix.setPrimaryDatasetIds([10, 11, 12])
        matrix.setSecondaryDatasetIds([21, 20])
        matrix.setDataset([[11, 18], [12, 19], [5, 12]])
        dests_in_range = matrix.getDestsInRange(12, 1)

        assert dests_in_range == {10: [21],
                                  11: [21],
                                  12: [21, 20]}

        sources_in_range = matrix.getSourcesInRange(8, 1)

        assert sources_in_range == {20: [],
                                    21: [12]}

        values_by_source_10 = matrix.getValuesBySource(10, True)

        assert values_by_source_10 == [(21, 11), (20, 18)]

        values_by_source_11 = matrix.getValuesBySource(11, False)

        assert values_by_source_11 == [(21, 12), (20, 19)]

        values_by_dest_21 = matrix.getValuesByDest(21, False)

        assert values_by_dest_21 == [(10, 11), (11, 12), (12, 5)]

        values_by_dest_20 = matrix.getValuesByDest(20, True)

        assert values_by_dest_20 == [(12, 12), (10, 18), (11, 19)]

        time_to_nearest = matrix.timeToNearestDest(12)

        assert time_to_nearest == 5

        count_dests_in_range_10 = matrix.countDestsInRange(10, 7)

        assert count_dests_in_range_10 == 0

        matrix.addToCategoryMap(21, "a")
        matrix.addToCategoryMap(20, "b")

        time_to_nearest_by_cat = matrix.timeToNearestDestPerCategory(10, "b")

        assert time_to_nearest_by_cat == 18

        count_dests_in_range_by_cat = matrix.countDestsInRangePerCategory(10, "a", 20)

        assert count_dests_in_range_by_cat == 1

        primary_dataset_ids = matrix.getPrimaryDatasetIds()

        assert primary_dataset_ids == [10, 11, 12]

        secondary_dataset_ids = matrix.getSecondaryDatasetIds()

        assert secondary_dataset_ids == [21, 20]
        is_symmetric = matrix.getIsSymmetric()

        assert not is_symmetric

        dataset = matrix.getDataset()

        assert dataset == [[11, 18], [12, 19], [5, 12]]

        assert matrix.getRows() == 3
        assert matrix.getCols() == 2

    def test_5(self):
        """
        Test asymmetric str/int transitMatrix with computed values.
        """
        matrix = transitMatrixAdapterSxI.pyTransitMatrix(False, 3, 2)
        matrix.prepareGraphWithVertices(4)
        matrix.addEdgeToGraph(0, 1, 3, False)
        matrix.addEdgeToGraph(1, 0, 4, False)
        matrix.addEdgeToGraph(0, 3, 5, False)
        matrix.addEdgeToGraph(3, 2, 7, False)
        matrix.addEdgeToGraph(0, 2, 2, True)

        matrix.addToUserSourceDataContainer(2, "A", 5)
        matrix.addToUserSourceDataContainer(1, "B", 4)
        matrix.addToUserSourceDataContainer(0, "C", 1)

        matrix.addToUserDestDataContainer(0, 20, 4)
        matrix.addToUserDestDataContainer(3, 21, 6)

        matrix.compute(1)

        dests_in_range = matrix.getDestsInRange(12, 1)

        assert dests_in_range == {"A": [20],
                                  "B": [20],
                                  "C": [20, 21]}

        sources_in_range = matrix.getSourcesInRange(8, 1)

        assert sources_in_range == {21: [],
                                    20: ["C"]}

        values_by_source_A = matrix.getValuesBySource("A", True)

        assert values_by_source_A == [(20, 11), (21, 18)]

        values_by_source_B = matrix.getValuesBySource("B", False)

        assert values_by_source_B == [(20, 12), (21, 19)]

        values_by_dest_21 = matrix.getValuesByDest(21, False)

        assert values_by_dest_21 == [("A", 18), ("B", 19), ("C", 12)]

        values_by_dest_20 = matrix.getValuesByDest(20, True)

        assert values_by_dest_20 == [("C", 5), ("A", 11), ("B", 12)]

        time_to_nearest = matrix.timeToNearestDest("C")

        assert time_to_nearest == 5

        count_dests_in_range_A = matrix.countDestsInRange("A", 7)

        assert count_dests_in_range_A == 0

        matrix.addToCategoryMap(21, "a")
        matrix.addToCategoryMap(20, "b")

        time_to_nearest_by_cat = matrix.timeToNearestDestPerCategory("A", "b")

        assert time_to_nearest_by_cat == 11

        count_dests_in_range_by_cat = matrix.countDestsInRangePerCategory("A", "a", 20)

        assert count_dests_in_range_by_cat == 1

        primary_dataset_ids = matrix.getPrimaryDatasetIds()

        assert primary_dataset_ids == [b"A", b"B", b"C"]

        secondary_dataset_ids = matrix.getSecondaryDatasetIds()

        assert secondary_dataset_ids == [20, 21]
        is_symmetric = matrix.getIsSymmetric()

        assert not is_symmetric

        dataset = matrix.getDataset()

        assert dataset == [[11, 18], [12, 19], [5, 12]]

        assert matrix.getRows() == 3
        assert matrix.getCols() == 2

    def test_6(self):
        """
        Test asymmetric str/int transitMatrix with set values.
        """
        matrix = transitMatrixAdapterSxI.pyTransitMatrix(False, 3, 2)
        matrix.setPrimaryDatasetIds([b"A", b"B", b"C"])
        matrix.setSecondaryDatasetIds([20, 21])
        matrix.setDataset([[11, 18], [12, 19], [5, 12]])

        dests_in_range = matrix.getDestsInRange(12, 1)

        assert dests_in_range == {"A": [20],
                                  "B": [20],
                                  "C": [20, 21]}

        sources_in_range = matrix.getSourcesInRange(8, 1)

        assert sources_in_range == {21: [],
                                    20: ["C"]}

        values_by_source_A = matrix.getValuesBySource("A", True)

        assert values_by_source_A == [(20, 11), (21, 18)]

        values_by_source_B = matrix.getValuesBySource("B", False)

        assert values_by_source_B == [(20, 12), (21, 19)]

        values_by_dest_21 = matrix.getValuesByDest(21, False)

        assert values_by_dest_21 == [("A", 18), ("B", 19), ("C", 12)]

        values_by_dest_20 = matrix.getValuesByDest(20, True)

        assert values_by_dest_20 == [("C", 5), ("A", 11), ("B", 12)]

        time_to_nearest = matrix.timeToNearestDest("C")

        assert time_to_nearest == 5

        count_dests_in_range_A = matrix.countDestsInRange("A", 7)

        assert count_dests_in_range_A == 0

        matrix.addToCategoryMap(21, "a")
        matrix.addToCategoryMap(20, "b")

        time_to_nearest_by_cat = matrix.timeToNearestDestPerCategory("A", "b")

        assert time_to_nearest_by_cat == 11

        count_dests_in_range_by_cat = matrix.countDestsInRangePerCategory("A", "a", 20)

        assert count_dests_in_range_by_cat == 1

        primary_dataset_ids = matrix.getPrimaryDatasetIds()

        assert primary_dataset_ids == [b"A", b"B", b"C"]

        secondary_dataset_ids = matrix.getSecondaryDatasetIds()

        assert secondary_dataset_ids == [20, 21]
        is_symmetric = matrix.getIsSymmetric()

        assert not is_symmetric

        dataset = matrix.getDataset()

        assert dataset == [[11, 18], [12, 19], [5, 12]]

        assert matrix.getRows() == 3
        assert matrix.getCols() == 2


    def test_7(self):
        """
        Test asymmetric int/str transitMatrix with computed values.
        """
        matrix = transitMatrixAdapterIxS.pyTransitMatrix(False, 3, 2)
        matrix.prepareGraphWithVertices(4)
        matrix.addEdgeToGraph(0, 1, 3, False)
        matrix.addEdgeToGraph(1, 0, 4, False)
        matrix.addEdgeToGraph(0, 3, 5, False)
        matrix.addEdgeToGraph(3, 2, 7, False)
        matrix.addEdgeToGraph(0, 2, 2, True)

        matrix.addToUserSourceDataContainer(2, 10, 5)
        matrix.addToUserSourceDataContainer(1, 11, 4)
        matrix.addToUserSourceDataContainer(0, 12, 1)

        matrix.addToUserDestDataContainer(0, "A", 4)
        matrix.addToUserDestDataContainer(3, "B", 6)

        matrix.compute(1)

        dests_in_range = matrix.getDestsInRange(12, 1)

        assert dests_in_range == {10: ["A"],
                                  11: ["A"],
                                  12: ["A", "B"]}

        sources_in_range = matrix.getSourcesInRange(8, 1)

        assert sources_in_range == {"A": [12],
                                    "B": []}

        values_by_source_10 = matrix.getValuesBySource(10, True)

        assert values_by_source_10 == [("A", 11), ("B", 18)]

        values_by_source_11 = matrix.getValuesBySource(11, False)

        assert values_by_source_11 == [("A", 12), ("B", 19)]

        values_by_dest_A = matrix.getValuesByDest("A", False)

        assert values_by_dest_A == [(10, 11), (11, 12), (12, 5)]

        values_by_dest_B = matrix.getValuesByDest("B", True)

        assert values_by_dest_B == [(12, 12), (10, 18), (11, 19)]

        time_to_nearest = matrix.timeToNearestDest(12)

        assert time_to_nearest == 5

        count_dests_in_range_10 = matrix.countDestsInRange(10, 7)

        assert count_dests_in_range_10 == 0

        matrix.addToCategoryMap("A", "a")
        matrix.addToCategoryMap("B", "b")

        time_to_nearest_by_cat = matrix.timeToNearestDestPerCategory(10, "b")

        assert time_to_nearest_by_cat == 18

        count_dests_in_range_by_cat = matrix.countDestsInRangePerCategory(10, "a", 20)

        assert count_dests_in_range_by_cat == 1

        primary_dataset_ids = matrix.getPrimaryDatasetIds()

        assert primary_dataset_ids == [10, 11, 12]

        secondary_dataset_ids = matrix.getSecondaryDatasetIds()

        assert secondary_dataset_ids == [b"A", b"B"]
        is_symmetric = matrix.getIsSymmetric()

        assert not is_symmetric

        dataset = matrix.getDataset()

        assert dataset == [[11, 18], [12, 19], [5, 12]]

        assert matrix.getRows() == 3
        assert matrix.getCols() == 2

    def test_8(self):
        """
        Test asymmetric int/str transitMatrix with set values.
        """
        matrix = transitMatrixAdapterIxS.pyTransitMatrix(False, 3, 2)
        matrix.setPrimaryDatasetIds([10, 11, 12])
        matrix.setSecondaryDatasetIds([b"A", b"B"])
        matrix.setDataset([[11, 18], [12, 19], [5, 12]])

        dests_in_range = matrix.getDestsInRange(12, 1)

        assert dests_in_range == {10: ["A"],
                                  11: ["A"],
                                  12: ["A", "B"]}

        sources_in_range = matrix.getSourcesInRange(8, 1)

        assert sources_in_range == {"A": [12],
                                    "B": []}

        values_by_source_10 = matrix.getValuesBySource(10, True)

        assert values_by_source_10 == [("A", 11), ("B", 18)]

        values_by_source_11 = matrix.getValuesBySource(11, False)

        assert values_by_source_11 == [("A", 12), ("B", 19)]

        values_by_dest_A = matrix.getValuesByDest("A", False)

        assert values_by_dest_A == [(10, 11), (11, 12), (12, 5)]

        values_by_dest_B = matrix.getValuesByDest("B", True)

        assert values_by_dest_B == [(12, 12), (10, 18), (11, 19)]

        time_to_nearest = matrix.timeToNearestDest(12)

        assert time_to_nearest == 5

        count_dests_in_range_10 = matrix.countDestsInRange(10, 7)

        assert count_dests_in_range_10 == 0

        matrix.addToCategoryMap("A", "a")
        matrix.addToCategoryMap("B", "b")

        time_to_nearest_by_cat = matrix.timeToNearestDestPerCategory(10, "b")

        assert time_to_nearest_by_cat == 18

        count_dests_in_range_by_cat = matrix.countDestsInRangePerCategory(10, "a", 20)

        assert count_dests_in_range_by_cat == 1

        primary_dataset_ids = matrix.getPrimaryDatasetIds()

        assert primary_dataset_ids == [10, 11, 12]

        secondary_dataset_ids = matrix.getSecondaryDatasetIds()

        assert secondary_dataset_ids == [b"A", b"B"]
        is_symmetric = matrix.getIsSymmetric()

        assert not is_symmetric

        dataset = matrix.getDataset()

        assert dataset == [[11, 18], [12, 19], [5, 12]]

        assert matrix.getRows() == 3
        assert matrix.getCols() == 2

    def test_11(self):
        """
        Test asymmetric str/str transitMatrix with computed values.
        """
        matrix = transitMatrixAdapterSxS.pyTransitMatrix(False, 3, 2)
        matrix.prepareGraphWithVertices(4)
        matrix.addEdgeToGraph(0, 1, 3, False)
        matrix.addEdgeToGraph(1, 0, 4, False)
        matrix.addEdgeToGraph(0, 3, 5, False)
        matrix.addEdgeToGraph(3, 2, 7, False)
        matrix.addEdgeToGraph(0, 2, 2, True)

        matrix.addToUserSourceDataContainer(2, "A", 5)
        matrix.addToUserSourceDataContainer(1, "B", 4)
        matrix.addToUserSourceDataContainer(0, "C", 1)

        matrix.addToUserDestDataContainer(0, "dest_A", 4)
        matrix.addToUserDestDataContainer(3, "dest_B", 6)

        matrix.compute(1)

        dests_in_range = matrix.getDestsInRange(12, 1)

        assert dests_in_range == {"A": ["dest_A"],
                                  "B": ["dest_A"],
                                  "C": ["dest_A", "dest_B"]}

        sources_in_range = matrix.getSourcesInRange(8, 1)

        assert sources_in_range == {"dest_A": ["C"],
                                    "dest_B": []}

        values_by_source_A = matrix.getValuesBySource("A", True)

        assert values_by_source_A == [("dest_A", 11), ("dest_B", 18)]

        values_by_source_B = matrix.getValuesBySource("B", False)

        assert values_by_source_B == [("dest_A", 12), ("dest_B", 19)]

        values_by_dest_A = matrix.getValuesByDest("dest_A", False)

        assert values_by_dest_A == [("A", 11), ("B", 12), ("C", 5)]

        values_by_dest_B = matrix.getValuesByDest("dest_B", True)

        assert values_by_dest_B == [("C", 12), ("A", 18), ("B", 19)]

        time_to_nearest = matrix.timeToNearestDest("C")

        assert time_to_nearest == 5

        count_dests_in_range_A = matrix.countDestsInRange("A", 7)

        assert count_dests_in_range_A == 0

        matrix.addToCategoryMap("dest_A", "a")
        matrix.addToCategoryMap("dest_B", "b")

        time_to_nearest_by_cat = matrix.timeToNearestDestPerCategory("A", "b")

        assert time_to_nearest_by_cat == 18

        count_dests_in_range_by_cat = matrix.countDestsInRangePerCategory("A", "a", 20)

        assert count_dests_in_range_by_cat == 1

        primary_dataset_ids = matrix.getPrimaryDatasetIds()

        assert primary_dataset_ids == [b"A", b"B", b"C"]

        secondary_dataset_ids = matrix.getSecondaryDatasetIds()

        assert secondary_dataset_ids == [b"dest_A", b"dest_B"]
        is_symmetric = matrix.getIsSymmetric()

        assert not is_symmetric

        dataset = matrix.getDataset()

        assert dataset == [[11, 18], [12, 19], [5, 12]]

        assert matrix.getRows() == 3
        assert matrix.getCols() == 2

    def test_12(self):
        """
        Test asymmetric str/str transitMatrix with set values.
        """
        matrix = transitMatrixAdapterSxS.pyTransitMatrix(False, 3, 2)
        matrix.setPrimaryDatasetIds([b"A", b"B", b"C"])
        matrix.setSecondaryDatasetIds([b"dest_A", b"dest_B"])
        matrix.setDataset([[11, 18], [12, 19], [5, 12]])

        dests_in_range = matrix.getDestsInRange(12, 1)

        assert dests_in_range == {"A": ["dest_A"],
                                  "B": ["dest_A"],
                                  "C": ["dest_A", "dest_B"]}

        sources_in_range = matrix.getSourcesInRange(8, 1)

        assert sources_in_range == {"dest_A": ["C"],
                                    "dest_B": []}

        values_by_source_A = matrix.getValuesBySource("A", True)

        assert values_by_source_A == [("dest_A", 11), ("dest_B", 18)]

        values_by_source_B = matrix.getValuesBySource("B", False)

        assert values_by_source_B == [("dest_A", 12), ("dest_B", 19)]

        values_by_dest_A = matrix.getValuesByDest("dest_A", False)

        assert values_by_dest_A == [("A", 11), ("B", 12), ("C", 5)]

        values_by_dest_B = matrix.getValuesByDest("dest_B", True)

        assert values_by_dest_B == [("C", 12), ("A", 18), ("B", 19)]

        time_to_nearest = matrix.timeToNearestDest("C")

        assert time_to_nearest == 5

        count_dests_in_range_A = matrix.countDestsInRange("A", 7)

        assert count_dests_in_range_A == 0

        matrix.addToCategoryMap("dest_A", "a")
        matrix.addToCategoryMap("dest_B", "b")

        time_to_nearest_by_cat = matrix.timeToNearestDestPerCategory("A", "b")

        assert time_to_nearest_by_cat == 18

        count_dests_in_range_by_cat = matrix.countDestsInRangePerCategory("A", "a", 20)

        assert count_dests_in_range_by_cat == 1

        primary_dataset_ids = matrix.getPrimaryDatasetIds()

        assert primary_dataset_ids == [b"A", b"B", b"C"]

        secondary_dataset_ids = matrix.getSecondaryDatasetIds()

        assert secondary_dataset_ids == [b"dest_A", b"dest_B"]
        is_symmetric = matrix.getIsSymmetric()

        assert not is_symmetric

        dataset = matrix.getDataset()

        assert dataset == [[11, 18], [12, 19], [5, 12]]

        assert matrix.getRows() == 3
        assert matrix.getCols() == 2