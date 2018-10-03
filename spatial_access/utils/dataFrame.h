#pragma once

#include <sstream>
#include <iostream>
#include <string>
#include <unordered_map>
#include <set>
#include <mutex>
#include <stdexcept>
#include <vector>

#define UNDEFINED (-1)

enum currentState
{
    UNRESERVED,
    RESERVED,
    LOADED_FROM_DISK,
    FREED,
    ERROR
};
 

/* a pandas-like dataFrame */
class dataFrame {
private:
    int * data;
    std::unordered_map <std::string, int> rows;
    std::unordered_map <std::string, int> cols;

    std::set<std::string> row_contents;
    std::set<std::string> col_contents;

    int n_rows;
    int n_cols;

    currentState state = UNRESERVED;

public:
    dataFrame(void);
    ~dataFrame(void);
    bool loadFromDisk(std::string infile);
    void insert(int val, std::string row_id, std::string col_id);
    void insertRow(std::unordered_map<std::string, int> row_data, std::string source_id);
    void insertLoc(int val, int row_loc, int col_loc);
    void reserve(std::vector<std::string> primary_ids, std::vector<std::string> secondary_ids);
    int retrieve(std::string row_id, std::string col_id);
    int retrieveSafe(std::string row_id, std::string col_id);
    void manualDelete(void);
    bool validKey(std::string row_id, std::string col_id);
};


/* void constructor */
dataFrame::dataFrame(void) {
}


bool dataFrame::loadFromDisk(std::string infile) {
    std::ifstream fileINA, fileINB;
    fileINA.open(infile);
    if (fileINA.fail()) {
        state = ERROR;
        return false;
    }

    std::string line;
    n_rows = 0, n_cols = 0;
    bool first_row = true;
    std::vector<std::string> row_labels;
    std::vector<std::string> col_labels;

    // first pass through to allocate matrix and load
    // columns/rows
    while (getline(fileINA, line)) {
        std::istringstream stream(line);
        if (first_row) {
            first_row = false;
            std::string col_id;
            n_cols = 0;
            bool first_col = true;
            while (getline(stream, col_id, ',')) {
                if (first_col) {

                    first_col = false;
                } else {
                    col_labels.push_back(col_id);
                }
            }
        } else {
            std::string row_id;
            getline(stream, row_id,',');
            row_labels.push_back(row_id);

        }
    }
    reserve(row_labels, col_labels);

    // second pass through to load up the matrix
    fileINA.close();

    fileINB.open(infile);
    if (fileINB.fail()) {
        state = ERROR;
        return false;
    }
    int row_counter = 0;
    int value;
    first_row = true;
    while (getline(fileINB, line)) {
        std::istringstream stream(line);
        if (first_row) {
            first_row = false;
            continue;
        }
        std::string row_id, input;
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
    state = LOADED_FROM_DISK;

    return true;

}


/* for use with void constructor */
void dataFrame::reserve(std::vector<std::string> primary_ids, std::vector<std::string> secondary_ids) {
    n_rows = primary_ids.size();
    n_cols = secondary_ids.size();

    std::string row_id, col_id;
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
    memset(data, UNDEFINED, sizeof(int) * n_rows * n_cols);
    state = RESERVED;
}

void dataFrame::manualDelete(void) {
    delete [] data;
}


/* destructor */

dataFrame::~dataFrame(void) {
    delete [] data;
}

/* insert a value with row_id, col_id */
void dataFrame::insertRow(std::unordered_map<std::string, int> row_data, std::string source_id) {

    for (std::pair<std::string, int> element : row_data)
    {
        data[rows[source_id] *  n_cols + cols[element.first]] = element.second;
    }
}


/* insert a value with row_id, col_id */
void dataFrame::insert(int val, std::string row_id, std::string col_id) {
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
int dataFrame::retrieve(std::string row_id, std::string col_id) {
    return data[rows[row_id] * n_cols + cols[col_id]];
}


/* check if a key pair is valid (both are in the data frame) */
bool dataFrame::validKey(std::string row_id, std::string col_id) {
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
int dataFrame::retrieveSafe(std::string row_id, std::string col_id) {
    if (!validKey(row_id, col_id)) {
        throw std::runtime_error("row or col id does not exist");
    }
    return data[rows[row_id] * n_cols + cols[col_id]];
    
}
