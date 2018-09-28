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
#include <mutex>

using namespace std;

/* represent and write a 2d json file */
class json_2d {
public:
    unordered_map<string, int>* data;
    string* map_ids;
    mutex lock;
    int n_entries;
    bool initialized = false;
    void init(int n_entries);
    ~json_2d(void);
    void insert(string map_id, unordered_map<string, int> in);
    void write(string filename);
};


/*initializer*/
void json_2d::init(int n_entries_in) {
    n_entries = 0;
    initialized = true;
    data = new unordered_map<string, int>[n_entries_in];
    map_ids = new string[n_entries_in];
}


/*destructor*/
json_2d::~json_2d(void) {
    if (initialized) {
        delete [] data;
        delete [] map_ids; 
    }
}


/* write the object to file*/
void json_2d::write(string outfile) {
    ofstream Ofile;
    Ofile.open(outfile);
    Ofile << "{";
    unordered_map<string, int>::iterator itr;
    unordered_map<string, int> map;
    string map_id;
    for (int i = 0; i < n_entries; i++) {
        map = data[i];
        map_id = map_ids[i];
        Ofile << "\"" << map_id << "\": ";
        Ofile << "{";
        bool first = true;
        for (itr = map.begin(); itr != map.end(); itr++) {
            if (first) {
                first = false;
            } else {
                Ofile << ",";
            }
            Ofile << "\"" << itr->first << "\"" << ": " << itr->second;
        }
        if (i != n_entries - 1) {
            Ofile << "},";
        } else {
            Ofile << "}";
        }

    }
    Ofile << "}" << endl;
}


/*insert a subset of the hierarchy*/
void json_2d::insert(string map_id, unordered_map<string, int> map) {
    lock.lock();
    data[n_entries] = map;
    map_ids[n_entries] = map_id;
    n_entries++;
    lock.unlock();
}


/* EXAMPLE USAGE: */

/*
void json_example() {
    unordered_map<string, int> um1;
    unordered_map<string, int> um2;
    um1["index_a"] = 123;
    um1["index_b"] = 124;

    um2["index_c"] = 223;
    um2["index_d"] = 224;

    json_2d val;
    val.init(2);
    val.insert("map1", um1);
    val.insert("map2", um2);

    val.write("example_json.json");

}
*/
