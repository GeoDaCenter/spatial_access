#include <iostream>
#include "transitMatrix.h"


int main()
{

    lmnoel::transitMatrix matrix(5, true);
    matrix.addEdgeToGraph(0, 1, 5, true);
    matrix.addEdgeToGraph(1, 2, 6, true);
    matrix.addEdgeToGraph(2, 3, 2, true);
    matrix.addEdgeToGraph(2, 4, 4, false);
    matrix.addEdgeToGraph(3, 4, 3, true);

    matrix.addToUserSourceDataContainer(1, 10, 1, true);
    matrix.addToUserSourceDataContainer(0, 11, 2, true);
    matrix.addToUserSourceDataContainer(4, 12, 3, true);
    matrix.addToUserSourceDataContainer(1, 13, 7, true);

    matrix.userDestDataContainer.print();

    matrix.compute(1);
    matrix.writeCSV("outfile.csv");
    matrix.printDataFrame();



    return 0;
}

  
