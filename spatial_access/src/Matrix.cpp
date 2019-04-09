// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#include <iostream>
#include "transitMatrix.h"
#include "TMXUtils.h"
#include "networkUtility.h"
#include <vector>
#include <unordered_map>

int main()
{
//    transitMatrix<unsigned long int, unsigned long int> matrix(true, true, 3, 3);
//
//    matrix.prepareGraphWithVertices(5);
//
//    matrix.addEdgeToGraph(0, 1, 2, true);
//    matrix.addEdgeToGraph(1, 2, 1, true);
//    matrix.addEdgeToGraph(2, 3, 3, true);
//    matrix.addEdgeToGraph(3, 4, 4, true);
//    matrix.addEdgeToGraph(2, 4, 1, true);
//    matrix.addEdgeToGraph(4, 0, 1, true);
//
//    matrix.addToUserSourceDataContainer(1, 10, 1);
//    matrix.addToUserSourceDataContainer(4, 11, 2);
//    matrix.addToUserSourceDataContainer(3, 12, 3);
//
//    matrix.addToUserDestDataContainer(1, 10, 1);
//    matrix.addToUserDestDataContainer(4, 11, 2);
//    matrix.addToUserDestDataContainer(3, 12, 3);
//
//    matrix.compute(1);
//    matrix.printDataFrame();
//    matrix.writeTMX("tmx_test.tmx");
//
//    TMXUtils util;
//
//    std::cout << "type of tmx:" << util.getTypeOfTMX("tmx_test.tmx") << std::endl;
////    std::cout << "next" << std::endl;
//    transitMatrix<unsigned long int, unsigned long int> matrix2;
//    matrix2.readTMX("tmx_test.tmx");
//    matrix2.printDataFrame();


std::vector<unsigned long int> nodes = {0, 1, 2, 3, 4, 5, 6, 7};

std::vector<std::pair<unsigned long, unsigned long>> edges;
edges.emplace_back(std::make_pair(0, 1));
edges.emplace_back(std::make_pair(1, 2));
edges.emplace_back(std::make_pair(1, 5));
edges.emplace_back(std::make_pair(1, 4));
edges.emplace_back(std::make_pair(2, 3));
edges.emplace_back(std::make_pair(2, 6));
edges.emplace_back(std::make_pair(3, 2));
edges.emplace_back(std::make_pair(3, 7));
edges.emplace_back(std::make_pair(4, 0));
edges.emplace_back(std::make_pair(4, 5));
edges.emplace_back(std::make_pair(5, 6));
edges.emplace_back(std::make_pair(6, 5));
edges.emplace_back(std::make_pair(7, 6));
edges.emplace_back(std::make_pair(7, 3));

    NetworkUtility utility(edges, nodes);
    auto res_nodes = utility.getConnectedNetworkNodes();
    auto res_edges = utility.getConnectedNetworkEdges();
    return 0;
};

  
