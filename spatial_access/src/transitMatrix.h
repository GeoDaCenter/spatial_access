#pragma once

#include <sstream>
#include <iostream>
#include <fstream>
#include <string>
#include <stdexcept>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <utility>
#include <mutex>

#include "utils/threadUtilities.h"
#include "utils/dataFrame.h"
#include "utils/Graph.h"
#include "utils/MinHeap.h"
#include "utils/userDataContainer.h"


/* struct to represent a single source associated with */
/* a single network node */

/* write the header line for the output file */

/* class to manage worker thread data */


class workerArgs {
public:
    Graph &graph;
    dataFrame &df;
    jobQueue jq;
    userDataContainer userSourceData;
    userDataContainer userDestData;
    int numNodes;
    std:: mutex writeLock;
    workerArgs(Graph &graph, userDataContainer &userSourceData,
                       userDataContainer &userDestData, 
                       int numNodes, dataFrame &df) 
    : graph(graph), df(df), userSourceData(userSourceData), userDestData(userDestData),
     numNodes(numNodes) {}
    ~workerArgs(void);
    void initialize();

};

void workerArgs::initialize()
{
    //initialize job queue
    for (auto i : userSourceData.retrieveUniqueNetworkNodeIds()) {
        jq.insert(i);
    }
}

/* wa destructor */
workerArgs::~workerArgs(void) {

}


/*write_row: write a row to file*/
void calculateRow(const std::vector<int> &dist, workerArgs *wa, int src) {

    unsigned short int src_imp, dst_imp, calc_imp, fin_imp;
    //  iterate through each data point of the current source tract
    auto sourceTract = wa->userSourceData.retrieveTract(src);

    for (auto sourceDataPoint : sourceTract.retrieveDataPoints())
    {
        src_imp = sourceDataPoint.lastMileDistance;

        auto destNodeIds = wa->userDestData.retrieveUniqueNetworkNodeIds();
        // iterate through each dest tract

        std::unordered_map<unsigned long int, unsigned short int> row_data;
        for (auto destNodeId : destNodeIds)
        {
            auto destTract = wa->userDestData.retrieveTract(destNodeId);
            auto destPoints = destTract.retrieveDataPoints();
            for (auto destDataPoint : destPoints)
            {
                calc_imp = dist.at(destNodeId);
                if (destDataPoint.id == sourceDataPoint.id)
                {
                    fin_imp = 0;
                }
                else 
                {
                    dst_imp = destDataPoint.lastMileDistance;
                    if (calc_imp == USHRT_MAX)
                    {
                        fin_imp = USHRT_MAX;
                    }
                    else
                    {
                        fin_imp = dst_imp + src_imp + calc_imp;    
                    }

                }
                row_data.insert(std::make_pair(destDataPoint.id, fin_imp));

            }

        }
        wa->writeLock.lock();
        wa->df.insertRow(row_data, sourceDataPoint.id);
        wa->writeLock.unlock();
    }
}


/* The main function that calulates distances of shortest paths from src to all*/
/* vertices. It is a O(ELogV) function*/
void dijkstra(int src, workerArgs *wa) {

    int V = wa->graph.V;// Get the number of vertices in graph
    
    std::vector<int> dist(V, USHRT_MAX);

    // minHeap represents set E
    MinHeap minHeap(V);
 
    // Initialize min heap with all vertices. dist value of all vertices 
    for (int v = 0; v < V; ++v)
    {
        minHeap.array[v] = MinHeapNode(v, dist[v]);
        minHeap.pos[v] = v;
    }
 
    // Make dist value of src vertex as 0 so that it is extracted first
    minHeap.array[src] = MinHeapNode(src, dist[src]);
    minHeap.pos[src] = src;
    dist[src] = 0;
    minHeap.decreaseKey(src, dist[src]);
 
    // Initially size of min heap is equal to V
    minHeap.size = V;
 
    // In the followin loop, min heap contains all nodes
    // whose shortest distance is not yet finalized.
    while (!minHeap.isEmpty())
    {
        // Extract the vertex with minimum distance value
        auto minHeapNode = minHeap.extractMin();
        int u = minHeapNode.v; // Store the extracted vertex number
 
        // Traverse through all adjacent vertices of u (the extracted
        // vertex) and update their distance values
        AdjListNode* pCrawl = wa->graph.array[u].head;
        while (pCrawl != NULL)
        {
            int v = pCrawl->dest;
 
            // If shortest distance to v is not finalized yet, and distance to v
            // through u is less than its previously calculated distance
            if (minHeap.isInMinHeap(v) && dist[u] != USHRT_MAX && 
                                          pCrawl->weight + dist[u] < dist[v])
            {
                dist[v] = dist[u] + pCrawl->weight;
 
                // update distance value in min heap also
                minHeap.decreaseKey(v, dist[v]);
            }
            pCrawl = pCrawl->next;
        }
    }

    //calculate row and add to dataFrame
    calculateRow(dist, wa, src);
    
}

