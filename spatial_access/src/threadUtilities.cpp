// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#include "include/threadUtilities.h"


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

void do_join(std::thread &t)
{
    t.join();
}