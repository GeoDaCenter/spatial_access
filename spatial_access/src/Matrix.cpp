#include <iostream>
#include "transitMatrix.cpp"
#include <vector>
#include <unordered_map>

void printArray(std::vector<unsigned long int> array)
{
    for (auto element : array)
    {
        std::cout << element << ", ";
    }
    std::cout << std::endl;
}

void printMapOfArrays(std::unordered_map<long unsigned int, std::vector<long unsigned int>> map)
{
    for (auto element : map)
    {
        std::cout << "row " << element.first << ":" << std::endl;
        printArray(element.second);
    }
}

using namespace lmnoel;
int main()
{
    transitMatrix<unsigned long int, std::string> tm(false, 2, 2);
//    tm.prepareGraphWithVertices(5);
//    tm.addEdgeToGraph(0, 1, 1, true);
//    tm.addEdgeToGraph(1, 2, 6, true);
//    tm.addEdgeToGraph(0, 3, 5, true);
//    tm.addEdgeToGraph(1, 3, 2, true);
//    tm.addToUserSourceDataContainer(1, "a", 4);
//    tm.addToUserSourceDataContainer(0, "b", 2);
//    tm.addToUserDestDataContainer(2, "c", 5);
//    tm.addToUserDestDataContainer(3, "d", 1);
//
//    tm.compute(1);
//
//    tm.printDataFrame();


    std::vector<unsigned long int> primaryIds = {11, 12};
    std::vector<std::string> secondaryIds = {"c", "d"};
    tm.setPrimaryDatasetIds(primaryIds);
    tm.setSecondaryDatasetIds(secondaryIds);
    tm.addToCategoryMap("c", "cat1");
    tm.addToCategoryMap("d", "cat2");
    std::vector<unsigned short int> row1 = {15, 7};
    std::vector<unsigned short int> row2 = {14, 6};
    tm.setDatasetRow(row1, 0);
    tm.setDatasetRow(row2, 1);
    tm.printDataFrame();
    auto destsInRange = tm.getDestsInRange(10, 1);
//
    auto sourcesInRange = tm.getSourcesInRange(10, 1);

    auto valuesBySource = tm.getValuesBySource(11, true);

    auto valuesByDest = tm.getValuesByDest("d", true);
    auto timeToNearestDestPerCatagory = tm.timeToNearestDestPerCategory(11, "cat1");
    auto countdestsInRangePerCategory = tm.countDestsInRangePerCategory(11, "cat2", 10);
    auto timeToNearestDest = tm.timeToNearestDest(12);
    auto countdestsInRange = tm.countDestsInRange(11, 10);
    return 0;
};

  
