/* Written by Logan Noel for the Center for Spatial Data Science (2018)
 *
 * See repository for license details.
 *
 */

#include <sstream>
#include <iostream>
#include <fstream>
#include <string>
#include <unordered_map>
#include <tuple>
#include <vector>

using namespace std;

typedef vector< tuple<string,int> > tuple_list;


/* limitedQueue: a class to retain only the (key, value)
 * pairs with the n lowest values.
 */
class limitedQueue {
public:
    tuple_list data;
    int index_of_max;
    int max_in_queue;
    int n_items;
    int max_items;
    bool first;

    limitedQueue(int max_items);
    ~limitedQueue(void);
    void put(string key, int value);
    unordered_map<string, int> get(void);

};


/* initializer */
limitedQueue::limitedQueue(int max_items_in) {
    index_of_max = 0;
    max_in_queue = 0;
    n_items = 0;
    first = true;
    max_items = max_items_in;

}

/* destructor */
limitedQueue::~limitedQueue(void) {

}

/* add a new (key, value) pair to the lq */
void limitedQueue::put(string key, int value) {
    // if lq is already full and value is larger than max in lq, reject
    if ((n_items >= max_items) && (value > max_in_queue)) {
        return;
    } else if (n_items < max_items) {
        //if lq is not yet full, add the new pair
        data.push_back(make_tuple(key, value));
        n_items++;
        if (value > max_in_queue) {
            max_in_queue = value;
            index_of_max = n_items - 1;
        }
    } else if (value < max_in_queue) {
        //if lq is full but value is better than existing worse, add it
        //and remove previous worst
        data.erase(data.begin() + index_of_max);
        data.push_back(make_tuple(key, value));
        max_in_queue = 0;
        for (int i = 0; i < n_items; i++) {
            int cur_val = std::get<1>(data[i]);
            if (cur_val > max_in_queue) {
                max_in_queue = cur_val;
                index_of_max = i;
            }
        }
    } else {
        return;
    }
}


/* get the best key, value pairs */
unordered_map<string, int> limitedQueue::get(void) {
    unordered_map <string, int> map;
    for (int i = 0; i < n_items; i++) {
            int val = std::get<1>(data[i]);
            string key = std::get<0>(data[i]);
            map[key] = val;
        }

    return map;
}


/*print the contents of a hashtable */
void printContents(unordered_map <string, int> map) {
   unordered_map<string, int>::iterator itr;

    for (itr = map.begin(); itr != map.end(); itr++) {
        cout << itr->first << ":" << itr->second << ",";
    }
    cout << endl;
}

/* EXAMPLE USAGE: */

/*
int example_lq() {
    limitedQueue lq(3);
    lq.put("a", 1);
    lq.put("b", 2);
    lq.put("c", 3);
    lq.put("e", 4);
    lq.put("f", 2);

    unordered_map <string, int> map = lq.get();
    printContents(map);
    return 0;
}
*/