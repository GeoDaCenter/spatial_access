// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#pragma once

#include <stdexcept>
#include <unordered_map>
#include <vector>
#include <climits>
#include <queue>
#include <functional>
#include <numeric>
#include <mutex>

#include "threadUtilities.h"
#include "dataFrame.h"
#include "Graph.h"
#include "userDataContainer.h"
#include "Serializer.h"
using namespace std;

typedef unsigned long int network_node;
typedef unsigned short int time_value;

template<class row_label_type, class col_label_type>
void calculateSingleRowOfDataFrame(const std::vector<time_value> &dist,
                                   graphWorkerArgs<row_label_type, col_label_type> &worker_args, network_node src) {
    time_value src_imp, dst_imp, calc_imp, fin_imp;
    //  iterate through each data point of the current source tract
    auto sourceTract = worker_args.userSourceData.retrieveTract(src);
    for (auto sourceDataPoint : sourceTract.retrieveDataPoints())
    {
        src_imp = sourceDataPoint.lastMileDistance;

        auto destNodeIds = worker_args.userDestData.retrieveUniqueNetworkNodeIds();
        // iterate through each dest tract
        std::vector<time_value> row_data;
        if (worker_args.df.isCompressible)
        {
            row_data.assign(worker_args.df.cols - sourceDataPoint.loc, USHRT_MAX);
        } else
        {
            row_data.assign(worker_args.df.cols, USHRT_MAX);
        }

        for (network_node destNodeId : destNodeIds)
        {
            auto destTract = worker_args.userDestData.retrieveTract(destNodeId);
            auto destPoints = destTract.retrieveDataPoints();
            for (auto destDataPoint : destPoints)
            {
                if (worker_args.df.isCompressible)
                {
                    if (worker_args.df.isUnderDiagonal(sourceDataPoint.loc, destDataPoint.loc))
                    {
                        continue;
                    }
                }
                calc_imp = dist.at(destNodeId);
                if ((worker_args.df.isSymmetric) && (destDataPoint.loc == sourceDataPoint.loc))
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
                if (worker_args.df.isCompressible)
                {
                    row_data.at(destDataPoint.loc - sourceDataPoint.loc) = fin_imp;
                } else {
                    row_data.at(destDataPoint.loc) = fin_imp;
                }


            }

        }
        worker_args.df.setRowByRowLoc(row_data, sourceDataPoint.loc);


    }

}


typedef std::pair<time_value, network_node> queue_pair;


template<class row_label_type, class col_label_type>
void doDijstraFromOneNetworkNode(network_node src, graphWorkerArgs<row_label_type, col_label_type> &worker_args,
                                 std::vector<time_value>& dist_vector)
{
    network_node V = worker_args.graph.getV();

    std::fill(dist_vector.begin(), dist_vector.end(), USHRT_MAX);
    dist_vector.at(src) = 0;
    std::priority_queue<queue_pair, std::vector<queue_pair>, std::greater<queue_pair>> queue;
    queue.push(std::make_pair(0, src));
    std::vector<bool> visited(V, false);
    while (!queue.empty())
    {
        network_node u = queue.top().second;
        queue.pop();
        visited.at(u) = true;
        for (auto neighbor : worker_args.graph.neighbors.at(u))
        {
            auto v = std::get<0>(neighbor);
            auto weight = std::get<1>(neighbor);
            if ((!visited.at(v)) and (dist_vector.at(v) > dist_vector.at(u) + weight))
            {
                dist_vector.at(v) = dist_vector.at(u) + weight;
                queue.push(std::make_pair(dist_vector.at(v), v));
            }
        }
    }

    //calculate row and add to dataFrame
    calculateSingleRowOfDataFrame(dist_vector, worker_args, src);

}

