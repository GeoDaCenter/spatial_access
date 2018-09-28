/* Written by Logan Noel for the Center for Spatial Data Science (2018)
 *
 * See repository for license details.
 *
 */

#include <iostream>
#include <thread>
#include <mutex>
#include <vector>

using namespace std;

/* jobQueue: a thread-safe queue for dispensing integer jobs*/
class jobQueue {
private:
    vector <int> data;
    mutex lock;
public:
    jobQueue(int size_in);
    jobQueue(void);
    ~jobQueue(void);
    void insert(int item);
    int pop(void);
    int size(void);
    bool empty(void);
};


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
void jobQueue::insert(int item) {
    lock.lock();
    data.insert(data.end(), item);
    lock.unlock();
}


/* pop from the jobQueue. Returns -1 if Queue is empty*/
int jobQueue::pop(void) {
    int res;
    lock.lock();
    if (!data.empty()) {
        res = data.front();
        data.erase(data.begin());
    } else {
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

typedef class workerArgs workerArgs;


/* A pool of worker threads to execute a job (f_in), which takes arguments (wa)*/
class workerQueue {
private:
    thread *threadArray;
    int n_threads;

public:
    workerQueue(int n_threads_in);
    ~workerQueue(void);
    void start(void (*f_in)(workerArgs*), workerArgs *wa);
};


/*initialize workerQueue */
workerQueue::workerQueue(int n_threads_in) {
    threadArray = new thread[n_threads_in];
    n_threads = n_threads_in;

}


/* start the workerQueue */
void workerQueue::start(void (*f_in)(workerArgs*), workerArgs *wa) {
    for (int i = 0; i < n_threads; i++) {
        threadArray[i] = thread(f_in, wa);
    }

    for (int j = 0; j < n_threads; j++) {
        threadArray[j].join();
    }
}


/* delete the workerQueue */
workerQueue::~workerQueue(void) {
    delete [] threadArray;
}


/* EXAMPLE USAGE: */

/*
class WorkerArgs {
public:
    vector<int> data;
    jobQueue jq;
};

void example_f(int item, WorkerArgs *wa) {
    cout << "item: " << item << endl;

    //do work
    wa->data.push_back(item);

}

//assign jobs to worker threads
void example_fx(WorkerArgs *wa) {
    int item;
    while (!jq->empty()) {
        item = jq->pop();
        if (item < 0) {
            break;
        }
        example_f(item, wa);
    }
}

void tq_test(void) {
    workerArgs *wa;

    //insert 4 jobs
    for (int i = 0; i < 4; i++) {
        wa->jq.insert(i);
    }

    //use 2 threads
    workerQueue wq(2);
    wq.start(example_fx, wa);

}
*/
