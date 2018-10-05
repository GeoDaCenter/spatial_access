#pragma once

#include <string>
#include <vector>
#include <sstream>
#include <iostream>
#include <fstream>

class AdjListNode
{
public:
    int dest;
    int weight;
    AdjListNode *next;
    AdjListNode(int dest, int weight);
    AdjListNode() {}
    ~AdjListNode();
};

AdjListNode::AdjListNode(int dest, int weight)
{
    this->dest = dest;
    this->weight = weight;
    this->next = nullptr;
}

AdjListNode::~AdjListNode()
{

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
    Graph(int v);
    Graph();
    void initializeGraph(int v);
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
    delete [] this->array;
}


/* Adds an edge to an undirected graph */
void Graph::addEdge(int src, int dest, int weight)
{
    // Add an edge from src to dest.  A new node is added to the adjacency
    // list of src.  The node is added at the begining
    AdjListNode newNode(dest, weight);
    newNode.next = this->array[src].head;
    this->array[src].head = &newNode;
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
