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

    lmnoel::transitMatrix matrix(5, true);
    matrix.addEdgeToGraph(0, 1, 5, true);
    matrix.addEdgeToGraph(1, 2, 6, true);
    matrix.addEdgeToGraph(2, 3, 2, true);
    matrix.addEdgeToGraph(2, 4, 4, true);
    matrix.addEdgeToGraph(3, 4, 3, true);

    matrix.addToUserSourceDataContainer(1, 1, 1, true);
    matrix.addToUserSourceDataContainer(0, 2, 2, true);
    matrix.addToUserSourceDataContainer(3, 3, 3, true);
    matrix.addToUserSourceDataContainer(1, 4, 7, true);
    // // matrix.addToUserDestDataContainer(1, 11, 1);
    // // matrix.addToUserDestDataContainer(0, 12, 2);
    // // matrix.addToUserDestDataContainer(3, 13, 3);
    // // matrix.addToUserDestDataContainer(1, 14, 7);

    matrix.compute(1);

    auto destsInRange = matrix.getDestsInRange(13, 10);
    printMapOfArrays(destsInRange);
    auto sourcesInRange = matrix.getSourcesInRange(13, 10);
    printMapOfArrays(sourcesInRange);
    // std::cout << "df1:" << std::endl;
    // matrix.printDataFrame();

    // lmnoel::transitMatrix matrix2("outfile.csv");
    // std::cout << "df2:" << std::endl;
    // matrix2.printDataFrame();

    return 0;
};

  
