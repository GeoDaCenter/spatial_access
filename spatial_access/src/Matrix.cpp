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
    transitMatrix<unsigned long, unsigned long, unsigned int> matrix2;
    matrix2.readCSV("ct_health.csv");
//    matrix2.printDataFrame();
    matrix2.getValuesBySource(17031841100, true);

    return 0;
};

  
