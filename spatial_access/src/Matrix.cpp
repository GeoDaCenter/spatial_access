// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#include <iostream>
#include "transitMatrix.cpp"
#include <vector>
#include <unordered_map>


using namespace lmnoel;
int main()
{
    transitMatrix<unsigned int, unsigned int> matrix(true, 3, 3);

    matrix.prepareGraphWithVertices(5);

    matrix.addEdgeToGraph(0, 1, 2, true);
    matrix.addEdgeToGraph(1, 2, 1, true);
    matrix.addEdgeToGraph(2, 3, 3, true);
    matrix.addEdgeToGraph(3, 4, 4, true);
    matrix.addEdgeToGraph(2, 4, 1, true);
    matrix.addEdgeToGraph(4, 0, 1, true);

    matrix.addToUserSourceDataContainer(1, 10, 1);
    matrix.addToUserSourceDataContainer(4, 11, 2);
    matrix.addToUserSourceDataContainer(3, 12, 3);

    matrix.addToUserDestDataContainer(1, 10, 1);
    matrix.addToUserDestDataContainer(4, 11, 2);
    matrix.addToUserDestDataContainer(3, 12, 3);

    matrix.compute(10);
    matrix.printDataFrame();

    return 0;
};

  
