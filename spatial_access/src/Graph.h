#pragma once

struct AdjListNode 
{ 
    int dest; 
    unsigned short int weight; 
    struct AdjListNode* next; 
}; 

// A utility function to create a new adjacency list node 
struct AdjListNode* newAdjListNode(int dest, unsigned short int weight);


class AdjList
{
public:
    AdjListNode *head;
};

/* A structure to represent a graph. A graph is an array of adjacency lists.*/
/* Size of array will be V (number of vertices in graph)*/
class Graph
{
public:
    int V;
    AdjList *array;
    std::vector<struct AdjListNode*> nodePointers;
    Graph(int vertices);
    Graph();
    void initializeGraph(int vertices);
    ~Graph();
    void addEdge(int src, int dest, unsigned short int weight);
    void readCSV(const std::string &infile);
    Graph(Graph const & other);
    Graph & operator=(Graph const & other);
};