template<class row_label_type, class col_label_type>
void graphWorkerHandler(graphWorkerArgs<row_label_type,col_label_type> &worker_args)
{
    network_node src;
    bool endNow = false;
    std::vector<unsigned short int> dist_vector(worker_args.graph.getV());
    while (!worker_args.jq.empty()) {
        src = worker_args.jq.pop(endNow);
        //exit loop if job queue worker_argss empty
        if (endNow) {
            break;
        }
        doDijstraFromOneNetworkNode(src, worker_args, dist_vector);
    }
}


template <class row_label_type, class col_label_type>
class transitMatrix {
public:

    // Public members
    dataFrame<row_label_type, col_label_type> df;
    userDataContainer userSourceDataContainer;
    userDataContainer userDestDataContainer;
    Graph graph;

    // Constructors
    transitMatrix(bool isCompressible, bool isSymmetric,  unsigned long int rows, unsigned long int cols)
    : df(isCompressible, isSymmetric, rows, cols) {}
    transitMatrix()= default;

    void
    prepareGraphWithVertices(unsigned long int V)
    {
        graph.initializeGraph(V);

    }

    void setMockDataFrame(const std::vector<std::vector<unsigned short int>> dataset,
                          const std::vector<row_label_type>& row_ids,
                          const std::vector<col_label_type>& col_ids)
    {
        df.setMockDataFrame(dataset, row_ids, col_ids);
    }


    void
    addToUserSourceDataContainer(network_node networkNodeId, const row_label_type& row_id, time_value lastMileDistance)
    {
        network_node row_loc = df.addToRowIndex(row_id);
        this->userSourceDataContainer.addPoint(networkNodeId, row_loc, lastMileDistance);

    }


    void
    addToUserDestDataContainer(network_node networkNodeId, const col_label_type& col_id, time_value lastMileDistance)
    {
        network_node col_loc = this->df.addToColIndex(col_id);
        this->userDestDataContainer.addPoint(networkNodeId, col_loc, lastMileDistance);
    }

    void addSingleEdgeToGraph(network_node from_loc, network_node to_loc,
                        time_value edge_weight, bool is_bidirectional)
    {
        graph.addEdge(from_loc, to_loc, edge_weight);
        if (is_bidirectional)
        {
            graph.addEdge(to_loc, from_loc, edge_weight);
        }
    }

    void
    addEdgesToGraph(const std::vector<network_node>& from_column,
            const std::vector<network_node>& to_column,
            const std::vector<time_value>& edge_weights_column,
            const std::vector<bool>& is_bidirectional_column)
    {
        for (unsigned long int i = 0; i < from_column.size(); i++)
        {
            auto from_loc = from_column.at(i);
            auto to_loc = to_column.at(i);
            auto edge_weight = edge_weights_column.at(i);
            auto is_bidirectional = is_bidirectional_column.at(i);
            graph.addEdge(from_loc, to_loc, edge_weight);
            if (is_bidirectional)
            {
                graph.addEdge(to_loc, from_loc, edge_weight);
            }
        }
    }

    void
    addToCategoryMap(const col_label_type& dest_id, const std::string& category)
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

    void
    compute(unsigned int numThreads)
    {
        try
        {
            graphWorkerArgs<row_label_type, col_label_type> worker_args(graph, userSourceDataContainer, userDestDataContainer,
                                                               df);
            worker_args.initialize();
            workerQueue<row_label_type, col_label_type> wq(numThreads, graphWorkerHandler, worker_args);
            wq.startGraphWorker();
        } catch (...)
        {
            throw std::runtime_error("Failed to compute matrix");
        }
    }


    const std::vector<std::pair<col_label_type, time_value>>
    getValuesBySource(row_label_type source_id, bool sort) const
    {
        return this->df.getValuesByRowId(source_id, sort);
    }


    const std::vector<std::pair<row_label_type, time_value>>
    getValuesByDest(col_label_type dest_id, bool sort) const
    {
        return this->df.getValuesByColId(dest_id, sort);
    }



