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

        std::unordered_map<unsigned int, unsigned short int> row_data;
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

void calculateValuesForOneIndex(unsigned long int index, rangeWorkerArgs *wa)
{
    // calculate dests (columns) in range of sources (rows)
    if (wa->isDestsInRange)
    {
        for (unsigned long int col_label : wa->df.metaData.col_label())
        {
            if (wa->df.retrieveValue(index, col_label) <= wa->threshold)
            {
                wa->rows.at(index).push_back(col_label);
            }
        }
    }
    else // calculate sources (rows) in range of dests (columns)
    {   
        for (unsigned long int row_label : wa->df.metaData.row_label())
        {
            if (wa->df.retrieveValue(row_label, index) <= wa->threshold)
            {
                wa->cols.at(index).push_back(row_label);
            }
        }
    }    

}

void rangeWorkerHandler(rangeWorkerArgs* wa) {
    unsigned long int index;
    bool endNow = false;
    while (!wa->jq.empty()) {
        index = wa->jq.pop(endNow);

        //exit loop if job queue was empty
        if (endNow) {
            break;
        }
        calculateValuesForOneIndex(index, wa);
    }
}


namespace lmnoel {


template<class row_label_type, class col_label_type>
void transitMatrix<row_label_type, col_label_type>::prepareGraphWithVertices(int V)
{
    numNodes = V;
    graph.initializeGraph(V);
}

template<class row_label_type, class col_label_type>
unsigned int transitMatrix<row_label_type, col_label_type>::getRows() const {
    return df.getRows();
}

template<class row_label_type, class col_label_type>
void transitMatrix<row_label_type, col_label_type>::setRows(unsigned int rows) {
    df.setRows(cols);
}

template<class row_label_type, class col_label_type>
unsigned int transitMatrix<row_label_type, col_label_type>::getCols() const {
    return df.getCols();
}

template<class row_label_type, class col_label_type>
void transitMatrix<row_label_type, col_label_type>::setCols(unsigned int cols) {
    df.setCols(cols);
}

template<class row_label_type, class col_label_type>
bool transitMatrix<row_label_type, col_label_type>::getIsSymmetric() const {
    return df.getIsSymmetric();
}

template<class row_label_type, class col_label_type>
void transitMatrix<row_label_type, col_label_type>::setIsSymmetric(bool isSymmetric)
{
    df.setIsSymmetric(isSymmetric);
}

template<class row_label_type, class col_label_type>
void transitMatrix<row_label_type, col_label_type>::setDataset(const std::vector<std::vector<unsigned short int>>& dataset)
{
    df.setDataset(dataset);
}

template<class row_label_type, class col_label_type>
const std::vector<std::vector<unsigned short int>>& transitMatrix<row_label_type, col_label_type>::getDataset() const
{
    return df.getDataset();
}

template<class row_label_type, class col_label_type>
void transitMatrix<row_label_type, col_label_type>::setPrimaryDatasetIds(const std::vector<row_label_type>& primaryDatasetIds)
{
    df.setRowIds(primaryDatasetIds);
}

template<class row_label_type, class col_label_type>
void transitMatrix<row_label_type, col_label_type>::setSecondaryDatasetIds(const std::vector<col_label_type>& secondaryDatasetIds)
{
    df.setColIds(secondaryDatasetIds);
}

template<class row_label_type, class col_label_type>
const std::vector<row_label_type>& transitMatrix<row_label_type, col_label_type>::getPrimaryDatasetIds()
{
    return df.getRowIds();
}

template<class row_label_type, class col_label_type>
const std::vector<col_label_type>& transitMatrix<row_label_type, col_label_type>::getSecondaryDatasetIds()
{
    return df.getColIds();
}

template<class row_label_type, class col_label_type>
bool transitMatrix<row_label_type, col_label_type>::writeCSV(const std::string &outfile)
{
    try {
        return this->df.writeCSV(outfile);    
    }
    catch (...)
    {
        throw std::runtime_error("Unable to write csv");
    }
}

template<class row_label_type, class col_label_type>
void transitMatrix<row_label_type, col_label_type>::compute(int numThreads)
{
    try 
    {
        graphWorkerArgs wa(graph, userSourceDataContainer, userDestDataContainer, 
            numNodes, df);
        wa.initialize();  
        workerQueue wq(numThreads);
        wq.startGraphWorker(graphWorkerHandler, &wa);
    } catch (...)
    {
        throw std::runtime_error("Failed to compute matrix");
    }

}

template<class row_label_type, class col_label_type>
void transitMatrix<row_label_type, col_label_type>::addToUserDestDataContainer(int networkNodeId, const col_label_type& col_id, int lastMileDistance)
{
    unsigned int col_loc = this->df.addToColIndex(id);
    this->addToUserDestDataContainerInt(networkNodeId, col_loc, lastMileDistance);
}

template<class row_label_type, class col_label_type>
void transitMatrix<row_label_type, col_label_type>::addToUserSourceDataContainer(int networkNodeId, const row_label_type& row_id, int lastMileDistance, bool isBidirectional)
{
    unsigned int row_loc = df.addToRowIndex(row_id);
    this->addToUserSourceDataContainerInt(networkNodeId, row_loc, lastMileDistance, isBidirectional);
}


template<class row_label_type, class col_label_type>
void transitMatrix<row_label_type, col_label_type>::addToCategoryMap(const col_label_type& dest_id, const std::string& category)
{
    if (categoryToDestMap.find(category) != categoryToDestMap.end())
    {
        categoryToDestMap.at(category).push_back(dest_id);
    }
    else {
        std::vector<col_label_type> data;
        data.push_back(dest_id);
        categoryToDestMap.emplace(std::make_pair(category, data));
    }
}

template<class row_label_type, class col_label_type>
unsigned short int transitMatrix<row_label_type, col_label_type>::timeToNearestDestPerCategory(const row_label_type& source_id, const std::string& category) const
{
    unsigned short int minimum = USHRT_MAX;
    for (const col_label_type dest_id : categoryToDestMap.at(category))
    {
        unsigned short int dest_time = this->df.retrieveValue(source_id, dest_id);
        if (dest_time <= minimum)
        {
            minimum = dest_time;
        }
    }
    return minimum;
}

template<class row_label_type, class col_label_type>
unsigned short int transitMatrix<row_label_type, col_label_type>::countDestsInRangePerCategory(const row_label_type& source_id, const std::string& category, unsigned short int range) const
{
    unsigned short int count = 0;
    for (const col_label_type dest_id : categoryToDestMap.at(category))
    {
        if (this->df.retrieveValue(source_id, dest_id) <= range)
        {
            count++;
        }
    }
    return count;
}

template<class row_label_type, class col_label_type>
unsigned short int transitMatrix<row_label_type, col_label_type>::timeToNearestDest(const row_label_type& source_id) const
{
    unsigned short int minimum = USHRT_MAX;
    unsigned int row_loc = df.getRowLocForId(source_id);
    for (unsigned int col_loc = 0; col_loc < df.getCols(); col_loc++)
    {
        unsigned short int dest_time = this->df.getValueByLoc(row_loc, col_loc);
        if (dest_time <= minimum)
        {
            minimum = dest_time;
        }
    }
    return minimum;
}

