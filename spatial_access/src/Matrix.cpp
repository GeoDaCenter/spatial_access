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

    // matrix.addToUserSourceDataContainer(1, 0, 1, true);
    // matrix.addToUserSourceDataContainer(0, 1, 2, true);
    // matrix.addToUserSourceDataContainer(4, 2, 3, true);
    // matrix.addToUserSourceDataContainer(1, 3, 7, true);

    // matrix.userDestDataContainer.print();

    // matrix.compute(1);
    // matrix.writeCSV("outfile.csv");
    matrix.printDataFrame();



    return 0;
}

  
