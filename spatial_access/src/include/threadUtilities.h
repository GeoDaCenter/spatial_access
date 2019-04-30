// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#pragma once

#include <thread>
#include <mutex>
#include <vector>
#include <queue>
#include <iostream>
#include <algorithm>

#include "Graph.h"
#include "userDataContainer.h"
#include "dataFrame.h"

/* jobQueue: a thread-safe queue for dispensing integer jobs*/
class jobQueue {
private:
    std::queue <unsigned long int> data;
    mutable std::mutex lock;
public:
    jobQueue() = default;
    void insert(unsigned long int item);
    unsigned long int pop(bool &endNow);
    bool empty() const;
};

void do_join(std::thread &t);

template<class row_label_type, class col_label_type, class value_type> class graphWorkerArgs;

/* A pool of worker threads to execute a job (f_in), which takes arguments (worker_args)*/
template<class row_label_type, class col_label_type, class value_type>
class workerQueue {
private:
    std::vector<std::thread> threads;
public:
    workerQueue(unsigned int numThreads,
            void (*f_in)(graphWorkerArgs<row_label_type, col_label_type, value_type>&),
            graphWorkerArgs<row_label_type, col_label_type, value_type> &worker_args)
    {

        for (unsigned long int i = 0; i < numThreads; i++)
        {
            this->threads.push_back(std::thread(f_in, std::ref(worker_args)));
        }

    }
    void startGraphWorker()
    {
        std::for_each(this->threads.begin(), this->threads.end(), do_join);
    }

};


template<class row_label_type, class col_label_type, class value_type>
class graphWorkerArgs {
public:
    Graph<value_type> &graph;
    dataFrame<row_label_type, col_label_type, value_type> &df;
    jobQueue jq;
    userDataContainer<value_type> userSourceData;
    userDataContainer<value_type> userDestData;
    graphWorkerArgs(Graph<value_type> &graph, userDataContainer<value_type> &userSourceData,
                       userDataContainer<value_type> &userDestData,
                       dataFrame<row_label_type, col_label_type, value_type> &df)
    : graph(graph), df(df), jq(), userSourceData(userSourceData), userDestData(userDestData) {}
    void initialize()
    {
        //initialize job queue
        for (auto i : userSourceData.retrieveUniqueNetworkNodeIds()) {
            jq.insert(i);
        }
    }
};
