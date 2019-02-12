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
    void insert(unsigned int item);
    unsigned int pop(bool &endNow);
    int size(void);
    bool empty(void);
};


template<class row_label_type, class col_label_type> class graphWorkerArgs;

/* A pool of worker threads to execute a job (f_in), which takes arguments (wa)*/
template<class row_label_type, class col_label_type>
class workerQueue {
private:
    std::thread *threadArray;
    int n_threads;

public:
    workerQueue(int n_threads_in);
    ~workerQueue(void);
    void startGraphWorker(void (*f_in)(graphWorkerArgs<row_label_type, col_label_type>*), graphWorkerArgs<row_label_type, col_label_type> *wa);
};


template<class row_label_type, class col_label_type>
class graphWorkerArgs {
public:
    Graph &graph;
    dataFrame<row_label_type, col_label_type> &df;
    jobQueue jq;
    userDataContainer userSourceData;
    userDataContainer userDestData;
    int numNodes;
    graphWorkerArgs(Graph &graph, userDataContainer &userSourceData,
                       userDataContainer &userDestData, 
                       int numNodes, dataFrame<row_label_type, col_label_type> &df)
    : graph(graph), df(df), jq(numNodes), userSourceData(userSourceData), userDestData(userDestData),
     numNodes(numNodes) {}
    void initialize();
};
