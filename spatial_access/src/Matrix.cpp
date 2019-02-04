#include <iostream>
#include "transitMatrix.h"


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

int main()
{

    lmnoel::transitMatrix matrix(5, false);
    matrix.addEdgeToGraph(0, 1, 5, true);
    matrix.addEdgeToGraph(1, 2, 6, true);
    matrix.addEdgeToGraph(2, 3, 2, true);
    matrix.addEdgeToGraph(2, 4, 4, true);
    matrix.addEdgeToGraph(3, 4, 3, true);

    matrix.addToUserSourceDataContainerString(1, "a", 1, false);
    matrix.addToUserSourceDataContainerString(0, "b", 2, false);
    matrix.addToUserSourceDataContainerString(3, "c", 3, false);
    matrix.addToUserSourceDataContainerString(1, "d", 7, false);

    matrix.addToUserDestDataContainerString(1, "a1", 1);
    matrix.addToUserDestDataContainerString(0, "b1", 2);
    matrix.addToUserDestDataContainerString(3, "c1", 3);
    matrix.addToUserDestDataContainerString(1, "d1", 7);

    std::cout << "finished adding" << std::endl;
    matrix.compute(19);
    std::cout << "finished compute" << std::endl;

     matrix.printDataFrame();

    return 0;
};

  
