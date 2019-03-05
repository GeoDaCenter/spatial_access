// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#include <iostream>
#include <algorithm>

#include "threadUtilities.h"
#include "Graph.h"
#include "userDataContainer.h"
#include "dataFrame.h"

/* initialize jobQueue, reserving size for known inputs*/



/* insert to the jobQueue */
void jobQueue::insert(unsigned long int item) {
    data.push(item);
}


/* pop from the jobQueue.*/
unsigned long int jobQueue::pop(bool &endNow) {
    unsigned long int res = 0;
    std::lock_guard<std::mutex> guard(lock);
    if (!data.empty()) {
        res = data.front();
        data.pop();

    } else {
        endNow = false;
    }
    return res;
}

/* return true if jobQueue is empty */
bool jobQueue::empty() const
{
    bool res;
    std::lock_guard<std::mutex> guard(lock);
    res = data.empty();
    return res;
}

/*initialize workerQueue */
template<class row_label_type, class col_label_type>
workerQueue<row_label_type, col_label_type>::workerQueue(unsigned int numThreads, void (*f_in)(graphWorkerArgs<row_label_type, col_label_type>*), graphWorkerArgs<row_label_type, col_label_type> *wa)
{
    for (unsigned long int i = 0; i < numThreads; i++)
    {
        this->threads.push_back(std::thread(f_in, wa));
    }
}

void do_join(std::thread &t)
{
    t.join();
}

/* start the workerQueue */
template<class row_label_type, class col_label_type>
void workerQueue<row_label_type, col_label_type>::startGraphWorker()
{
   std::for_each(this->threads.begin(), this->threads.end(), do_join);
}


template <class row_label_type, class col_label_type>
void graphWorkerArgs<row_label_type, col_label_type>::initialize()
{
    //initialize job queue
    for (auto i : userSourceData.retrieveUniqueNetworkNodeIds()) {
        jq.insert(i);
    }
}
