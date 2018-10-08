#include <iostream>
#include "transitMatrix.h"


int main()
{
    lmnoel::transitMatrix matrix("outfile.csv");
    // lmnoel::transitMatrix matrix(5);
    // matrix.addEdgeToGraph(0, 1, 5, true);
    // matrix.addEdgeToGraph(1, 2, 6, true);
    // matrix.addEdgeToGraph(2, 3, 2, true);
    // matrix.addEdgeToGraph(2, 4, 4, false);
    // matrix.addEdgeToGraph(3, 4, 3, true);

    // matrix.addToUserSourceDataContainer(1, "A", 1, true);
    // matrix.addToUserSourceDataContainer(0, "B", 2, true);
    // matrix.addToUserSourceDataContainer(4, "C", 3, true);
    // matrix.addToUserSourceDataContainer(1, "D", 7, true);

    // std::cout << "dest data" << std::endl;
    // matrix.userDestDataContainer.print();

    // matrix.compute(1, 3);
    // matrix.writeCSV("outfile.csv");
    matrix.printDataFrame();



    return 0;
}

  