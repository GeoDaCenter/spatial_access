#include <vector>
#include <tuple>

#include "Graph.h"

void Graph::initializeGraph(unsigned int vertices)
{
    std::vector<std::pair<unsigned int, unsigned short int>> value;
    this->neighbors.assign(vertices, value);
    this->vertices = vertices;
}

unsigned int Graph::getV() const
{
    return this->vertices;
}


/* Adds an edge to an undirected graph */
void Graph::addEdge(unsigned int src, unsigned int dest, unsigned short int weight)
{

    this->neighbors.at(src).push_back(std::make_pair(dest, weight));
}
