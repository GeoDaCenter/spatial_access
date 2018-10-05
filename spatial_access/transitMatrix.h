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
    auto sourceTractIds = userSourceData.retrieveAllNetworkNodeIds();
    for (auto i : sourceTractIds) {
        jq.insert(i);
    }

 }


/* wa destructor */
workerArgs::~workerArgs(void) {

}


/*write_row: write a row to file*/
void writeRow(const std::vector<int> &dist, workerArgs *wa, int src) {
    std::ofstream Ofile;
    if (wa->writeMode) {
        Ofile.open(wa->outfile, std::ios_base::app);
        wa->write_lock.lock();
    }
    int src_imp, dst_imp, calc_imp, fin_imp;
    // std::vector<userDataPoint> sourceUserDataPoints = wa->primaryMap.retrieveEntry(src);
    // for (auto sourceUserDataPoint : sourceUserDataPoints) {
    //     src_imp = sourceUserDataPoint.dist / wa->impedence;
    //     std::unordered_map<std::string, int> row_data;
    //     if ((wa->write_mode == WRITE_ONLY) || (wa->write_mode == WRITE_AND_LOAD)) {
    //         Ofile <<  sourceUserDataPoint.id << ",";
    //     }
    //     std::vector<userDataPoint> destUserDataPoints = wa->primaryMap.retrieveEntry(src);
    //     for (auto j = 0; j < wa->V; j++) {
    //         dst_imp = wa->secondaryNN.me.entries.at(j).dist * wa->impedence;
    //         calc_imp = dist[wa->secondaryNN.me.entries.at(j).pos];
    //         if (calc_imp == INT_MAX) {
    //             fin_imp = -1;
    //         } else if (me_prim.entries.at(i).pos == wa->secondaryNN.me.entries.at(j).pos) {
    //             fin_imp = 0;
    //         }
    //         else {
    //             fin_imp = dst_imp + calc_imp + src_imp;
    //         }
    //         if ((wa->write_mode == WRITE_ONLY) || (wa->write_mode == WRITE_AND_LOAD)) {
    //             Ofile << fin_imp;
    //         }
    //         if (j < wa->secondaryNN.me.entries.size() - 1) {
    //             if ((wa->write_mode == WRITE_ONLY) || (wa->write_mode == WRITE_AND_LOAD)) {
    //                 Ofile << ",";
    //             }
    //         }
    //         row_data[wa->secondaryNN.me.entries.at(j).id] = fin_imp;

    //     }
    //     if ((wa->write_mode == LOAD_ONLY) || (wa->write_mode == WRITE_AND_LOAD)) {
    //         wa->insert_data.lock();
    //         wa->df.insertRow(row_data, me_prim.entries[i].id);
    //         wa->insert_data.unlock();
    //     }
    //     if ((wa->write_mode == WRITE_ONLY) || (wa->write_mode == WRITE_AND_LOAD)) {
    //         Ofile << std::endl;
    //     }
    // }
    if (wa->writeMode) {
        Ofile.close();
        wa->write_lock.unlock();
    }
}


/* The main function that calulates distances of shortest paths from src to all*/
/* vertices. It is a O(ELogV) function*/
void dijkstra(int src, workerArgs *wa) {

    int V = wa->graph.V;// Get the number of vertices in graph
    
    std::vector<int> dist;
    dist.reserve(V);

    // minHeap represents set E
    MinHeap minHeap(V);
 
    // Initialize min heap with all vertices. dist value of all vertices 
    for (int v = 0; v < V; ++v)
    {
        dist[v] = INT_MAX;
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

    //write row to file or find best
    writeRow(dist, wa, src);
    
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
    std::cout << "foo" << std::endl;
    workerQueue wq(numThreads);
    std::cout << "bar" << std::endl;
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
