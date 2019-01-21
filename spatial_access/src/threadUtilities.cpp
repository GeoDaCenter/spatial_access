#include <iostream>

#include "threadUtilities.h"
#include "Graph.h"
#include "userDataContainer.h"
#include "dataFrame.h"

/* initialize jobQueue, reserving size for known inputs*/
jobQueue::jobQueue(int size_in) {
    data.reserve(size_in);
}


/* initialize jobQueue (unknown number of inputs */
jobQueue::jobQueue(void) {
}


/* free the jobQueue */
jobQueue::~jobQueue(void) {
}


/* insert to the jobQueue */
void jobQueue::insert(unsigned long int item) {
    data.insert(data.end(), item);
}


/* pop from the jobQueue. Returns -1 if Queue is empty*/
unsigned long int jobQueue::pop(bool &endNow) {
    unsigned long int res;
    lock.lock();
    if (!data.empty()) {
        res = data.front();
        data.erase(data.begin());
    } else {
        endNow = false;
        res = -1;
    }
    lock.unlock();
    return res;
}


/* Get size of jobQueue */
int jobQueue::size(void) {
    int res;
    lock.lock();
    res = data.size();
    lock.unlock();
    return res;
}


/* return true if jobQueue is empty */
bool jobQueue::empty(void) {
    bool res;
    lock.lock();
    res = data.empty();
    lock.unlock();
    return res;
}

/*initialize workerQueue */
workerQueue::workerQueue(int n_threads_in) {
    threadArray = new std::thread[n_threads_in];
    n_threads = n_threads_in;

}


/* start the workerQueue */
void workerQueue::startGraphWorker(void (*f_in)(graphWorkerArgs*), graphWorkerArgs *wa) {
    for (int i = 0; i < n_threads; i++) {
        threadArray[i] = std::thread(f_in, wa);
    }

    for (int j = 0; j < n_threads; j++) {
        threadArray[j].join();
    }
}

/* start the workerQueue */
void workerQueue::startRangeWorker(void (*f_in)(rangeWorkerArgs*), rangeWorkerArgs *wa) {
    for (int i = 0; i < n_threads; i++) {
        threadArray[i] = std::thread(f_in, wa);
    }

    for (int j = 0; j < n_threads; j++) {
        threadArray[j].join();
    }
}

/* delete the workerQueue */
workerQueue::~workerQueue(void) {
    delete [] threadArray;
}


void graphWorkerArgs::initialize()
{
    //initialize job queue
    for (auto i : userSourceData.retrieveUniqueNetworkNodeIds()) {
        jq.insert(i);
    }
}

/* wa destructor */
graphWorkerArgs::~graphWorkerArgs(void) 
{

}

void rangeWorkerArgs::initialize()
{
    //initialize job queue
    for (auto i : df.metaData.row_label_int()) 
    {
        jq.insert(i);
    }

    // initialize column_locks;
    for (auto col_label : df.metaData.col_label_int())
    {
        column_locks.emplace(col_label, new std::mutex);
    }
}


/* wa destructor */
rangeWorkerArgs::~rangeWorkerArgs(void) 
{
// initialize column_locks;
    for (auto col_label : df.metaData.col_label_int())
    {
        // column_locks.erase(col_label);
    }
}