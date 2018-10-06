#pragma once

#include <string>
#include <vector>
#include <sstream>
#include <iostream>
#include <fstream>

struct AdjListNode 
{ 
    int dest; 
    int weight; 
    struct AdjListNode* next; 
}; 

// A utility function to create a new adjacency list node 
struct AdjListNode* newAdjListNode(int dest, int weight) 
{ 
    struct AdjListNode* newNode = new AdjListNode; 
    newNode->dest = dest; 
    newNode->weight = weight; 
    newNode->next = NULL; 
    return newNode; 
} 


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
    Graph(int vertices);
    Graph();
    void initializeGraph(int vertices);
    ~Graph();
    void addEdge(int src, int dest, int weight);
    void readCSV(const std::string &infile);
    void print();
};

void Graph::print()
{

}

 
Graph::Graph(int V)
{
    initializeGraph(V);
}

Graph::Graph()
{

}

void Graph::initializeGraph(int V)
{
    this->V = V;
 
    // Create an array of adjacency lists.  Size of array will be V
    this->array = new AdjList[V];
     // Initialize each adjacency list as empty by making head as NULL
    for (int i = 0; i < V; i++)
    {
        this->array[i].head = nullptr;
    }
}

 
/* free a graph struct*/
 Graph::~Graph() {
    for (auto i = 0; i < V; i++)
    {
        auto nodeToDelete = this->array[i].head;
        if (!nodeToDelete)
        {
            break;
        }
        while (nodeToDelete)
        {
            auto nextNodeToDelete = nodeToDelete->next;
            //delete nodeToDelete;
            nodeToDelete = nextNodeToDelete;
        }
    }
}


/* Adds an edge to an undirected graph */
void Graph::addEdge(int src, int dest, int weight)
{
    struct AdjListNode* newNode = newAdjListNode(dest, weight); 
    newNode->next = this->array[src].head; 
    this->array[src].head = newNode; 
}

/* Utility function to read edge list from .csv*/
void Graph::readCSV(const std::string& infile) {
    std::ifstream fileIN;

    int src, dst, edge_weight;

    fileIN.open(infile);
    if (fileIN.fail()) {
        throw std::runtime_error("Could not load input file");
    }

    std::string line;
    
    while (getline(fileIN, line)) {
        std::istringstream stream(line);
        std::string input;
        getline(stream, input,',');
        src = (int) stoi(input);
        getline(stream, input,',');
        dst = (int) stoi(input);
        getline(stream, input,',');
        edge_weight = (int) stoi(input);
        addEdge(src, dst, edge_weight);

    }
}
