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
//    lmnoel::transitMatrix<unsigned long int, unsigned long int> matrix(false, false, 3, 2);
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
//
//
//    matrix.compute(1);
//    matrix.printDataFrame();

//    transitMatrix<unsigned long int, unsigned long int> matrix2;
//    matrix2.readTMX("tmx_test.tmx");
//    matrix2.printDataFrame();


std::vector<std::string> nodes = {"a", "b", "c", "d", "e", "f", "g", "h"};

std::vector<std::pair<std::string, std::string>> edges;
edges.emplace_back(std::make_pair("a", "b"));
edges.emplace_back(std::make_pair("b", "c"));
edges.emplace_back(std::make_pair("b", "f"));
edges.emplace_back(std::make_pair("b", "e"));
edges.emplace_back(std::make_pair("c", "d"));
edges.emplace_back(std::make_pair("c", "g"));
edges.emplace_back(std::make_pair("d", "c"));
edges.emplace_back(std::make_pair("d", "h"));
edges.emplace_back(std::make_pair("e", "a"));
edges.emplace_back(std::make_pair("e", "f"));
edges.emplace_back(std::make_pair("f", "g"));
edges.emplace_back(std::make_pair("g", "f"));
edges.emplace_back(std::make_pair("h", "g"));
edges.emplace_back(std::make_pair("h", "d"));
//edges.emplace_back(std::make_pair(7, 3));

    NetworkUtility<std::string> utility(edges, nodes);
    auto res_nodes = utility.getConnectedNetworkNodes();

    return 0;
};

  
