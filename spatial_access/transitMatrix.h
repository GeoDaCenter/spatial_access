#pragma once

#include <sstream>
#include <iostream>
#include <fstream>
#include <string>
#include <mutex>
#include <thread>
#include <stdexcept>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <utility>

#include "utils/threadUtilities.h"
#include "utils/dataFrame.h"
#include "utils/Graph.h"
#include "utils/MinHeap.h"
#include "utils/userDataContainer.h"

#define UNDEFINED (-1)

/* struct to represent a single source associated with */
/* a single network node */

/* write the header line for the output file */

/* class to manage worker thread data */
class workerArgs {
public:
    Graph graph;
    jobQueue jq;
    userDataContainer userSourceData;
    userDataContainer userDestData;
    dataFrame df;
    std::string outfile;
    float impedence;
    int numNodes;
    int writeMode;
    std::mutex write_lock;
    std::mutex insert_data;
    workerArgs(Graph &graph, userDataContainer &userSourceData,
                       userDataContainer &userDestData, float impedence, 
                       int numNodes, dataFrame &df, const std::string &outfile, bool writeMode);
    ~workerArgs(void);

};



/* wa initializer */
workerArgs::workerArgs(Graph &graph, userDataContainer &userSourceData,
                       userDataContainer &userDestData, float impedence, 
                       int numNodes, dataFrame &df, const std::string &outfile, bool writeMode) {

    //init values
    this->graph = graph;
    this->userSourceData = userSourceData;
    this->userDestData = userDestData;
    this->impedence = impedence;
    this->numNodes = numNodes;
    this->df = df;
    this->writeMode = writeMode;
    this->outfile = outfile;


    //initialize job queue
    auto sourceTractIds = userSourceData.retrieveUniqueNetworkNodeIds();
    for (int i : sourceTractIds) {
        jq.insert(i);
    }

 }


/* wa destructor */
workerArgs::~workerArgs(void) {

}


/*write_row: write a row to file*/
void writeRow(const std::vector<int> &dist, workerArgs *wa, int src) {
    std::ofstream Ofile;
    // std::cout << "src tract id : " << src << std::endl;
    if (wa->writeMode) {
        Ofile.open(wa->outfile, std::ios_base::app);
        wa->write_lock.lock();
    }
    int src_imp, dst_imp, calc_imp, fin_imp;
    //  iterate through each data point of the current source tract
    auto sourceTract = wa->userSourceData.retrieveTract(src);
    // std::cout << "size of source" <<  sourceTract.retrieveDataPoints().size() << std::endl;
    for (auto sourceDataPoint : sourceTract.retrieveDataPoints())
    {
        // std::cout << "sourceDataPoint: " <<  sourceDataPoint.id << std::endl;
        src_imp = sourceDataPoint.lastMileDistance / wa->impedence;

        auto destNodeIds = wa->userDestData.retrieveAllNetworkNodeIds();
        // iterate through each dest tract

        std::unordered_map<std::string, int> row_data;
        for (auto destNodeId : destNodeIds)
        {
           //  std::cout << "destNodeId: " << destNodeId << std::endl;
            std::vector<userDataPoint> destPoints = wa->userDestData.retrieveTract(destNodeId).retrieveDataPoints();
          //   std::cout << "number of associated points in tract " << destPoints.size() << std::endl;
            for (auto destDataPoint : destPoints)
            {
               calc_imp = dist.at(destNodeId);
               //  std::cout << "destDataPoint.id: " << destDataPoint.id << std::endl;
                if (destDataPoint.id == sourceDataPoint.id)
                {
                  //  std::cout << "matching indexes" << std::endl;
                    fin_imp = 0;
                }
                else 
                {
                    dst_imp = destDataPoint.lastMileDistance / wa->impedence;
                  //  std::cout << "before calc imp" << std::endl;
                   //  std::cout << "dist.size(): " << dist.size() << std::endl;  
                    // std::cout << "calc_imp: " << calc_imp << std::endl;
                    if (calc_imp == INT_MAX)
                    {
                        fin_imp = UNDEFINED;
                    }
                    else
                    {
                        fin_imp = dst_imp + src_imp + calc_imp;    
                    }

                    //std::cout << "fin_imp: " << fin_imp << std::endl;
                }
                std::cout << "(" << sourceDataPoint.id << "," << destDataPoint.id << ") :" << fin_imp << std::endl;
                //std::cout << "src_imp: "  << src_imp << std::endl;
                //std::cout << "dst_imp: "  << dst_imp << std::endl;
                // std::cout << "calc_imp: "  << calc_imp << std::endl;


                // row_data.at(destDataPoint.id) = fin_imp;

            }
        }
        wa->insert_data.lock();
        wa->df.insertRow(row_data, sourceDataPoint.id);
        wa->insert_data.unlock();
        
    }
    if (wa->writeMode) {
        Ofile.close();
        wa->write_lock.unlock();
    }
}

