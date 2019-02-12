#pragma once

#include "threadUtilities.h"
#include "dataFrame.cpp"
#include "Graph.h"
#include "MinHeap.h"
#include "userDataContainer.h"

#include <mutex>


/*write_row: write a row to file*/
void calculateRow(const std::vector<int> &dist, graphWorkerArgs *wa, int src);


/* Calulates distances of shortest paths from src to all*/
/* vertices. It is a O(ELogV) function*/
void dijkstra(int src, graphWorkerArgs *wa);

void graphWorkerHandler(graphWorkerArgs* wa);

void rangeWorkerHandler(rangeWorkerArgs* wa);

void calculateValuesForOneIndex(unsigned int index, rangeWorkerArgs *wa);


namespace lmnoel {

template <class row_label_type, class col_label_type>
class transitMatrix {
public:

    // Public members
    dataFrame<row_label_type, col_label_type> df;
    userDataContainer userSourceDataContainer;
    userDataContainer userDestDataContainer;
    Graph graph;
    int numNodes;

    // Constructors
    transitMatrix(bool isSymmetric, unsigned int rows, unsigned int cols) : df(isSymmetric, rows, cols) {
        this->sourcesInRangeThreshold = 0;
        this->destsInRangeThreshold = 0;
        this->numNodes = 0;
    }

    // Initialization
    void addToUserSourceDataContainer(int networkNodeId, row_label_type row_id, int lastMileDistance, bool isBidirectional);
    void addToUserDestDataContainer(int networkNodeId, col_label_type col_id, int lastMileDistance);
    void addEdgeToGraph(int src, int dest, int weight, bool isBidirectional);

    void compute(int numThreads);
    void addToCategoryMap(col_label_type dest_id, const std::string& category);
    void prepareGraphWithVertices(int V);


    // Calculations
    const std::vector<std::pair<col_label_type, unsigned short int>> getValuesBySource(row_label_type source_id, bool sort);
    const std::vector<std::pair<row_label_type, unsigned short int>> getValuesByDest(col_label_type dest_id, bool sort);
    const std::unordered_map<row_label_type, std::vector<col_label_type>>& getDestsInRange(unsigned int range, int numThreads);
    const std::unordered_map<col_label_type, std::vector<row_label_type>>& getSourcesInRange(unsigned int range, int numThreads);

    unsigned short int timeToNearestDestPerCategory(row_label_type source_id, const std::string& category) const;
    unsigned short int countDestsInRangePerCategory(row_label_type source_id, const std::string& category, unsigned short int range) const;
    unsigned short int timeToNearestDest(row_label_type source_id) const;
    unsigned short int countDestsInRange(row_label_type source_id, unsigned short int range) const;

    // IO
    bool writeCSV(const std::string &outfile);
    void printDataFrame() const;

    // Getters
    unsigned short int getValueById(const row_label_type& source, const col_label_type& dest) const;
    unsigned int getRows();
    unsigned int getColumns();
    bool getIsSymmetric();
    const std::vector<std::vector<unsigned short int>>& getDataset();
    const std::vector<row_label_type>& getPrimaryDatasetIds();
    const std::vector<col_label_type>& getSecondaryDatasetIds();

    // Setters
    void setRows(unsigned int rows);
    void setColumns(unsigned int columns);
    void setIsSymmetric(bool isSymmetric);
    void setDataset(const std::vector<std::vector<unsigned short int>>& dataset);
    void setPrimaryDatasetIds(const std::vector<row_label_type>& primaryDatasetIds);
    void setSecondaryDatasetIds(const std::vector<col_label_type>& secondaryDatasetIds);


    // Aliases (for cython bug)
    typedef unsigned long int label;
    typedef unsigned short int value;


private:
    // Private Members
    std::unordered_map<std::string, std::vector<col_label_type>> categoryToDestMap;


};


} // namespace lnoel