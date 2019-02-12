#pragma once

#include <thread>
#include <mutex>
#include <vector>
#include <memory>

#include "Graph.h"
#include "userDataContainer.h"
#include "dataFrame.h"

/* jobQueue: a thread-safe queue for dispensing integer jobs*/
class jobQueue {
private:
    std::vector <unsigned int> data;
    std::mutex lock;
public:
    jobQueue(int size_in);
    jobQueue(void);
    ~jobQueue(void);
    void insert(unsigned int item);
    unsigned int pop(bool &endNow);
    int size(void);
    bool empty(void);
};


typedef class graphWorkerArgs graphWorkerArgs;

typedef class rangeWorkerArgs rangeWorkerArgs;


/* A pool of worker threads to execute a job (f_in), which takes arguments (wa)*/
class workerQueue {
private:
    std::thread *threadArray;
    int n_threads;

public:
    workerQueue(int n_threads_in);
    ~workerQueue(void);
    void startGraphWorker(void (*f_in)(graphWorkerArgs*), graphWorkerArgs *wa);
    void startRangeWorker(void (*f_in)(rangeWorkerArgs*), rangeWorkerArgs *wa);
};



class graphWorkerArgs {
public:
    Graph &graph;
    dataFrame &df;
    jobQueue jq;
    userDataContainer userSourceData;
    userDataContainer userDestData;
    int numNodes;
    graphWorkerArgs(Graph &graph, userDataContainer &userSourceData,
                       userDataContainer &userDestData, 
                       int numNodes, dataFrame &df) 
    : graph(graph), df(df), userSourceData(userSourceData), userDestData(userDestData),
     numNodes(numNodes) {}
    ~graphWorkerArgs(void);
    void initialize();
};

class rangeWorkerArgs {
public:
    bool isDestsInRange;
    jobQueue jq;
    dataFrame &df;
    int threshold;
    std::unordered_map<unsigned long int, std::vector<unsigned long int>> &rows;
    std::unordered_map<unsigned long int, std::vector<unsigned long int>> &cols;
    std::mutex write_lock;
    rangeWorkerArgs(bool isDestsInRange, dataFrame &df, int threshold, 
                    std::unordered_map<unsigned long int, std::vector<unsigned long int>> &rows,
                    std::unordered_map<unsigned long int, std::vector<unsigned long int>> &cols) 
                        : isDestsInRange(isDestsInRange), df(df), threshold(threshold), 
                            rows(rows), cols(cols) {}
    
    ~rangeWorkerArgs(void);
    void initialize();
};