void printDistArray( std::vector<int> dist)
{
    std::cout << "printing dist" << std::endl;
    for (auto element : dist) 
    {
        std::cout << element << std::endl;
    }
}


/* The main function that calulates distances of shortest paths from src to all*/
/* vertices. It is a O(ELogV) function*/
void dijkstra(int src, workerArgs *wa) {
    std::cout << "started dijkstra for source: " << src << std::endl;

    int V = wa->graph.V;// Get the number of vertices in graph
    
    std::vector<int> dist(V, INT_MAX);

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
            if (minHeap.isInMinHeap(v) && dist[u] != INT_MAX && 
                                          pCrawl->weight + dist[u] < dist[v])
            {
                dist[v] = dist[u] + pCrawl->weight;
 
                // update distance value in min heap also
                minHeap.decreaseKey(v, dist[v]);
            }
            pCrawl = pCrawl->next;
        }
    }
    // printDistArray(dist);
    //write row to file or find best
    writeRow(dist, wa, src);
    
}

void workerHandler(workerArgs* wa) {
    int src;
    std::cout << "entered workerHandler" << std::endl;
    while (!wa->jq.empty()) {
        src = wa->jq.pop();
        std::cout << "added src " << src << " to queue" << std::endl;
        //exit loop if job queue was empty
        if (src < 0) {
            break;
        }
        dijkstra(src, wa);
    }
}

class transitMatrix {
public:
    dataFrame df;
    userDataContainer userSourceDataContainer;
    userDataContainer userDestDataContainer;
    Graph graph;
    int numNodes;
    void addToUserSourceDataContainer(int networkNodeId, std::string id, int lastMileDistance);
    void addToUserDestDataContainer(int networkNodeId, std::string id, int lastMileDistance);
    void addEdgeToGraph(int src, int dest, int weight, bool isBidirectional);
    transitMatrix(int V);
    transitMatrix(std::string infile);
    void compute(float impedence, int numThreads);
    void compute(float impedence, int numThreads, const std::string &outfile);
    transitMatrix(void);
    int get(const std::string &source, const std::string &dest);
    void loadFromDisk(void);
    void prepareDataFrame();
    void writeHeader(const std::string &outfile);
};


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

void transitMatrix::compute(float impedence, int numThreads, const std::string &outfile)
{
    prepareDataFrame();

    writeHeader(outfile);

    workerArgs wa(graph, userSourceDataContainer, userDestDataContainer, impedence, 
        numNodes, df, outfile, true);   

    workerQueue wq(numThreads);

    wq.start(workerHandler, &wa);
}

void transitMatrix::compute(float impedence, int numThreads)
{
    prepareDataFrame();
    workerArgs wa(graph, userSourceDataContainer, userDestDataContainer, impedence, 
        numNodes, df, "blah", false);   

    workerQueue wq(numThreads);

    wq.start(workerHandler, &wa);
}

void transitMatrix::writeHeader(const std::string &outfile) {
    std::ofstream Ofile;
    auto userDestIds = userDestDataContainer.retrieveAllUserDataIds();

    Ofile.open(outfile);
    if (Ofile.fail()) {
        throw std::runtime_error("Could not open output file");
    }
    auto numUserDestIds = userDestIds.size();
    Ofile << ",";
    for (auto i = 0; i < numUserDestIds; i++) {
        Ofile << userDestIds.at(i);
        if (i < numUserDestIds - 1) {
            Ofile << ",";
        }
    }
    Ofile << std::endl;
    Ofile.close();

}
void transitMatrix::addToUserDestDataContainer(int networkNodeId, std::string id, int lastMileDistance)
{
    userDestDataContainer.addPoint(networkNodeId, id, lastMileDistance);
}

void transitMatrix::addToUserSourceDataContainer(int networkNodeId, std::string id, int lastMileDistance)
{
    userSourceDataContainer.addPoint(networkNodeId, id, lastMileDistance);
}

void transitMatrix::addEdgeToGraph(int src, int dest, int weight, bool isBidirectional)
{
    graph.addEdge(src, dest, weight);
    if (isBidirectional)
    {
        graph.addEdge(dest, src, weight);
    }
}


transitMatrix::transitMatrix(std::string infile) 
{
    if (!df.loadFromDisk(infile)) 
    {
        throw std::runtime_error("failed to load dataFrame from file");
    }

}

// change ids to ints to speed up a lot
int transitMatrix::get(const std::string &source, const std::string &dest) {
    return df.retrieveSafe(source, dest);
}
