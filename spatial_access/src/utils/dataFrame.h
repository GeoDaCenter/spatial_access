#pragma once

#include <sstream>
#include <iostream>
#include <string>
#include <unordered_map>
#include <set>
#include <stdexcept>
#include <vector>

#include "serializer/p2p.pb.h"

#define UNDEFINED (0)

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

public:
    dataFrame(void);
    ~dataFrame(void);
    bool loadCSV(const std::string &infile);
    bool loadTMX(const std::string &infile);
    void insert(unsigned short int val, unsigned long int row_id, unsigned long int col_id);
    void insertRow(const std::unordered_map<unsigned long int, unsigned short int> &row_data, unsigned long int source_id);
    void insertLoc(unsigned short int val, int row_loc, int col_loc);
    unsigned short int retrieveLoc(int row_loc, int col_loc);
    void reserve(const std::vector<unsigned long int> &primary_ids, const std::vector<unsigned long int> &secondary_ids);
    unsigned short int retrieve(unsigned long int row_id, unsigned long int col_id);
    unsigned short int retrieveSafe(unsigned long int row_id, unsigned long int col_id);
    void manualDelete(void);
    bool validKey(unsigned long int row_id, unsigned long int col_id);
    bool writeCSV(const std::string &outfile);
    bool writeTMX(const std::string &outfile);
    void printDataFrame();
};

/* void constructor */
dataFrame::dataFrame() {
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
}

/* Manual Destructor */
void dataFrame::manualDelete(void) {
     delete [] data;
}


/* destructor (unused) */
dataFrame::~dataFrame(void) {

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
/* DOES NOT PERFORM A BOUNDS CHECK */
void dataFrame::insert(unsigned short int val, unsigned long int row_id, unsigned long int col_id) {
    data[rows[row_id] *  n_cols + cols[col_id]] = val;
}


/* insert a value with row_loc, col_loc */
/* DOES NOT PERFORM A BOUNDS CHECK */
void dataFrame::insertLoc(unsigned short int val, int row_loc, int col_loc) {
    data[row_loc *  n_cols + col_loc] = val;
}


/* retrieve a value with row_loc, col_loc */
/* DOES NOT PERFORM A BOUNDS CHECK */
unsigned short int dataFrame::retrieveLoc(int row_loc, int col_loc) {
    return data[row_loc *  n_cols + col_loc];
}


/* retrieve a value with row_id, col_id */
/* DOES NOT PERFORM A BOUNDS CHECK */
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


/* IO Methods*/

/* print the data frame to stdio */
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


/* Write the dataFrame to a .tmx (a custom binary format) */
bool dataFrame::writeTMX(const std::string &outfile)
{
    p2p::dataFrame df;
    for (auto row_label : this->row_labels)
    {
        df.add_row_label(row_label);
    }
    for (auto col_label : this->col_labels)
    {
        df.add_col_label(col_label);
    }
    for (int i = 0; i < n_rows; i++)
    {
        auto new_row = df.add_row();
        for (int j = 0; j < n_cols; j++)
        {
            new_row->add_column(this->retrieveLoc(i, j));
        }
    }
    std::fstream output(outfile, std::ios::out | std::ios::trunc | std::ios::binary);
    if (!df.SerializeToOstream(&output)) {
        std::cerr << "Failed to write .tmx" << std::endl;
        return false;
    }
    output.close();
    return true;

}


/* Read the dataFrame from a .tmx (a custom binary format) */
bool dataFrame::loadTMX(const std::string& infile)
{
    p2p::dataFrame df;
    std::fstream inputFile(infile, std::ios::in | std::ios::binary);

    if (!df.ParseFromIstream(&inputFile)) {
        std::cerr << "Failed to load .tmx" << std::endl;
        return false;
    }    
    std::vector<unsigned long int> infileRowLabels;
    std::vector<unsigned long int> infileColLabels;

    this->n_rows = df.row_label_size();
    this->n_cols = df.col_label_size();
    for (int i = 0; i < this->n_rows; i++)
    {
        infileRowLabels.push_back(df.row_label(i));
    }
    for (int j = 0; j < this->n_cols; j++)
    {
        infileColLabels.push_back(df.col_label(j));
    }
    this->reserve(infileRowLabels, infileColLabels);

    for (int i = 0; i < this->n_rows; i++)
    {
        auto matrix_row = df.row(i);
        for (int j = 0; j < this->n_cols; j++)
        {
            this->insertLoc(matrix_row.column(j), i, j);
        }
    }
    inputFile.close();
    return true;
}


/* Write the dataFrame to a .csv */
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


/* Read the dataFrame from a .csv */
bool dataFrame::loadCSV(const std::string &infile) {
    std::ifstream fileINA, fileINB;
    fileINA.open(infile);
    if (fileINA.fail()) {
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
    return true;

}
