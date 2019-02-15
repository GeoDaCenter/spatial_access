#pragma once

#include "threadUtilities.cpp"
#include "dataFrame.cpp"
#include "Graph.cpp"
#include "userDataContainer.cpp"

#include <mutex>


/*write_row: write a row to file*/
template<class row_label_type, class col_label_type>
void calculateRow(const std::vector<int> &dist, graphWorkerArgs<row_label_type, col_label_type> *wa, int src);


/* Calulates distances of shortest paths from src to all*/
/* vertices. It is a O(ELogV) function*/
template<class row_label_type, class col_label_type>
void dijkstra(unsigned int src, graphWorkerArgs<row_label_type, col_label_type> *wa);

template<class row_label_type, class col_label_type>
void graphWorkerHandler(graphWorkerArgs<row_label_type, col_label_type>* wa);

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
    transitMatrix(bool isSymmetric, unsigned int rows, unsigned int cols) : df(isSymmetric, rows, cols), numNodes(0) {}

    // Initialization
    void prepareGraphWithVertices(unsigned int V);
    void addToUserSourceDataContainer(unsigned int networkNodeId, const row_label_type& row_id, unsigned short int lastMileDistance);
    void addToUserDestDataContainer(unsigned int networkNodeId, const col_label_type& col_id, unsigned short int lastMileDistance);
    void addEdgeToGraph(unsigned int src, unsigned int dest, unsigned short int weight, bool isBidirectional);
    void addToCategoryMap(const col_label_type& dest_id, const std::string& category);


    // Calculations
    void compute(unsigned int numThreads);
    const std::vector<std::pair<col_label_type, unsigned short int>> getValuesBySource(row_label_type source_id, bool sort) const;
    const std::vector<std::pair<row_label_type, unsigned short int>> getValuesByDest(col_label_type dest_id, bool sort) const;
    const std::unordered_map<row_label_type, std::vector<col_label_type>> getDestsInRange(unsigned int range, int numThreads) const;
    const std::unordered_map<col_label_type, std::vector<row_label_type>> getSourcesInRange(unsigned int range, int numThreads) const;
    unsigned short int timeToNearestDestPerCategory(const row_label_type& source_id, const std::string& category) const;
    unsigned short int countDestsInRangePerCategory(const row_label_type& source_id, const std::string& category, unsigned short int range) const;
    unsigned short int timeToNearestDest(const row_label_type& source_id) const;
    unsigned short int countDestsInRange(const row_label_type& source_id, unsigned short int range) const;

    // Getters
    unsigned short int getValueById(const row_label_type& source_id, const col_label_type& dest_id) const;
    unsigned int getRows() const;
    unsigned int getCols() const;
    bool getIsSymmetric() const;
    const std::vector<unsigned short int>& getDatasetRow(unsigned int row) const;
    const std::vector<std::vector<unsigned short int>>& getDataset() const;
    const std::vector<row_label_type>& getPrimaryDatasetIds() const;
    const std::vector<col_label_type>& getSecondaryDatasetIds() const;

    // Setters
    void setRows(unsigned int rows);
    void setCols(unsigned int columns);
    void setIsSymmetric(bool isSymmetric);
    void setDataset(const std::vector<std::vector<unsigned short int>>& dataset);
    void setPrimaryDatasetIds(const std::vector<row_label_type>& primaryDatasetIds);
    void setSecondaryDatasetIds(const std::vector<col_label_type>& secondaryDatasetIds);

    // IO
    bool writeCSV(const std::string &outfile) const;
    void printDataFrame() const;

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