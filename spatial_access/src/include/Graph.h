// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#pragma once

#include <vector>
#include <tuple>
#include <stdexcept>

typedef unsigned long int network_loc;

template <class value_type>
class Graph
{
public:
    Graph()= default;
    unsigned long int vertices;
    std::vector<std::vector<std::pair<network_loc, value_type>>> neighbors;
    void initializeGraph(unsigned long int vertices)
    {
        std::vector<std::pair<network_loc , value_type>> value;
        this->neighbors.assign(vertices, value);
        this->vertices = vertices;
    }

/* Adds an edge to an undirected graph */
    void addEdge(network_loc src, network_loc dest, value_type weight)
    {
        try
        {
            this->neighbors.at(src).push_back(std::make_pair(dest, weight));
        }
        catch (...)
        {
            throw std::runtime_error("edge incompatible with declared graph structure");
        }
    }

};