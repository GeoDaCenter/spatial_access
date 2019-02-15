#include <iostream>
#include "transitMatrix.cpp"
#include <vector>
#include <unordered_map>


using namespace lmnoel;
int main()
{
    transitMatrix<std::string, std::string> tm(false, 9, 10);
    tm.prepareGraphWithVertices(7);
    tm.addEdgeToGraph(0, 1, 1, true);
    tm.addEdgeToGraph(1, 2, 6, true);
    tm.addEdgeToGraph(0, 3, 5, true);
    tm.addEdgeToGraph(1, 3, 2, true);
    tm.addEdgeToGraph(0, 4, 2, true);
    tm.addEdgeToGraph(3, 5, 3, true);
    tm.addEdgeToGraph(2, 5, 1, true);
    tm.addEdgeToGraph(1, 3, 1, true);
    tm.addEdgeToGraph(4, 5, 1, true);
    tm.addEdgeToGraph(2, 1, 1, true);
    tm.addEdgeToGraph(6, 5, 1, true);
    tm.addEdgeToGraph(5, 4, 1, true);
    tm.addEdgeToGraph(6, 3, 1, true);
    tm.addEdgeToGraph(6, 1, 1, true);
    tm.addEdgeToGraph(6, 2, 1, true);


    tm.addToUserSourceDataContainer(1, "a", 4);
    tm.addToUserSourceDataContainer(0, "c", 2);
    tm.addToUserSourceDataContainer(2, "d", 3);
    tm.addToUserSourceDataContainer(4, "j", 1);
    tm.addToUserSourceDataContainer(4, "j", 1);
    tm.addToUserSourceDataContainer(4, "j", 1);
    tm.addToUserSourceDataContainer(4, "j", 1);
    tm.addToUserSourceDataContainer(4, "j", 1);
    tm.addToUserSourceDataContainer(4, "j", 1);

    tm.addToUserDestDataContainer(2, "k", 3);
    tm.addToUserDestDataContainer(3, "l", 2);
    tm.addToUserDestDataContainer(5, "p", 5);
    tm.addToUserDestDataContainer(5, "p", 5);
    tm.addToUserDestDataContainer(5, "p", 5);
    tm.addToUserDestDataContainer(5, "p", 5);
    tm.addToUserDestDataContainer(5, "p", 5);
    tm.addToUserDestDataContainer(5, "p", 5);
    tm.addToUserDestDataContainer(5, "p", 5);
    tm.addToUserDestDataContainer(5, "p", 5);


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

  
