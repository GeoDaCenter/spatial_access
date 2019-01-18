#include <iostream>
#include "transitMatrix.h"


int main()
{

    // lmnoel::transitMatrix matrix(5, true);
    // matrix.addEdgeToGraph(0, 1, 5, true);
    // matrix.addEdgeToGraph(1, 2, 6, true);
    // matrix.addEdgeToGraph(2, 3, 2, true);
    // matrix.addEdgeToGraph(2, 4, 4, false);
    // matrix.addEdgeToGraph(3, 4, 3, true);

    // matrix.addToUserSourceDataContainer(1, 10, 1, true);
    // matrix.addToUserSourceDataContainer(0, 11, 2, true);
    // matrix.addToUserSourceDataContainer(4, 12, 3, true);
    // matrix.addToUserSourceDataContainer(1, 13, 7, true);

    // matrix.compute(1);
    // matrix.writeCSV("outfile.csv");
    // matrix.writeTMX("outfile1"); 
    lmnoel::transitMatrix matrix("transit.csv", true, true);
    std::cout << "df1:" << std::endl;
    matrix.printDataFrame();

    // lmnoel::transitMatrix matrix2("outfile.csv");
    // std::cout << "df2:" << std::endl;
    // matrix2.printDataFrame();

    return 0;
}

  
