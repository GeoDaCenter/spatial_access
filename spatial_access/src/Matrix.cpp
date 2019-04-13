// This is a test file used for development of the package
// it should be removed prior to distribution

#include <iostream>
#include "transitMatrix.h"
#include "TMXUtils.h"
#include <vector>
#include <unordered_map>
#include <cstdlib>
#include <chrono>

int main()
{
    auto num_vertices = 10000;
    auto max_edges_per_vertex = 4;
    auto max_edge_weight = 50;
    auto num_sources = 5000;
    auto num_dests = 2000;

    transitMatrix<unsigned long int, unsigned long int> matrix(false, false, num_sources, num_dests);
    matrix.prepareGraphWithVertices(num_vertices);
    srand(0);
    for (auto i = 0; i < num_vertices; i++)
    {
        auto num_edges = std::rand() % max_edges_per_vertex;
        for (auto t = 0; t < num_edges; t++)
        {
            unsigned long int adjoining_vertex = std::rand() % num_vertices;
            unsigned short int weight = std::rand() % max_edge_weight;
            matrix.addSingleEdgeToGraph(i, adjoining_vertex, weight, true);
        }
    }


    auto max_last_mile_impedence = 10;

    for (auto i = 0; i < num_sources; i++)
    {
        unsigned long int associated_network_node = std::rand() % num_vertices;
        unsigned short int last_mile_weight = std::rand() % max_last_mile_impedence;
        matrix.addToUserSourceDataContainer(associated_network_node, i, last_mile_weight);
    }

    for (auto i = 0; i < num_dests; i++)
    {
        unsigned long int associated_network_node = std::rand() % num_vertices;
        unsigned short int last_mile_weight = std::rand() % max_last_mile_impedence;
        matrix.addToUserDestDataContainer(associated_network_node, i, last_mile_weight);
    }
    auto start = std::chrono::high_resolution_clock::now();


    matrix.compute(5);
    auto finish = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed_secs = finish - start;
    std::cout << "elapsed_time" << elapsed_secs.count() << std::endl;
//    matrix.printDataFrame();



    return 0;
};

  
