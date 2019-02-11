#pragma once

#include "threadUtilities.h"
#include "dataFrame.h"
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

void calculateValuesForOneIndex(unsigned long int index, rangeWorkerArgs *wa);


namespace lmnoel {
class transitMatrix {
public:
    // Constructors
    transitMatrix(int V);
    transitMatrix(void);


    typedef unsigned long int label;
    typedef unsigned short int value;
    dataFrame df;
    userDataContainer userSourceDataContainer;
    userDataContainer userDestDataContainer;
    Graph graph;
    int numNodes;
    void addToUserSourceDataContainerInt(int networkNodeId, unsigned long int id, int lastMileDistance, bool isBidirectional);
    void addToUserDestDataContainerInt(int networkNodeId, unsigned long int id, int lastMileDistance);
    void addToUserSourceDataContainerString(int networkNodeId, const std::string& id, int lastMileDistance, bool isBidirectional);
    void addToUserDestDataContainerString(int networkNodeId, const std::string& id, int lastMileDistance);
    void addEdgeToGraph(int src, int dest, int weight, bool isBidirectional);
    void compute(int numThreads);
    int get(unsigned long int source, unsigned long intdest) const;
    const std::vector<std::pair<unsigned long int, unsigned short int>> getValuesBySource(unsigned long int source_id, bool sort);
    const std::vector<std::pair<unsigned long int, unsigned short int>> getValuesByDest(unsigned long int dest_id, bool sort);

    void prepareDataFrame();
    bool writeCSV(const std::string &outfile);
    bool writeTMX(const std::string &outfile);
    void printDataFrame() const;
    void calculateSourcesInRange(unsigned int threshold, int numThreads);
    void calculateDestsInRange(unsigned int threshold, int numThreads);
    const std::unordered_map<unsigned long int, std::vector<unsigned long int>>& getDestsInRange(unsigned int range, int numThreads);
    const std::unordered_map<unsigned long int, std::vector<unsigned long int>>& getSourcesInRange(unsigned int range, int numThreads);
    const std::unordered_map<std::string, unsigned long int> getUserRowIdCache();
    const std::unordered_map<std::string, unsigned long int> getUserColIdCache();
    void addToCategoryMap(unsigned long int dest_id, const std::string& category);
    unsigned short int timeToNearestDestPerCategory(unsigned long int source_id, const std::string& category) const;
    unsigned short int countDestsInRangePerCategory(unsigned long int source_id, const std::string& category, unsigned short int range) const;
    unsigned short int timeToNearestDest(unsigned long int source_id) const;
    unsigned short int countDestsInRange(unsigned long int source_id, unsigned short int range) const;


    // Getters
    const std::string& getDatasetName();
    unsigned int getRows();
    unsigned int getColumns();
    bool getIsSymmetric();
    const std::string& getPrimaryDatasetIdsName();
    const std::string& getSecondaryDatasetIdsName();
    std::vector<std::vector<unsigned short int>> getDataset();
    const std::vector<std::string>& getPrimaryDatasetStringIds();
    const std::vector<std::string>& getSecondaryDatasetStringIds();
    const std::vector<unsigned long int>& getPrimaryDatasetIntIds();
    const std::vector<unsigned long int>& getSecondaryDatasetIntIds();

    // Setters
    void setDatasetName(const std::string& datasetName);
    void setRows(unsigned int rows);
    void setColumns(unsigned int columns);
    void setIsSymmetric(bool isSymmetric);
    void setPrimaryDatasetIdsName(const std::string& primaryDatasetIdsName);
    void setSecondaryDatasetIdsName(const std::string& secondaryDatasetIdsName);
    void setDataset(std::vector<std::vector<unsigned short int>> dataset);
    void setPrimaryDatasetStringIds(const std::vector<std::string>& primaryDatasetIds);
    void setSecondaryDatasetStringIds(const std::vector<std::string>& primaryDatasetIds);
    void setPrimaryDatasetIntIds(const std::vector<unsigned long int>& primaryDatasetIds);
    void setSecondaryDatasetIntIds(const std::vector<unsigned long int>& primaryDatasetIds);

private:
    std::unordered_map<unsigned long int, std::vector<unsigned long int>> sourcesInRange;
    std::unordered_map<unsigned long int, std::vector<unsigned long int>> destsInRange;
    bool primaryDatasetIdsIsString;
    bool secondaryDatasetIdsIsString;
    unsigned int sourcesInRangeThreshold;
    unsigned int destsInRangeThreshold;
    std::unordered_map<std::string, std::vector<unsigned long int>> categoryToDestMap;
    std::string datasetName;
    std::string primaryDatasetIdsName;
    std::string secondaryDatasetIdsName;
    std::unordered_map<unsigned long int, unsigned long int> primaryDatasetIntIdsToLoc;
    std::unordered_map<unsigned long int, unsigned long int> secondaryDatasetIntIdsToLoc;
    std::unordered_map<std::string, unsigned long int> primaryDatasetStringIdsToLoc;
    std::unordered_map<std::string, unsigned long int> secondaryDatasetStringIdsToLoc;

    std::vector<std::string> primaryDatasetIdsString;
    std::vector<std::string> secondaryDatasetIdsString;
    std::vector<unsigned long int> primaryDatasetIdsInt;
    std::vector<unsigned long int> secondaryDatasetIdsInt;
};

} // namespace lnoel