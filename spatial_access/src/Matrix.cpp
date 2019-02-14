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
    transitMatrix<std::string, std::string> tm(false, 9, 7);
    tm.prepareGraphWithVertices(5);
    tm.addEdgeToGraph(0, 1, 1, true);
    tm.addEdgeToGraph(1, 2, 6, true);
    tm.addEdgeToGraph(0, 3, 5, true);
    tm.addEdgeToGraph(1, 3, 2, true);
    tm.addToUserSourceDataContainer(1, "a", 4);
    tm.addToUserSourceDataContainer(0, "c", 2);
    tm.addToUserSourceDataContainer(0, "d", 2);
    tm.addToUserSourceDataContainer(0, "e", 2);
    tm.addToUserSourceDataContainer(0, "f", 2);
    tm.addToUserSourceDataContainer(0, "g", 2);
    tm.addToUserSourceDataContainer(0, "h", 2);
    tm.addToUserSourceDataContainer(0, "j", 2);
    tm.addToUserSourceDataContainer(0, "i", 2);

    tm.addToUserDestDataContainer(2, "k", 3);
    tm.addToUserDestDataContainer(3, "l", 2);
    tm.addToUserDestDataContainer(2, "m", 4);
    tm.addToUserDestDataContainer(1, "n", 2);
    tm.addToUserDestDataContainer(3, "o", 7);
    tm.addToUserDestDataContainer(2, "p", 1);
    tm.addToUserDestDataContainer(1, "q", 1);

    tm.compute(1);

    tm.printDataFrame();

//
//    tm.printDataFrame();
//    auto destsInRange = tm.getDestsInRange(10, 1);
////
//    auto sourcesInRange = tm.getSourcesInRange(10, 1);
//
//    auto valuesBySource = tm.getValuesBySource("a", true);
//
//    auto valuesByDest = tm.getValuesByDest("d", true);
////    auto timeToNearestDestPerCatagory = tm.timeToNearestDestPerCategory("a", "cat1");
////    auto countdestsInRangePerCategory = tm.countDestsInRangePerCategory("b", "cat2", 10);
//    auto timeToNearestDest = tm.timeToNearestDest("a");
//    auto countdestsInRange = tm.countDestsInRange("b", 10);
    return 0;
};

  
