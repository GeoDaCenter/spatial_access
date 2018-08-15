#include <sstream>
#include <iostream>
#include <string>
#include <unordered_map>
#include <set>
#include <mutex>
#include <stdexcept>
#include <vector>

using namespace std;

#define UNDEFINED (-1)
 

/* a pandas-like dataFrame */
class dataFrame {
private:
    int * data;
    unordered_map <string, int> rows;
    unordered_map <string, int> cols;

    set<string> row_contents;
    set<string> col_contents;

    int n_rows;
    int n_cols;

    bool freed;

public:
    dataFrame(void);
    ~dataFrame(void);
    bool loadFromDisk(string infile);
    void insert(int val, string row_id, string col_id);
    void insertRow(unordered_map<string, int> row_data, string source_id);
    void insertLoc(int val, int row_loc, int col_loc);
    void reserve(vector<string> primary_ids, vector<string> secondary_ids);
    int retrieve(string row_id, string col_id);
    int retrieveSafe(string row_id, string col_id);
    void manualDelete(void);
    bool validKey(string row_id, string col_id);
};


/* void constructor */
dataFrame::dataFrame(void) {
    freed = false;
}


bool dataFrame::loadFromDisk(string infile) {
    ifstream fileINA, fileINB;
    fileINA.open(infile);
    if (fileINA.fail()) {
        return false;
    }

    string line;
    n_rows = 0, n_cols = 0;
    bool first_row = true;
    while (getline(fileINA, line)) {
        istringstream stream(line);
        if (first_row) {
            first_row = false;
            string col_id;
            n_cols = 0;
            bool first_col = true;
            while (getline(stream, col_id, ',')) {
                if (first_col) {

                    first_col = false;
                } else {
                    cols[col_id] = n_cols;
                    col_contents.insert(col_id);
                    n_cols++;
                }
            }
        } else {
            string row_id;
            getline(stream, row_id,',');
            rows[row_id] = n_rows;
            row_contents.insert(row_id);
            n_rows++;

        }
    }

    data = new int [n_rows * n_cols];
    memset(data, 0, sizeof(int) * n_rows * n_cols);

    //have to do a second read through because c++ doesn't have realloc
    fileINA.close();

    fileINB.open(infile);
    if (fileINB.fail()) {
        return false;
    }
    int row_counter = 0;
    int value;
    first_row = true;
    while (getline(fileINB, line)) {
        istringstream stream(line);
        if (first_row) {
            first_row = false;
            continue;
        }
        string row_id, input;
        int col_counter = 0;
        bool first_col = true;
        while (getline(stream, input, ',')) {
            if (first_col) {
                first_col = false;
                row_id = input;
            } else {
                value = stoull(input);
                insertLoc(value, row_counter, col_counter);
                col_counter++;
            }
        }
        row_counter++;
    }
    fileINB.close();


    return true;


}


/* for use with void constructor */
void dataFrame::reserve(vector<string> primary_ids, vector<string> secondary_ids) {
    n_rows = primary_ids.size();
    n_cols = secondary_ids.size();

    string row_id, col_id;
    for (int row_idx = 0; row_idx < n_rows; row_idx++) {
        row_id = primary_ids.at(row_idx);
        rows[row_id] = row_idx;
        row_contents.insert(row_id);
    }

    for (int col_idx = 0; col_idx < n_cols; col_idx++) {
        col_id = secondary_ids.at(col_idx);
        cols[col_id] = col_idx;
        col_contents.insert(col_id);
    }


    data = new int[n_rows * n_cols];
    memset(data, 0, sizeof(int) * n_rows * n_cols);
}

void dataFrame::manualDelete(void) {
    delete [] data;
}


/* destructor */

dataFrame::~dataFrame(void) {
    if (freed) {
        return;
    }
    freed = true;
    //delete [] data;
}

/* insert a value with row_id, col_id */
void dataFrame::insertRow(unordered_map<string, int> row_data, string source_id) {

    for (pair<string, int> element : row_data)
    {
        data[rows[source_id] *  n_cols + cols[element.first]] = element.second;
    }
}


/* insert a value with row_id, col_id */
void dataFrame::insert(int val, string row_id, string col_id) {
    data[rows[row_id] *  n_cols + cols[col_id]] = val;
}


/* insert a value with row_loc, col_loc */
void dataFrame::insertLoc(int val, int row_loc, int col_loc) {
    data[row_loc *  n_cols + col_loc] = val;
}

/* retrieve a value with row_id, col_id */
/* warning: this method is UNSAFE. Results are undefined*/
/* if keys are not present in dataframe */
/* for safe retrieval, use retrieveSafe */
int dataFrame::retrieve(string row_id, string col_id) {
    return data[rows[row_id] * n_cols + cols[col_id]];
}


/* check if a key pair is valid (both are in the data frame) */
bool dataFrame::validKey(string row_id, string col_id) {
    if (row_contents.find(row_id) == row_contents.end()) {
        return false;
    }
    if (col_contents.find(col_id) == col_contents.end()) {
        return false;
    }

    return true;
}

/* retrieve a value with row_id, col_id */
/* this method is SAFE, and will throw an error*/
/* if keys are undefined*/
int dataFrame::retrieveSafe(string row_id, string col_id) {
    if (!validKey(row_id, col_id)) {
        throw runtime_error("row or col id does not exist");
    }
    return data[rows[row_id] * n_cols + cols[col_id]];
    
}
