// This is a test file used for development of the package
// it should be removed prior to distribution

#include <iostream>
#include "transitMatrix.h"
#include "TMXUtils.h"
#include "networkUtility.h"
#include <vector>
#include <unordered_map>

int main()
{
    lmnoel::transitMatrix<unsigned long int, unsigned long int> matrix(false, false, 3, 2);

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


    matrix.compute(1);
    matrix.printDataFrame();

//    transitMatrix<unsigned long int, unsigned long int> matrix2;
//    matrix2.readTMX("tmx_test.tmx");
//    matrix2.printDataFrame();


//std::vector<unsigned long int> nodes = {0, 1, 2, 3, 4, 5, 6, 7};
//
//std::vector<std::pair<unsigned long, unsigned long>> edges;
//edges.emplace_back(std::make_pair(0, 1));
//edges.emplace_back(std::make_pair(1, 2));
//edges.emplace_back(std::make_pair(1, 5));
//edges.emplace_back(std::make_pair(1, 4));
//edges.emplace_back(std::make_pair(2, 3));
//edges.emplace_back(std::make_pair(2, 6));
//edges.emplace_back(std::make_pair(3, 2));
//edges.emplace_back(std::make_pair(3, 7));
//edges.emplace_back(std::make_pair(4, 0));
//edges.emplace_back(std::make_pair(4, 5));
//edges.emplace_back(std::make_pair(5, 6));
//edges.emplace_back(std::make_pair(6, 5));
//edges.emplace_back(std::make_pair(7, 6));
//edges.emplace_back(std::make_pair(7, 3));
//
//    NetworkUtility utility(edges, nodes);
//    auto res_nodes = utility.getConnectedNetworkNodes();
//    auto res_edges = utility.getConnectedNetworkEdges();
    return 0;
};

  