    const std::unordered_map<row_label_type, std::vector<col_label_type>>
    getDestsInRange(unsigned int threshold) const
    {
        // Initialize maps
        std::unordered_map<row_label_type, std::vector<col_label_type>> destsInRange;
        for (network_node row_loc = 0; row_loc < df.rows; row_loc++)
        {
            std::vector<col_label_type> valueData;
            for (network_node col_loc = 0; col_loc < df.cols; col_loc++) {
                if (df.getValueByLoc(row_loc, col_loc) <= threshold) {
                    valueData.push_back(df.getColIdForLoc(col_loc));
                }
            }
            row_label_type row_id = df.getRowIdForLoc(row_loc);
            destsInRange.emplace(std::make_pair(row_id, valueData));
        }
        return destsInRange;

    }


    const std::unordered_map<col_label_type, std::vector<row_label_type>>
    getSourcesInRange(unsigned int threshold) const
    {
        // Initialize maps
        std::unordered_map<col_label_type, std::vector<row_label_type>> sourcesInRange;
        for (network_node col_loc = 0; col_loc < df.cols; col_loc++)
        {
            std::vector<row_label_type> valueData;
            for (network_node row_loc = 0; row_loc < df.rows; row_loc++) {
                if (df.getValueByLoc(row_loc, col_loc) <= threshold) {
                    valueData.push_back(df.getRowIdForLoc(row_loc));
                }
            }
            col_label_type col_id = df.getColIdForLoc(col_loc);
            sourcesInRange.emplace(std::make_pair(col_id, valueData));
        }
        return sourcesInRange;

    }


    time_value
    timeToNearestDestPerCategory(const row_label_type& source_id, const std::string& category) const
    {
        time_value minimum = USHRT_MAX;
        for (const col_label_type dest_id : categoryToDestMap.at(category))
        {
            time_value dest_time = this->df.getValueById(source_id, dest_id);
            if (dest_time <= minimum)
            {
                minimum = dest_time;
            }
        }
        return minimum;
    }


    time_value
    countDestsInRangePerCategory(const row_label_type& source_id, const std::string& category, time_value range) const
    {
        time_value count = 0;
        for (const col_label_type dest_id : categoryToDestMap.at(category))
        {
            if (this->df.getValueById(source_id, dest_id) <= range)
            {
                count++;
            }
        }
        return count;
    }


    time_value
    timeToNearestDest(const row_label_type& source_id) const
    {
        time_value minimum = USHRT_MAX;
        network_node row_loc = df.getRowLocForId(source_id);
        for (network_node col_loc = 0; col_loc < df.cols; col_loc++)
        {
            time_value dest_time = this->df.getValueByLoc(row_loc, col_loc);
            if (dest_time <= minimum)
            {
                minimum = dest_time;
            }
        }
        return minimum;
    }


    time_value
    countDestsInRange(const row_label_type& source_id, time_value range) const
    {

        time_value count = 0;
        network_node row_loc = df.getRowLocForId(source_id);
        for (network_node col_loc = 0; col_loc < df.cols; col_loc++)
        {
            if (this->df.getValueByLoc(row_loc, col_loc) <= range)
            {
                count++;
            }
        }
        return count;
    }

    // Getters


    time_value
    getValueById(const row_label_type& row_id, const col_label_type& col_id) const
    {
        return df.getValueById(row_id, col_id);
    }

    // IO

    void
    printDataFrame() const
    {
        this->df.printDataFrame();
    }

    void
    readTMX(const std::string &infile) {
        df.readTMX(infile);
    }

    void
    readOTPCSV(const std::string &infile)
    {
        df.readOTPCSV(infile);
    }


    void
    writeCSV(const std::string &outfile) const
    {
        try {
            df.writeCSV(outfile);
        }
        catch (...)
        {
            throw std::runtime_error("Unable to write csv");
        }
    }

    void
    writeTMX(const std::string &outfile) const
    {
        try {
            df.writeTMX(outfile);
        }
        catch (...)
        {
            throw std::runtime_error("Unable to write tmx");
        }

    }


private:
    // Private Members
    std::unordered_map<std::string, std::vector<col_label_type>> categoryToDestMap;

};