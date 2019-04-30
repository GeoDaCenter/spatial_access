// This is a test file used for development of the package
// it should be removed prior to distribution

#include <iostream>
#include "transitMatrix.h"
#include <vector>
#include <unordered_map>
#include <cstdlib>
#include <chrono>

int main()
{
//
    transitMatrix<unsigned long, unsigned long, unsigned int> matrix(false, true, 3, 3);

    matrix.prepareGraphWithVertices(5);

    std::vector<unsigned long> a = {0, 1, 2, 3, 2, 4};
    std::vector<unsigned long> b = {1, 2, 3, 4, 4, 0};
    std::vector<unsigned int> c = {100000, 1, 100000, 100000, 4, 5};
    std::vector<bool> d = {true, true, true, true, true, true};

    matrix.addEdgesToGraph(a, b, c, d);

    matrix.addToUserSourceDataContainer(1, 10, 1);
    matrix.addToUserSourceDataContainer(4, 11, 2);
    matrix.addToUserSourceDataContainer(3, 12, 3);

    matrix.addToUserDestDataContainer(1, 10, 1);
    matrix.addToUserDestDataContainer(4, 11, 2);
    matrix.addToUserDestDataContainer(3, 12, 3);

    matrix.compute(10);
    matrix.printDataFrame();
    matrix.writeCSV("temp.csv");

    transitMatrix<unsigned long, unsigned long, unsigned int> matrix2;
    matrix2.readCSV("temp.csv");
    matrix2.printDataFrame();

    return 0;
};

  
