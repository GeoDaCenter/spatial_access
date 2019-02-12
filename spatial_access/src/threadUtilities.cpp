#include <iostream>

#include "threadUtilities.h"
#include "Graph.h"
#include "userDataContainer.h"
#include "dataFrame.h"

/* initialize jobQueue, reserving size for known inputs*/

jobQueue::jobQueue(int size_in) {
    data.reserve(size_in);
}


/* insert to the jobQueue */
void jobQueue::insert(unsigned int item) {
    data.insert(data.end(), item);
}


/* pop from the jobQueue.*/
unsigned int jobQueue::pop(bool &endNow) {
    unsigned int res;
    lock.lock();
    if (!data.empty()) {
        res = data.front();
        data.erase(data.begin());
    } else {
        endNow = false;
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
template<class row_label_type, class col_label_type>
workerQueue<row_label_type, col_label_type>::workerQueue(int n_threads_in) {
    threadArray = new std::thread[n_threads_in];
    n_threads = n_threads_in;

}


/* start the workerQueue */
template<class row_label_type, class col_label_type>
void workerQueue<row_label_type, col_label_type>::startGraphWorker(void (*f_in)(graphWorkerArgs<row_label_type, col_label_type>*), graphWorkerArgs<row_label_type, col_label_type> *wa) {
    for (int i = 0; i < n_threads; i++) {
        threadArray[i] = std::thread(f_in, wa);
    }

    for (int j = 0; j < n_threads; j++) {
        threadArray[j].join();
    }
}


/* delete the workerQueue */
template<class row_label_type, class col_label_type>
workerQueue<row_label_type, col_label_type>::~workerQueue(void) {
    delete [] threadArray;
}

template <class row_label_type, class col_label_type>
void graphWorkerArgs<row_label_type, col_label_type>::initialize()
{
    //initialize job queue
    for (auto i : userSourceData.retrieveUniqueNetworkNodeIds()) {
        jq.insert(i);
    }
}
