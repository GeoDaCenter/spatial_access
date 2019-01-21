#include <sstream>
#include <iostream>
#include <fstream>
#include <string>
#include <stdexcept>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <utility>
#include <climits>

#include "transitMatrix.h"


/*write_row: write a row to file*/
void calculateRow(const std::vector<int> &dist, graphWorkerArgs *wa, int src) {
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
                if (wa->df.isSymmetric())
                {
                    if (wa->df.isUnderDiagonal(sourceDataPoint.id, destDataPoint.id))
                    {
                        continue;
                    }
                }
                calc_imp = dist.at(destNodeId);
                if ((wa->df.isSymmetric()) && (destDataPoint.id == sourceDataPoint.id))
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
        wa->df.insertRow(row_data, sourceDataPoint.id);
    }
}


/* The main function that calulates distances of shortest paths from src to all*/
/* vertices. It is a O(ELogV) function*/
void dijkstra(int src, graphWorkerArgs *wa) {
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
            if (minHeap.isInMinHeap(v) && (dist[u] != USHRT_MAX) && 
                                          (pCrawl->weight + dist[u] < dist[v]))
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

void graphWorkerHandler(graphWorkerArgs* wa) {
    int src;
    bool endNow = false;
    while (!wa->jq.empty()) {
        src = wa->jq.pop(endNow);

        //exit loop if job queue was empty
        if (endNow) {
            break;
        }
        dijkstra(src, wa);
    }
}

void calculateValuesForOneRow(unsigned long int row_label, rangeWorkerArgs *wa)
{
    for (unsigned long int col_label : wa->df.metaData.col_label_int())
        {
            if ((wa->df.retrieveValue(row_label, col_label) <= wa->threshold) and (row_label != col_label))
            {
                wa->rows.at(row_label).push_back(col_label);
                wa->column_write_lock.lock();
                wa->cols.at(col_label).push_back(row_label);
                wa->column_write_lock.unlock();
            }
        }

}

void rangeWorkerHandler(rangeWorkerArgs* wa) {
    unsigned long int row_id;
    bool endNow = false;
    while (!wa->jq.empty()) {
        row_id = wa->jq.pop(endNow);

        //exit loop if job queue was empty
        if (endNow) {
            break;
        }
        calculateValuesForOneRow(row_id, wa);
    }
}


namespace lmnoel {

transitMatrix::transitMatrix(int V, bool isSymmetric)
{
    this->previousThreshold = 0;
    this->numNodes = V;
    this->isSymmetric = isSymmetric;
    graph.initializeGraph(V);
}


transitMatrix::transitMatrix(const std::string& infile, bool isSymmetric, bool isOTPMatrix) 
{
    this->previousThreshold = 0;
    if (isOTPMatrix)
    {
        this->isSymmetric = false;
        if (!df.readOTPMatrix(infile))
        {
            throw std::runtime_error("failed to load dataFrame from OTP matrix");
        }   
        return;
    }
    if (infile.find(".csv") != std::string::npos)
    {
        if (!df.readCSV(infile)) 
        {
            throw std::runtime_error("failed to load dataFrame from csv");
        }
        // assume dataFrame read from csv is not symmetric because it has
        // no metadata
        this->isSymmetric = isSymmetric;
    }
    else 
    {
        if (!df.readTMX(infile)) 
        {
            throw std::runtime_error("failed to load dataFrame from tmx");
        }
        // set the transitMatrix's symmetric boolean based on tmx file
        this->isSymmetric = df.isSymmetric();
    }
  

}



bool transitMatrix::writeCSV(const std::string &outfile)
{
    return this->df.writeCSV(outfile);
}

bool transitMatrix::writeTMX(const std::string &outfile)
{
    return this->df.writeTMX(outfile);
}



void transitMatrix::prepareDataFrame()
{
    auto userSourceIds = userSourceDataContainer.retrieveAllUserDataIds();
    auto userDestIds = userDestDataContainer.retrieveAllUserDataIds();
    df.setSymmetric(this->isSymmetric);
    df.reserve(userSourceIds, userDestIds);
}

void transitMatrix::compute(int numThreads)
{
    prepareDataFrame();
    graphWorkerArgs wa(graph, userSourceDataContainer, userDestDataContainer, 
        numNodes, df);
    wa.initialize();  
    workerQueue wq(numThreads);
    wq.startGraphWorker(graphWorkerHandler, &wa);

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

void transitMatrix::printDataFrame() const
{
    this->df.printDataFrame();
}


int transitMatrix::get(unsigned long int source, unsigned long int dest) const
{
    return df.retrieveValue(source, dest);
}

void transitMatrix::calculateValuesInRange(int threshold, int numThreads)
{
    // Initialize maps
    for (unsigned long int row_id : this->df.metaData.row_label_int())
    {
        std::vector<unsigned long int> valueData;
        // If the map is uninitialized, emplace the keys
        if (previousThreshold == 0)
        {
            this->destsInRange.emplace(std::make_pair(row_id, valueData));
        }
        // otherwise, reset the values
        else
        {
            this->destsInRange.at(row_id) = valueData;
        }
    }

    for (unsigned long int col_id : this->df.metaData.col_label_int())
    {
        std::vector<unsigned long int> valueData;
        // If the map is uninitialized, emplace the keys
        if (previousThreshold == 0)
        {
            this->sourcesInRange.emplace(std::make_pair(col_id, valueData));
        }
        // otherwise, reset the values
        else
        {
            this->sourcesInRange.at(col_id) = valueData;
        }
    }
    
    rangeWorkerArgs wa(this->df, threshold, this->destsInRange, this->sourcesInRange);
    wa.initialize();
    workerQueue wq(numThreads);
    wq.startRangeWorker(rangeWorkerHandler, &wa);
    this->previousThreshold = threshold;
    

}

const std::unordered_map<unsigned long int, std::vector<unsigned long int>>& transitMatrix::getDestsInRange(int threshold, int numThreads)
{
    // if transitMatrix has not yet calculated destsInRange for this value of 
    // threshold (which defaults to zero if it has never been calcualtes)
    if (this->previousThreshold != threshold)
    {
        calculateValuesInRange(threshold, numThreads);
    }
    return this->destsInRange;
}


const std::unordered_map<unsigned long int, std::vector<unsigned long int>>& transitMatrix::getSourcesInRange(int threshold, int numThreads)
{
    // if transitMatrix has not yet calculated destsInRange for this value of 
    // threshold (which defaults to zero if it has never been calcualtes)
    if (this->previousThreshold != threshold)
    {
        calculateValuesInRange(threshold, numThreads);
    }
    return this->sourcesInRange;
}

const std::vector<std::pair<unsigned long int, unsigned short int>> transitMatrix::getValuesBySource(unsigned long int source_id, bool sort)
{
    return this->df.getValuesByRow(source_id, sort);
}

const std::vector<std::pair<unsigned long int, unsigned short int>> transitMatrix::getValuesByDest(unsigned long int dest_id, bool sort)
{
    return this->df.getValuesByCol(dest_id, sort);
}

} // namespace lnoel