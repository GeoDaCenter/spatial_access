// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#pragma once

#include "threadUtilities.cpp"
#include "dataFrame.h"
#include "Graph.cpp"
#include "userDataContainer.cpp"
#include "Serializer.cpp"

#include <stdexcept>
#include <unordered_map>
#include <vector>
#include <climits>
#include <queue>
#include <functional>
#include <numeric>


#include <mutex>
using namespace std;

int getTypeOfTMX(const std::string& filename)
{
    Deserializer d(filename);
    return d.readShortInt();
}

template<class row_label_type, class col_label_type>
void calculateRow(const std::vector<unsigned short int> &dist, graphWorkerArgs<row_label_type, col_label_type> *wa, unsigned long int src) {
    unsigned short int src_imp, dst_imp, calc_imp, fin_imp;
    //  iterate through each data point of the current source tract
    auto sourceTract = wa->userSourceData.retrieveTract(src);
    for (auto sourceDataPoint : sourceTract.retrieveDataPoints())
    {
        src_imp = sourceDataPoint.lastMileDistance;

        auto destNodeIds = wa->userDestData.retrieveUniqueNetworkNodeIds();
        // iterate through each dest tract
        std::vector<unsigned short int> row_data;
        if (wa->df.getIsSymmetric())
        {
            row_data.assign(wa->df.getCols() - sourceDataPoint.loc, USHRT_MAX);
        } else
        {
            row_data.assign(wa->df.getCols(), USHRT_MAX);
        }

        for (unsigned long int destNodeId : destNodeIds)
        {
            auto destTract = wa->userDestData.retrieveTract(destNodeId);
            auto destPoints = destTract.retrieveDataPoints();
            for (auto destDataPoint : destPoints)
            {
                if (wa->df.getIsSymmetric())
                {
                    if (wa->df.isUnderDiagonal(sourceDataPoint.loc, destDataPoint.loc))
                    {
                        continue;
                    }
                }
                calc_imp = dist.at(destNodeId);
                if ((wa->df.getIsSymmetric()) && (destDataPoint.loc == sourceDataPoint.loc))
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
                if (wa->df.getIsSymmetric())
                {
                    row_data.at(destDataPoint.loc - sourceDataPoint.loc) = fin_imp;
                } else {
                    row_data.at(destDataPoint.loc) = fin_imp;
                }


            }

        }
        wa->df.setRowByRowLoc(row_data, sourceDataPoint.loc);


    }
}


typedef std::pair<unsigned short int, unsigned long int> queue_pair;


template<class row_label_type, class col_label_type>
void dijkstra(unsigned long int src, graphWorkerArgs<row_label_type, col_label_type> *wa) {
    unsigned long int V = wa->graph.getV();// Get the number of vertices in graph

    std::vector<unsigned short int> dist(V, USHRT_MAX);
    dist.at(src) = 0;
    std::priority_queue<queue_pair, std::vector<queue_pair>, std::greater<queue_pair>> queue;
    queue.push(std::make_pair(0, src));
    std::vector<bool> visited(V, false);
    while (!queue.empty())
    {
        unsigned long int u = queue.top().second;
        queue.pop();
        visited.at(u) = true;
        for (auto neighbor : wa->graph.neighbors.at(u))
        {
            auto v = std::get<0>(neighbor);
            auto weight = std::get<1>(neighbor);
            if ((!visited.at(v)) and (dist.at(v) > dist.at(u) + weight))
            {
                dist.at(v) = dist.at(u) + weight;
                queue.push(std::make_pair(dist.at(v), v));
            }
        }
    }

    //calculate row and add to dataFrame
    calculateRow(dist, wa, src);

}

