#pragma once

#include <string>
#include <vector>
#include <sstream>
#include <iostream>
#include <cstring>
#include <fstream>

/* Node of an adjacency list */
struct AdjListNode 
{ 
    int dest; 
    unsigned short int weight; 
    struct AdjListNode* next; 
}; 

/* A utility function to create a new adjacency list node */
struct AdjListNode* newAdjListNode(int dest, unsigned short int weight) 
{ 
    struct AdjListNode* newNode = new AdjListNode; 
    newNode->dest = dest; 
    newNode->weight = weight; 
    newNode->next = NULL; 
    return newNode; 
} 

/* Adjacency list wrapper class */
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
    void print();
    Graph(Graph const & other);
    Graph & operator=(Graph const & other);
};


/* Constructor for when the number of vertices is known at instantiation */ 
Graph::Graph(int V)
{
    initializeGraph(V);
}

/* Constructor for when the number of vertices is not known at instantiation */ 
Graph::Graph()
{

}


/* Copy constructor */
Graph::Graph(Graph const & other)
{
    this->V = other.V;
    this->array = new AdjList[this->V];
    std::memcpy(this->array, other.array, this->V * sizeof(AdjList));
}


/* Assignment operator */
Graph & Graph::operator=(Graph const & other)
{
    V = other.V;
    *array = *other.array;

    return *this;
}

/* Initialize graph when number of vertices isn't known at instantiation */
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

 
/* Destructor h*/
 Graph::~Graph() {
    for (auto nodePointer : nodePointers)
    {
        delete nodePointer;
    }
}


/* Adds an edge to an undirected graph */
void Graph::addEdge(int src, int dest, unsigned short int weight)
{
    struct AdjListNode* newNode = newAdjListNode(dest, weight); 
    this->nodePointers.push_back(newNode);
    newNode->next = this->array[src].head; 
    this->array[src].head = newNode; 
}


/* Utility function to read edge list from .csv*/
void Graph::readCSV(const std::string& infile) {
    std::ifstream fileIN;

    int src, dst;
    unsigned short int edge_weight;

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
        edge_weight = (unsigned short int) stoi(input);
        addEdge(src, dst, edge_weight);

    }
}
