#pragma once

class Graph
{
private:
    unsigned int vertices;
public:
    Graph()= default;
    void initializeGraph(unsigned int vertices);
    std::vector<std::vector<std::pair<unsigned int, unsigned short int>>> neighbors;
    unsigned int getV() const;
    void addEdge(unsigned int src, unsigned int dest, unsigned short int weight);
};