template<class row_label_type, class col_label_type>
void graphWorkerHandler(graphWorkerArgs<row_label_type,col_label_type>* wa)
{
    unsigned long int src;
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


namespace lmnoel {

template <class row_label_type, class col_label_type>
class transitMatrix {
public:

    // Public members
    dataFrame<row_label_type, col_label_type> df;
    userDataContainer userSourceDataContainer;
    userDataContainer userDestDataContainer;
    Graph graph;
    unsigned long int numNodes;

    // Constructors
    transitMatrix(bool isSymmetric, unsigned long int rows, unsigned long int cols) : df(isSymmetric, rows, cols), numNodes(0) {}
    transitMatrix()= default;

    void prepareGraphWithVertices(unsigned long int V)
    {
        numNodes = V;
        graph.initializeGraph(V);
    }


    void addToUserSourceDataContainer(unsigned long int networkNodeId, const row_label_type& row_id, unsigned short int lastMileDistance)
    {
        unsigned long int row_loc = df.addToRowIndex(row_id);
        this->userSourceDataContainer.addPoint(networkNodeId, row_loc, lastMileDistance);

    }


    void addToUserDestDataContainer(unsigned long int networkNodeId, const col_label_type& col_id, unsigned short int lastMileDistance)
    {
        unsigned long int col_loc = this->df.addToColIndex(col_id);
        this->userDestDataContainer.addPoint(networkNodeId, col_loc, lastMileDistance);
    }


    void addEdgeToGraph(unsigned long int src, unsigned long int dest, unsigned short int weight, bool isBidirectional)
    {

        graph.addEdge(src, dest, weight);
        if (isBidirectional)
        {
            graph.addEdge(dest, src, weight);
        }
    }


    void addToCategoryMap(const col_label_type& dest_id, const std::string& category)
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

    // Calculations



    void compute(unsigned int numThreads)
    {
        try
        {
            graphWorkerArgs<row_label_type, col_label_type> wa(graph, userSourceDataContainer, userDestDataContainer,
                                                               numNodes, df);
            wa.initialize();
            workerQueue<row_label_type, col_label_type> wq(numThreads, graphWorkerHandler, &wa);
            wq.startGraphWorker();
        } catch (...)
        {
            throw std::runtime_error("Failed to compute matrix");
        }

    }


    const std::vector<std::pair<col_label_type, unsigned short int>> getValuesBySource(row_label_type source_id, bool sort) const
    {
        return this->df.getValuesByRowId(source_id, sort);
    }


    const std::vector<std::pair<row_label_type, unsigned short int>> getValuesByDest(col_label_type dest_id, bool sort) const
    {
        return this->df.getValuesByColId(dest_id, sort);
    }



    const std::unordered_map<row_label_type, std::vector<col_label_type>> getDestsInRange(unsigned int threshold, unsigned int numThreads) const
    {
        // Initialize maps
        std::unordered_map<row_label_type, std::vector<col_label_type>> destsInRange;
        for (unsigned long int row_loc = 0; row_loc < df.getRows(); row_loc++)
        {
            std::vector<col_label_type> valueData;
            for (unsigned long int col_loc = 0; col_loc < df.getCols(); col_loc++) {
                if (df.getValueByLoc(row_loc, col_loc) <= threshold) {
                    valueData.push_back(df.getColIdForLoc(col_loc));
                }
            }
            row_label_type row_id = df.getRowIdForLoc(row_loc);
            destsInRange.emplace(std::make_pair(row_id, valueData));
        }
        return destsInRange;

    }


    const std::unordered_map<col_label_type, std::vector<row_label_type>> getSourcesInRange(unsigned int threshold, unsigned int numThreads) const
    {
        // Initialize maps
        std::unordered_map<col_label_type, std::vector<row_label_type>> sourcesInRange;
        for (unsigned long int col_loc = 0; col_loc < df.getCols(); col_loc++)
        {
            std::vector<row_label_type> valueData;
            for (unsigned long int row_loc = 0; row_loc < df.getRows(); row_loc++) {
                if (df.getValueByLoc(row_loc, col_loc) <= threshold) {
                    valueData.push_back(df.getRowIdForLoc(row_loc));
                }
            }
            col_label_type col_id = df.getColIdForLoc(col_loc);
            sourcesInRange.emplace(std::make_pair(col_id, valueData));
        }
        return sourcesInRange;

    }


    unsigned short int timeToNearestDestPerCategory(const row_label_type& source_id, const std::string& category) const
    {
        unsigned short int minimum = USHRT_MAX;
        for (const col_label_type dest_id : categoryToDestMap.at(category))
        {
            unsigned short int dest_time = this->df.getValueById(source_id, dest_id);
            if (dest_time <= minimum)
            {
                minimum = dest_time;
            }
        }
        return minimum;
    }


    unsigned short int countDestsInRangePerCategory(const row_label_type& source_id, const std::string& category, unsigned short int range) const
    {
        unsigned short int count = 0;
        for (const col_label_type dest_id : categoryToDestMap.at(category))
        {
            if (this->df.getValueById(source_id, dest_id) <= range)
            {
                count++;
            }
        }
        return count;
    }


    unsigned short int timeToNearestDest(const row_label_type& source_id) const
    {
        unsigned short int minimum = USHRT_MAX;
        unsigned long int row_loc = df.getRowLocForId(source_id);
        for (unsigned long int col_loc = 0; col_loc < df.getCols(); col_loc++)
        {
            unsigned short int dest_time = this->df.getValueByLoc(row_loc, col_loc);
            if (dest_time <= minimum)
            {
                minimum = dest_time;
            }
        }
        return minimum;
    }


    unsigned short int countDestsInRange(const row_label_type& source_id, unsigned short int range) const
    {

        unsigned short int count = 0;
        unsigned long int row_loc = df.getRowLocForId(source_id);
        for (unsigned long int col_loc = 0; col_loc < df.getCols(); col_loc++)
        {
            if (this->df.getValueByLoc(row_loc, col_loc) <= range)
            {
                count++;
            }
        }
        return count;
    }

    // Getters


    unsigned short int getValueById(const row_label_type& row_id, const col_label_type& col_id) const
    {
        return df.getValueById(row_id, col_id);
    }



    unsigned long int getRows() const
    {
        return df.getRows();
    }


    unsigned long int getCols() const
    {
        return df.getCols();
    }


    bool getIsSymmetric() const
    {
        return df.getIsSymmetric();
    }


    const std::vector<unsigned short int>& getDatasetRow(unsigned long int datasetRow) const
    {
        return df.getDatasetRow(datasetRow);
    }


    const std::vector<std::vector<unsigned short int>>& getDataset() const
    {
        return df.getDataset();
    }


    const std::vector<row_label_type>& getPrimaryDatasetIds() const
    {
        return df.getRowIds();
    }


    const std::vector<col_label_type>& getSecondaryDatasetIds() const
    {
        return df.getColIds();
    }

    // Setters


    void setRows(unsigned long int rows) {
        df.setRows(rows);
    }



    void setCols(unsigned long int cols) {
        df.setCols(cols);
    }



    void setIsSymmetric(bool isSymmetric)
    {
        df.setIsSymmetric(isSymmetric);
    }


    void setDataset(const std::vector<std::vector<unsigned short int>>& dataset)
    {
        df.setDataset(dataset);
    }


    void setPrimaryDatasetIds(const std::vector<row_label_type>& primaryDatasetIds)
    {
        df.setRowIds(primaryDatasetIds);
    }


    void setSecondaryDatasetIds(const std::vector<col_label_type>& secondaryDatasetIds)
    {
        df.setColIds(secondaryDatasetIds);
    }



    // IO


    void printDataFrame() const
    {
        this->df.printDataFrame();
    }

    void readTMX(const std::string &infile) {
        df.readTMX(infile);
    }


    void writeCSV(const std::string &outfile) const
    {
        try {
            df.writeCSV(outfile);
        }
        catch (...)
        {
            throw std::runtime_error("Unable to write csv");
        }
    }

    void writeTMX(const std::string &outfile) const
    {
        try {
            df.writeTMX(outfile);
        }
        catch (...)
        {
            throw std::runtime_error("Unable to write tmx");
        }

    }

    // Aliases (for cython bug)
    typedef unsigned short int value;
    typedef unsigned long int int_label;
    typedef std::pair<unsigned long int, unsigned short int> value_pair;


private:
    // Private Members
    std::unordered_map<std::string, std::vector<col_label_type>> categoryToDestMap;

};


} // namespace lnoel
typedef unsigned long int int_label;