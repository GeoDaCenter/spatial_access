// This is a test file used for development of the package
// it should be removed prior to distribution

#include <iostream>
#include "transitMatrix.h"
#include "TMXUtils.h"
#include <vector>
#include <unordered_map>

int main()
{
    lmnoel::transitMatrix<unsigned long int, unsigned long int> matrix;
    matrix.readOTPCSV("sample_otp.csv");
    matrix.printDataFrame();

//    CSV incsv("sample_otp.csv");
//    lmnoel::transitMatrix<std::string, std::string> matrix(false, false, 3, 2);
//
//    matrix.prepareGraphWithVertices(5);
//
//    matrix.addSingleEdgeToGraph(0, 1, 2, true);
//    matrix.addSingleEdgeToGraph(1, 2, 1, true);
//    matrix.addSingleEdgeToGraph(2, 3, 3, true);
//    matrix.addSingleEdgeToGraph(3, 4, 4, true);
//    matrix.addSingleEdgeToGraph(2, 4, 1, true);
//    matrix.addSingleEdgeToGraph(4, 0, 1, true);
//
//    matrix.addToUserSourceDataContainer(1, "a", 1);
//    matrix.addToUserSourceDataContainer(4, "b", 2);
//    matrix.addToUserSourceDataContainer(3, "c", 3);
//
//    matrix.addToUserDestDataContainer(1, "e", 1);
//    matrix.addToUserDestDataContainer(4, "f", 2);
//
//
//    matrix.compute(1);
//    matrix.printDataFrame();
//    matrix.writeTMX("tmx_test1.tmx");
//
//    lmnoel::transitMatrix<std::string, std::string> matrix2;
//    matrix2.readTMX("tmx_test1.tmx");
//    matrix2.printDataFrame();


    return 0;
};

  