    template<class row_label_type, class col_label_type>
unsigned short int transitMatrix<row_label_type, col_label_type>::countDestsInRange(const row_label_type& source_id, unsigned short int range) const
{
    unsigned short int count = 0;
    unsigned int row_loc = df.getRowLocForId(source_id);
    for (unsigned int col_loc = 0; col_loc < df.getCols(); col_loc++)
    {
        if (this->df.getValueByLoc(row_loc, col_loc) <= range)
        {
            count++;
        }
    }
    return count;
}


    template<class row_label_type, class col_label_type>
void transitMatrix<row_label_type, col_label_type>::addEdgeToGraph(int src, int dest, int weight, bool isBidirectional)
{
    graph.addEdge(src, dest, weight);
    if (isBidirectional)
    {
        graph.addEdge(dest, src, weight);
    }
}

    template<class row_label_type, class col_label_type>
void transitMatrix<row_label_type, col_label_type>::printDataFrame() const
{
    this->df.printDataFrame();
}


    template<class row_label_type, class col_label_type>
int transitMatrix<row_label_type, col_label_type>::getValueById(const row_label_type&, const col_label_type&) const
{
    return df.getValueById(source, dest);
}

template<class row_label_type, class col_label_type>
void transitMatrix<row_label_type, col_label_type>::getDestsInRange(unsigned int threshold, int numThreads)
{
    // Initialize maps
    std::unordered_map<row_label_type, std::vector<col_label_type>> destsInRange;
    for (const row_label_type row_id : this->df.getRowIds())
    {
        std::vector<col_label_type> valueData;

        destsInRange.emplace(std::make_pair(row_id, valueData));

    }

    rangeWorkerArgs wa(false, this->df, threshold, destsInRange);
    wa.initialize();
    workerQueue wq(1);
    wq.startRangeWorker(rangeWorkerHandler, &wa);
}

    template<class row_label_type, class col_label_type>
void transitMatrix<row_label_type, col_label_type>::getSourcesInRange(unsigned int threshold, int numThreads)
{
    // Initialize maps
    std::unordered_map<col_label_type, std::vector<row_label_type>> sourcesInRange;
    for (const col_label_type col_id : this->df.getColIds())
    {
        std::vector<row_label_type> valueData;

        sourcesInRange.emplace(std::make_pair(col_id, valueData));

    }
    
    rangeWorkerArgs wa(false, this->df, threshold, sourcesInRange);
    wa.initialize();
    workerQueue wq(1);
    wq.startRangeWorker(rangeWorkerHandler, &wa);
}

    template<class row_label_type, class col_label_type>
const std::vector<std::pair<col_label_type, unsigned short int>> transitMatrix<row_label_type, col_label_type>::getValuesBySource(row_label_type source_id, bool sort)
{
    return this->df.getValuesByRow(source_id, sort);
}

    template<class row_label_type, class col_label_type>
const std::vector<std::pair<row_label_type, unsigned short int>> transitMatrix<row_label_type, col_label_type>::getValuesByDest(col_label_type dest_id, bool sort)
{
    return this->df.getValuesByCol(dest_id, sort);
}

} // namespace lnoel