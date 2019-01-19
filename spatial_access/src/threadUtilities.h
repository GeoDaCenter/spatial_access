#pragma once

#include <thread>
#include <mutex>
#include <vector>

#include "Graph.h"
#include "userDataContainer.h"
#include "dataFrame.h"

/* jobQueue: a thread-safe queue for dispensing integer jobs*/
class jobQueue {
private:
    std::vector <int> data;
    std::mutex lock;
public:
    jobQueue(int size_in);
    jobQueue(void);
    ~jobQueue(void);
    void insert(int item);
    int pop(void);
    int size(void);
    bool empty(void);
};


typedef class graphWorkerArgs graphWorkerArgs;


/* A pool of worker threads to execute a job (f_in), which takes arguments (wa)*/
class workerQueue {
private:
    std::thread *threadArray;
    int n_threads;

public:
    workerQueue(int n_threads_in);
    ~workerQueue(void);
    void startGraphWorker(void (*f_in)(graphWorkerArgs*), graphWorkerArgs *wa);
};



class graphWorkerArgs {
public:
    Graph &graph;
    dataFrame &df;
    jobQueue jq;
    userDataContainer userSourceData;
    userDataContainer userDestData;
    int numNodes;
    std:: mutex writeLock;
    graphWorkerArgs(Graph &graph, userDataContainer &userSourceData,
                       userDataContainer &userDestData, 
                       int numNodes, dataFrame &df) 
    : graph(graph), df(df), userSourceData(userSourceData), userDestData(userDestData),
     numNodes(numNodes) {}
    ~graphWorkerArgs(void);
    void initialize();
};