#pragma once

#include <sstream>
#include <iostream>
#include <string>
#include <unordered_map>
#include <set>
#include <stdexcept>
#include <vector>

#define UNDEFINED (0)

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
    unsigned short int * data;
    std::unordered_map <unsigned long int, int> rows;
    std::unordered_map <unsigned long int, int> cols;

    std::vector<unsigned long int> row_labels;
    std::vector<unsigned long int> col_labels;
    std::set<unsigned long int> row_contents;
    std::set<unsigned long int> col_contents;

    int n_rows;
    int n_cols;

    currentState state = UNRESERVED;

public:
    dataFrame(void);
    ~dataFrame(void);
    bool loadFromDisk(const std::string &infile);
    void insert(unsigned short int val, unsigned long int row_id, unsigned long int col_id);
    void insertRow(const std::unordered_map<unsigned long int, unsigned short int> &row_data, unsigned long int source_id);
    void insertLoc(unsigned short int val, int row_loc, int col_loc);
    void reserve(const std::vector<unsigned long int> &primary_ids, const std::vector<unsigned long int> &secondary_ids);
    unsigned short int retrieve(unsigned long int row_id, unsigned long int col_id);
    unsigned short int retrieveSafe(unsigned long int row_id, unsigned long int col_id);
    void manualDelete(void);
    bool validKey(unsigned long int row_id, unsigned long int col_id);
    bool writeCSV(const std::string &outfile);
    void printDataFrame();
};

bool dataFrame::writeCSV(const std::string &outfile)
{
    std::ofstream Ofile;
    Ofile.open(outfile);
    if (Ofile.fail()) {
        throw std::runtime_error("Could not open output file");
    }
    Ofile << ",";
    for (auto col_label : col_labels)
    {
        Ofile << col_label << ",";
    }
    Ofile << std::endl;
    for (int row_index = 0; row_index < n_rows; row_index++)
    {
        Ofile << row_labels[row_index] << ",";
        for (int col_index = 0; col_index < n_cols; col_index++)
        {
            Ofile << data[row_index * n_cols + col_index] << ","; 
        }
        Ofile << std::endl;
    }



    Ofile << std::endl;
    Ofile.close();
    return true;
} 

void dataFrame::printDataFrame()
{

    std::cout << ",";
    for (auto col_label : col_labels)
    {
        std::cout << col_label << ",";
    }
    std::cout << std::endl;
    for (int row_index = 0; row_index < n_rows; row_index++)
    {
        std::cout << row_labels[row_index] << ",";
        for (int col_index = 0; col_index < n_cols; col_index++)
        {
            std::cout << data[row_index * n_cols + col_index] << ","; 
        }
        std::cout << std::endl;
    }

} 


/* void constructor */
dataFrame::dataFrame() {
}



void printArray(const std::vector<unsigned long int> &data)
{
    for (auto element : data)
    {
        std::cout << element << std::endl;
    }
}


bool dataFrame::loadFromDisk(const std::string &infile) {
    std::ifstream fileINA, fileINB;
    fileINA.open(infile);
    if (fileINA.fail()) {
        state = ERROR;
        return false;
    }
    std::vector<unsigned long int> infileColLabels;
    std::vector<unsigned long int> infileRowLabels;
    std::string line;
    n_rows = 0, n_cols = 0;
    bool first_row = true;

    // first pass through to allocate matrix and load
    // columns/rows
    while (getline(fileINA, line)) {
        std::istringstream stream(line);
        if (first_row) {
            first_row = false;
            std::string tmp_col_id;
            unsigned long int col_id;
            n_cols = 0;
            bool first_col = true;
            while (getline(stream, tmp_col_id, ',')) {
                if (first_col) {

                    first_col = false;
                } else {
                    col_id = stoul(tmp_col_id);
                    infileColLabels.push_back(col_id);
                }
            }
        } else {
            std::string tmp_row_id;
            unsigned long int row_id;
            getline(stream, tmp_row_id,',');
            if (!tmp_row_id.size())
            {
                break;
            }
            row_id = stoul(tmp_row_id);
            infileRowLabels.push_back(row_id);
            
        }
    }
    reserve(infileRowLabels, infileColLabels);

    fileINA.close();

    fileINB.open(infile);
    if (fileINB.fail()) {
        state = ERROR;
        return false;
    }
    int row_counter = 0;
    unsigned short int value;
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
                row_id = stoul(input);
            } else {
                value = stoul(input);
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

// use when creating a new data frame
void dataFrame::reserve(const std::vector<unsigned long int> &primary_ids, const std::vector<unsigned long int> &secondary_ids) {
    n_rows = primary_ids.size();
    n_cols = secondary_ids.size();

    unsigned long int row_id, col_id;
    for (int row_idx = 0; row_idx < n_rows; row_idx++) {
        row_id = primary_ids.at(row_idx);
        rows[row_id] = row_idx;
        row_contents.insert(row_id);
        row_labels.push_back(row_id);
    }

    for (int col_idx = 0; col_idx < n_cols; col_idx++) {
        col_id = secondary_ids.at(col_idx);
        cols[col_id] = col_idx;
        col_contents.insert(col_id);
        col_labels.push_back(col_id);
    }

    data = new unsigned short int[n_rows * n_cols];
    memset(data, UNDEFINED, sizeof(unsigned short int) * n_rows * n_cols);
    state = RESERVED;
}

void dataFrame::manualDelete(void) {
     delete [] data;
}


/* destructor */

dataFrame::~dataFrame(void) {
    // delete [] data;
}

/* insert a value with row_id, col_id */
void dataFrame::insertRow(const std::unordered_map<unsigned long int, unsigned short int> &row_data, unsigned long int source_id) {
    auto rowNum = rows[source_id];
    for (std::pair<unsigned long int, unsigned short int> element : row_data)
    {
        data[rowNum *  n_cols + cols[element.first]] = element.second;
    }
}


/* insert a value with row_id, col_id */
void dataFrame::insert(unsigned short int val, unsigned long int row_id, unsigned long int col_id) {
    data[rows[row_id] *  n_cols + cols[col_id]] = val;
}


/* insert a value with row_loc, col_loc */
void dataFrame::insertLoc(unsigned short int val, int row_loc, int col_loc) {
    data[row_loc *  n_cols + col_loc] = val;
}

/* retrieve a value with row_id, col_id */
/* warning: this method is UNSAFE. Results are undefined*/
/* if keys are not present in dataframe */
/* for safe retrieval, use retrieveSafe */
unsigned short int dataFrame::retrieve(unsigned long int row_id, unsigned long int col_id) {
    return data[rows[row_id] * n_cols + cols[col_id]];
}


/* check if a key pair is valid (both are in the data frame) */
bool dataFrame::validKey(unsigned long int row_id, unsigned long int col_id) {
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
unsigned short int dataFrame::retrieveSafe(unsigned long int row_id, unsigned long int col_id) {
    if (!validKey(row_id, col_id)) {
        throw std::runtime_error("row or col id does not exist");
    }
    return data[rows[row_id] * n_cols + cols[col_id]];
    
}
