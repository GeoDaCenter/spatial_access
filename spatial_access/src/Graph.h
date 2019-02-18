// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#pragma once

class Graph
{
private:
    unsigned long int vertices;
public:
    Graph()= default;
    void initializeGraph(unsigned long int vertices);
    std::vector<std::vector<std::pair<unsigned long int, unsigned short int>>> neighbors;
    unsigned long int getV() const;
    void addEdge(unsigned long int src, unsigned long int dest, unsigned short int weight);
};