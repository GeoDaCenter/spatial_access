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
    transitMatrix<std::string, std::string> tm(false, 2, 2);
    tm.prepareGraphWithVertices(5);
    tm.addEdgeToGraph(0, 1, 1, true);
    tm.addEdgeToGraph(1, 2, 6, true);
    tm.addEdgeToGraph(0, 3, 5, true);
    tm.addEdgeToGraph(1, 3, 2, true);
    tm.addToUserSourceDataContainerInt(1, 0, 4, false);
    tm.addToUserSourceDataContainerInt(0, 1, 2, false);
    tm.addToUserDestDataContainerInt(0, 2, 3);
    tm.addToUserDestDataContainerInt(2, 3, 8);

    tm.compute(1);

    tm.printDataFrame();
    return 0;
};

  