void workerHandler(workerArgs* wa) {
    int src;
    while (!wa->jq.empty()) {
        src = wa->jq.pop();

        //exit loop if job queue was empty
        if (src < 0) {
            break;
        }
        dijkstra(src, wa);
    }
}


namespace lmnoel {

class transitMatrix {
public:
    dataFrame df;
    userDataContainer userSourceDataContainer;
    userDataContainer userDestDataContainer;
    Graph graph;
    int numNodes;
    void addToUserSourceDataContainer(int networkNodeId, unsigned long int id, int lastMileDistance, bool isBidirectional);
    void addToUserDestDataContainer(int networkNodeId, unsigned long int id, int lastMileDistance);
    void addEdgeToGraph(int src, int dest, int weight, bool isBidirectional);
    transitMatrix(int V);
    transitMatrix(const std::string &infile);
    void compute(int numThreads);
    transitMatrix(void);
    int get(unsigned long int source, unsigned long intdest);
    void loadFromDisk(void);
    void prepareDataFrame();
    bool writeCSV(const std::string &outfile);
    void printDataFrame();
};

bool transitMatrix::writeCSV(const std::string &outfile)
{
    return this->df.writeCSV(outfile);
}

transitMatrix::transitMatrix(int V)
{
    this->numNodes = V;
    graph.initializeGraph(V);
}

void transitMatrix::prepareDataFrame()
{
    auto userSourceIds = userSourceDataContainer.retrieveAllUserDataIds();
    auto userDestIds = userDestDataContainer.retrieveAllUserDataIds();
    df.reserve(userSourceIds, userDestIds);
}

void transitMatrix::compute(int numThreads)
{
    prepareDataFrame();

    workerArgs wa(graph, userSourceDataContainer, userDestDataContainer, 
        numNodes, df);

    wa.initialize();  

    workerQueue wq(numThreads);

    wq.start(workerHandler, &wa);
}

void transitMatrix::addToUserDestDataContainer(int networkNodeId, unsigned long int id, int lastMileDistance)
{
    userDestDataContainer.addPoint(networkNodeId, id, lastMileDistance);
}

void transitMatrix::addToUserSourceDataContainer(int networkNodeId, unsigned long int id, int lastMileDistance, bool isBidirectional)
{
    userSourceDataContainer.addPoint(networkNodeId, id, lastMileDistance);
    if (isBidirectional)
    {
        userDestDataContainer.addPoint(networkNodeId, id, lastMileDistance);   
    }
}

void transitMatrix::addEdgeToGraph(int src, int dest, int weight, bool isBidirectional)
{
    graph.addEdge(src, dest, weight);
    if (isBidirectional)
    {
        graph.addEdge(dest, src, weight);
    }
}


transitMatrix::transitMatrix(const std::string &infile) 
{
    if (!df.loadFromDisk(infile)) 
    {
        throw std::runtime_error("failed to load dataFrame from file");
    }

}

void transitMatrix::printDataFrame(){
    this->df.printDataFrame();
}

// change ids to ints to speed up a lot
int transitMatrix::get(unsigned long int source, unsigned long int dest) {
    return df.retrieveSafe(source, dest);
}

} // namespace lnoel
