#pragma once

#include <sstream>
#include <iostream>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <stdexcept>
#include <vector>
#include <cmath>
#include <utility>

#include "protobuf/p2p.pb.h"

#define UNDEFINED (0)

/* a pandas-like dataFrame */
class dataFrame {
private:

    // TODO: Eliminate redundancy with templates
    std::unordered_map <unsigned long int, unsigned long int> row_id_map_int;
    std::unordered_map <unsigned long int, unsigned long int> col_id_map_int;
    std::unordered_map <std::string, unsigned long int> row_id_map_string;
    std::unordered_map <std::string, unsigned long int> col_id_map_string;

    std::unordered_set<unsigned long int> row_contents_int;
    std::unordered_set<unsigned long int> col_contents_int;
    std::unordered_set<std::string> row_contents_string;
    std::unordered_set<std::string> col_contents_string;

    p2p::dataFrame proto_data;

    unsigned long int n_rows;
    unsigned long int n_cols;

public:
    bool isSymmetric;
    unsigned long int sizeOfData;

    // Initialization:
    dataFrame();
    void reserve(const std::vector<unsigned long int> &primary_ids, const std::vector<unsigned long int> &secondary_ids);
    void reserve(const std::vector<std::string> &primary_ids, const std::vector<std::string> &secondary_ids);
    void initializeDataCells();

    // Getters and Setters:
    void setSymmetric(bool isSymmetric);
    void insert(unsigned short int val, unsigned long int row_id, unsigned long int col_id);
    void insert(unsigned short int val, std::string row_id, std::string col_id);
    void insertSafe(unsigned short int val, unsigned long int row_id, unsigned long int col_id);
    void insertSafe(unsigned short int val, std::string row_id, std::string col_id);
    void insertRow(const std::unordered_map<unsigned long int, unsigned short int> &row_data, unsigned long int source_id);
    void insertRow(const std::unordered_map<std::string, unsigned short int> &row_data, std::string source_id);
    void insertLoc(unsigned short int val, unsigned long int row_loc, unsigned long int col_loc);
    unsigned short int retrieve(unsigned long int row_id, unsigned long int col_id);
    unsigned short int retrieve(std::string, std::string);
    unsigned short int retrieveLoc(unsigned long int row_loc, unsigned long int col_loc);
    unsigned short int retrieveSafe(unsigned long int row_id, unsigned long int col_id);
    unsigned short int retrieveSafe(std::string row_id, std::string col_id);
    bool validKey(unsigned long int row_id, unsigned long int col_id);
    bool validKey(std::string row_id, std::string col_id);
    unsigned long int symmetricEquivalentLoc(unsigned long int row_loc, unsigned long int col_loc);
    unsigned long int getRowIndexLoc(unsigned long int row_index);
    unsigned long int getRowIndexLoc(std::string row_index);
    unsigned long int getColIndexLoc(unsigned long int col_index);
    unsigned long int getColIndexLoc(std::string col_index);

    // Input/Output:
    bool readCSV(const std::string &infile);
    bool readTMX(const std::string &infile);
    bool writeCSV(const std::string &outfile);
    bool writeTMX(const std::string &outfile);
    void printDataFrame();
    bool readTransitCSV(const std::string& infile);

private:
    // Input/Output
    bool writeToStream(std::ostream& streamToWrite);
};

// Initialization:

/* void constructor */
dataFrame::dataFrame() 
{
}

void dataFrame::initializeDataCells()
{
    // determine the size of the flat array
    if (this->isSymmetric)
    {
        this->sizeOfData = n_rows * (n_rows + 1) / 2;
    }
    else
    {
        this->sizeOfData = n_rows * n_cols;
    }
    proto_data.mutable_data_cell()->Resize(sizeOfData, UNDEFINED);
}

/* reserve a data frame according to the given indeces */
void dataFrame::reserve(const std::vector<unsigned long int> &primary_ids, const std::vector<unsigned long int> &secondary_ids) 
{
    n_rows = primary_ids.size();
    n_cols = secondary_ids.size();

    // preallocate row index structures
    for (unsigned long int row_idx = 0; row_idx < n_rows; row_idx++) {
        auto new_row_label = proto_data.add_row_label();
        new_row_label->set_int_label(primary_ids.at(row_idx));
        row_id_map_int[primary_ids.at(row_idx)] = row_idx;
        row_contents_int.insert(primary_ids.at(row_idx));
    }

    // preallocate col index structures
    for (unsigned long int col_idx = 0; col_idx < n_cols; col_idx++) {
        auto new_col_label = proto_data.add_col_label();
        new_col_label->set_int_label(secondary_ids.at(col_idx));
        col_id_map_int[secondary_ids.at(col_idx)] = col_idx;
        col_contents_int.insert(secondary_ids.at(col_idx));
    }

    initializeDataCells();
}

void dataFrame::reserve(const std::vector<std::string> &primary_ids, const std::vector<std::string> &secondary_ids)
{
    n_rows = primary_ids.size();
    n_cols = secondary_ids.size();


    // preallocate row index structures
    for (unsigned long int row_idx = 0; row_idx < n_rows; row_idx++) {
        auto new_row_label = proto_data.add_row_label();
        new_row_label->set_string_label(primary_ids.at(row_idx));
        row_id_map_string[primary_ids.at(row_idx)] = row_idx;
        row_contents_string.insert(primary_ids.at(row_idx));
    }

    // preallocate col index structures
    for (unsigned long int col_idx = 0; col_idx < n_cols; col_idx++) {
        auto new_col_label = proto_data.add_col_label();
        new_col_label->set_string_label(secondary_ids.at(col_idx));
        col_id_map_string[secondary_ids.at(col_idx)] = col_idx;
        col_contents_string.insert(secondary_ids.at(col_idx));
    }

    initializeDataCells();
}

// Getters and Setters:

unsigned long int dataFrame::getRowIndexLoc(unsigned long int row_index)
{
    return row_id_map_int.at(row_index);
}

unsigned long int dataFrame::getRowIndexLoc(std::string row_index)
{
    return row_id_map_string.at(row_index);
}

unsigned long int dataFrame::getColIndexLoc(unsigned long int col_index)
{
    return col_id_map_int.at(col_index);
}

unsigned long int dataFrame::getColIndexLoc(std::string col_index)
{
    return col_id_map_string.at(col_index);
}

void dataFrame::setSymmetric(bool isSymmetric)
{
    this->isSymmetric = isSymmetric;
}

/* insert a value with row_id, col_id */
void dataFrame::insertRow(const std::unordered_map<unsigned long int, unsigned short int> &row_data, unsigned long int source_id) 
{
    for (auto element : row_data)
    {
        this->insert(element.second, source_id, element.first);
    }
}


/* insert a value and throw an exception if the indeces don't exist */
void dataFrame::insertSafe(unsigned short int val, unsigned long int row_id, unsigned long int col_id)
{
    if (row_id_map_int.find(row_id) == row_id_map_int.end())
    {
        throw std::runtime_error("row_id does not exist:" + std::to_string(row_id));
    }
    if (col_id_map_int.find(col_id) == col_id_map_int.end())
    {
        throw std::runtime_error("col_id does not exist:" + std::to_string(col_id));
    }
    try
    {
        insertLoc(val, col_id_map_int.at(row_id), col_id_map_int.at(col_id));
    }
    catch (...)
    {
        auto errorMessage = "index is out of bounds:" + std::to_string(row_id) + "," + std::to_string(col_id) + "\n";
        errorMessage += "row_loc:" + std::to_string(row_id_map_int.at(row_id)) + "\n";
        errorMessage += "col_loc:" + std::to_string(col_id_map_int.at(col_id)) + "\n";
        if (this->isSymmetric)
        {
            if (col_id_map_int.at(col_id) >= row_id_map_int.at(row_id))
            {
                errorMessage += "symmetric equivalent (over diagonal):" + std::to_string(symmetricEquivalentLoc(row_id_map_int.at(row_id), col_id_map_int.at(col_id))) + "\n";
            }
            else
            {
                errorMessage += "symmetric equivalent (under diagonal):" + std::to_string(symmetricEquivalentLoc(col_id_map_int.at(col_id), row_id_map_int.at(row_id))) + "\n";   
            }
            errorMessage += "out of: " + std::to_string(this->sizeOfData) + "\n"; 
        }
        throw std::runtime_error(errorMessage);
    }
}

/* insert a value and throw an exception if the indeces don't exist */
void dataFrame::insertSafe(unsigned short int val, std::string row_id, std::string col_id)
{
    if (row_id_map_string.find(row_id) == row_id_map_string.end())
    {
        throw std::runtime_error("row_id does not exist:" + row_id);
    }
    if (col_id_map_string.find(col_id) == col_id_map_string.end())
    {
        throw std::runtime_error("col_id does not exist:" + col_id);
    }
    try
    {
        insertLoc(val, row_id_map_string.at(row_id), col_id_map_string.at(col_id));
    }
    catch (...)
    {
        auto errorMessage = "index is out of bounds:" + row_id + "," + col_id + "\n";
        errorMessage += "row_loc:" + std::to_string(row_id_map_string.at(row_id)) + "\n";
        errorMessage += "col_loc:" + std::to_string(col_id_map_string.at(col_id)) + "\n";
        if (this->isSymmetric)
        {
            if (col_id_map_string.at(col_id) >= row_id_map_string.at(row_id))
            {
                errorMessage += "symmetric equivalent (over diagonal):" + std::to_string(symmetricEquivalentLoc(row_id_map_string.at(row_id), col_id_map_string.at(col_id))) + "\n";
            }
            else
            {
                errorMessage += "symmetric equivalent (under diagonal):" + std::to_string(symmetricEquivalentLoc(col_id_map_string.at(col_id), row_id_map_string.at(row_id))) + "\n";   
            }
            errorMessage += "out of: " + std::to_string(this->sizeOfData) + "\n"; 
        }
        throw std::runtime_error(errorMessage);
    }
}

/* insert a value with row_id, col_id. Undefined behavior if indeces don't exist */
void dataFrame::insert(unsigned short int val, unsigned long int row_id, unsigned long int col_id) 
{
    insertLoc(val, row_id_map_int.at(row_id), col_id_map_int.at(col_id));
}

/* insert a value with row_id, col_id. Undefined behavior if indeces don't exist */
void dataFrame::insert(unsigned short int val, std::string row_id, std::string col_id) 
{
    insertLoc(val, row_id_map_string.at(row_id), col_id_map_string.at(col_id));
}

/* calculate the flat array index of a coordinate pair for a symmetric matrix */
unsigned long int dataFrame::symmetricEquivalentLoc(unsigned long int row_loc, unsigned long int col_loc)
{
    return col_loc - row_loc + this->sizeOfData - (this->n_rows - row_loc) * (this->n_rows - row_loc + 1) / 2;
}


/* insert a value with row_loc, col_loc */
void dataFrame::insertLoc(unsigned short int val, unsigned long int row_loc, unsigned long int col_loc) {
    if (this->isSymmetric)
    {
        if (col_loc >= row_loc)
        {
            //this->data.at(this->symmetricEquivalentLoc(row_loc, col_loc)) = val;
            auto index = this->symmetricEquivalentLoc(row_loc, col_loc);
            this->proto_data.mutable_data_cell()->Set(index, val);
        }
    }
    else
    {
        //this->data.at(row_loc * n_cols + col_loc) = val;
        auto index = row_loc * n_cols + col_loc;
        this->proto_data.mutable_data_cell()->Set(index, val);
    }
}

/* retrieve a value with row_id, col_id */
/* warning: this method is UNSAFE. Results are undefined*/
/* if keys are not present in dataframe */
/* for safe retrieval, use retrieveSafe */
unsigned short int dataFrame::retrieve(unsigned long int row_id, unsigned long int col_id) 
{
    return retrieveLoc(row_id_map_int.at(row_id), col_id_map_int.at(col_id));
}

/* retrieve a value with row_id, col_id */
/* warning: this method is UNSAFE. Results are undefined*/
/* if keys are not present in dataframe */
/* for safe retrieval, use retrieveSafe */
unsigned short int dataFrame::retrieve(std::string row_id, std::string col_id) 
{
    return retrieveLoc(row_id_map_string.at(row_id), col_id_map_string.at(col_id));
}

/* return the value by location. Return the converse if symmetric
 * and below the diagonal
 */
unsigned short int dataFrame::retrieveLoc(unsigned long int row_loc, unsigned long int col_loc)
{
    unsigned long int index;
    if (isSymmetric)
    {
        if (col_loc >= row_loc)
        {
            index = this->symmetricEquivalentLoc(row_loc, col_loc);
        }
        else
        {   
            index = this->symmetricEquivalentLoc(col_loc, row_loc);
        }
    }
    else
    {
        index = row_loc * n_cols + col_loc;
    }
    //return this->data.at(row_loc * n_cols + col_loc);
    return this->proto_data.data_cell(index);
}


/* check if a key pair is valid (both are in the data frame) */
bool dataFrame::validKey(unsigned long int row_id, unsigned long int col_id) 
{
    if (row_contents_int.find(row_id) == row_contents_int.end()) {
        return false;
    }
    if (col_contents_int.find(col_id) == col_contents_int.end()) {
        return false;
    }

    return true;
}

/* check if a key pair is valid (both are in the data frame) */
bool dataFrame::validKey(std::string row_id, std::string col_id) 
{
    if (row_contents_string.find(row_id) == row_contents_string.end()) {
        return false;
    }
    if (col_contents_string.find(col_id) == col_contents_string.end()) {
        return false;
    }

    return true;
}

/* retrieve a value with row_id, col_id */
/* this method is SAFE, and will throw an error*/
/* if keys are undefined*/
unsigned short int dataFrame::retrieveSafe(unsigned long int row_id, unsigned long int col_id) 
{
    try
    {
        return this->retrieve(row_id, col_id);    
    }
    catch (...)
    {
        throw std::runtime_error("index is out of bounds:" + std::to_string(row_id) + "," + std::to_string(col_id));
    }
}

/* retrieve a value with row_id, col_id */
/* this method is SAFE, and will throw an error*/
/* if keys are undefined*/
unsigned short int dataFrame::retrieveSafe(std::string row_id, std::string col_id) 
{
    try
    {
        return this->retrieve(row_id, col_id);    
    }
    catch (...)
    {
        throw std::runtime_error("index is out of bounds:" + row_id + "," + col_id);
    }
}



// Input/Output:

/* Write the dataFrame to a .tmx (a custom binary format) */
bool dataFrame::writeTMX(const std::string &outfile)
{
    
    std::fstream output(outfile, std::ios::out | std::ios::trunc | std::ios::binary);
    if (!proto_data.SerializeToOstream(&output)) {
        std::cerr << "Failed to write .tmx" << std::endl;
        return false;
    }
    output.close();
    return true;

}


/* Read the dataFrame from a .tmx (a custom binary format) */
bool dataFrame::readTMX(const std::string& infile)
{
    std::fstream inputFile(infile, std::ios::in | std::ios::binary);

    if (!proto_data.ParseFromIstream(&inputFile)) {
        std::cerr << "Failed to load .tmx" << std::endl;
        return false;
    }    

    std::vector<unsigned long int> infileRowIntLabels;
    std::vector<unsigned long int> infileColIntLabels;

    std::vector<std::string> infileRowStringLabels;
    std::vector<std::string> infileColStringLabels;

    this->n_rows = proto_data.row_label_size();
    this->n_cols = proto_data.col_label_size();
    if (proto_data.row_label_type() == p2p::dataFrame::STRING)
    {
        for (auto row_label : proto_data.row_label())
        {
            infileRowStringLabels.push_back(row_label.string_label());
        }
    }
    else
    {
        for (auto row_label : proto_data.row_label())
        {
            infileRowIntLabels.push_back(row_label.int_label());
        }
    }
    if (proto_data.col_label_type() == p2p::dataFrame::STRING)
    {
        for (auto col_label : proto_data.col_label())
        {
            infileColStringLabels.push_back(col_label.string_label());
        }
    }
    else
    {
        for (auto col_label : proto_data.col_label())
        {
            infileColIntLabels.push_back(col_label.int_label());
        }
    }
    if (proto_data.row_label_type() == proto_data.col_label_type())
    {
        // check which set of labels to send
        switch (proto_data.row_label_type())
        {
            case p2p::dataFrame::STRING:
                this->reserve(infileRowStringLabels, infileColStringLabels);
                break;
            case p2p::dataFrame::INT:
                this->reserve(infileRowIntLabels, infileColIntLabels);
                break;
            default:
                inputFile.close();
                throw std::runtime_error("Unrecognized enum type");
        }
    }   
    else
    {
        // throw a runtime error if the labels for columns and rows
        // are not the same type
        inputFile.close();
        throw std::runtime_error("Columns and rows must have the same label type");
    }

    inputFile.close();
    return true;
}


bool dataFrame::writeCSV(const std::string &outfile)
{
    std::ofstream Ofile;
    Ofile.open(outfile);
    if (Ofile.fail()) {
        throw std::runtime_error("Could not open output file");
    }
    writeToStream(Ofile);
    Ofile.close();
    return true;
} 

bool dataFrame::writeToStream(std::ostream& streamToWrite)
{
    streamToWrite << ",";
    
    // write the top row of column labels
    if (proto_data.col_label_type() == p2p::dataFrame::STRING) 
    {
        for (auto col_label : proto_data.col_label())
        {
            streamToWrite << col_label.string_label() << ",";
        }
    } else {
        for (auto col_label : proto_data.col_label())
        {
            streamToWrite << col_label.int_label() << ",";
        }
    }
    streamToWrite << std::endl;

    // write the body of the table, each row has a row label and values
    if (proto_data.row_label_type() == p2p::dataFrame::STRING)
    {
        for (unsigned long int row_index = 0; row_index < n_rows; row_index++)
        {
            streamToWrite << proto_data.row_label(row_index).string_label() << ",";
            for (unsigned long int col_index = 0; col_index < n_cols; col_index++)
            {
                streamToWrite << this->retrieveLoc(row_index, col_index) << ","; 
            }
            streamToWrite << std::endl;
        }

    } else 
    {
        for (unsigned long int row_index = 0; row_index < n_rows; row_index++)
        {
            streamToWrite << proto_data.row_label(row_index).int_label() << ",";
            for (unsigned long int col_index = 0; col_index < n_cols; col_index++)
            {
                streamToWrite << this->retrieveLoc(row_index, col_index) << ","; 
            }
            streamToWrite << std::endl;
        }
    }
    return true;
}

void dataFrame::printDataFrame()
{
    writeToStream(std::cout);
} 

/* Read the dataFrame from a .csv */
bool dataFrame::readCSV(const std::string &infile) {
    // std::ifstream fileINA, fileINB;
    // fileINA.open(infile);
    // if (fileINA.fail()) {
    //     return false;
    // }
    // std::vector<unsigned long int> infileColLabels;
    // std::vector<unsigned long int> infileRowLabels;
    // std::string line;
    // n_rows = 0, n_cols = 0;
    // bool first_row = true;

    // // first pass through to allocate matrix and load
    // // columns/rows
    // while (getline(fileINA, line)) {
    //     std::istringstream stream(line);
    //     if (first_row) {
    //         first_row = false;
    //         std::string tmp_col_id;
    //         unsigned long int col_id;
    //         n_cols = 0;
    //         bool first_col = true;
    //         while (getline(stream, tmp_col_id, ',')) {
    //             if (first_col) {

    //                 first_col = false;
    //             } else {
    //                 col_id = stoul(tmp_col_id);
    //                 infileColLabels.push_back(col_id);
    //             }
    //         }
    //     } else {
    //         std::string tmp_row_id;
    //         unsigned long int row_id;
    //         getline(stream, tmp_row_id,',');
    //         if (!tmp_row_id.size())
    //         {
    //             break;
    //         }
    //         row_id = stoul(tmp_row_id);
    //         infileRowLabels.push_back(row_id);
            
    //     }
    // }
    // reserve(infileRowLabels, infileColLabels);

    // fileINA.close();

    // fileINB.open(infile);
    // if (fileINB.fail()) {
    //     return false;
    // }
    // int row_counter = 0;
    // unsigned short int value;
    // first_row = true;
    // while (getline(fileINB, line)) {
    //     std::istringstream stream(line);
    //     if (first_row) {
    //         first_row = false;
    //         continue;
    //     }
    //     std::string row_id, input;
    //     int col_counter = 0;
    //     bool first_col = true;
    //     while (getline(stream, input, ',')) {
    //         if (first_col) {
    //             first_col = false;
    //             row_id = stoul(input);
    //         } else {
    //             value = stoul(input);
    //             insertLoc(value, row_counter, col_counter);
    //             col_counter++;
    //         }
    //     }
    //     row_counter++;
    // }
    // fileINB.close();
    // return true;

}
bool dataFrame::readTransitCSV(const std::string& infile)
{
    // std::ifstream Ifile;
    // Ifile.open(infile);
    // if (Ifile.fail()) {
    //     Ifile.close();
    //     return false;
    // }
    // std::string line;
    // std::string srcId;
    // std::string dstId;
    // std::string weight;
    // unsigned long int table_rows = 0;
    // std::unordered_map<std::pair<unsigned long int, unsigned long int>, unsigned short int, pair_hash> input_data;
    // //read the file
    // while (getline(Ifile, line))
    // {
    //     std::istringstream stream(line);
    //     getline(stream, srcId, ',');
    //     getline(stream, dstId, ',');
    //     getline(stream, weight, '\n');
    //     table_rows++;
    //     unsigned long int srcIdInt = stoul(srcId);
    //     unsigned long int dstIdInt = stoul(dstId);
    //     unsigned short int weightInt = stoi(weight);
    //     input_data.insert(std::make_pair(std::make_pair(srcIdInt, dstIdInt), weightInt));
    // }
    // Ifile.close();

    // // ensure the table is symmetric by verifying the number of rows
    // // read in is a perfect square
    // unsigned long int table_rows_sqrt = sqrt(table_rows);
    // if (table_rows_sqrt * table_rows_sqrt != table_rows)
    // {
    //     throw std::runtime_error("Input table was not symmetrical");
    // }
    // this->n_rows = table_rows_sqrt;
    // this->n_cols = table_rows_sqrt;
    // this->isSymmetric = true;

    // std::vector<unsigned long int> srcIdVector;
    // std::vector<unsigned long int> dstIdVector;
    // for (auto key : input_data)
    // {
    //     unsigned long int srcInt = key.first.first;
    //     unsigned long int dstInt = key.first.second;
    //     srcIdVector.push_back(srcInt);
    //     dstIdVector.push_back(dstInt);
    // }
    // this->reserve(srcIdVector, dstIdVector);
    // for (auto pair : input_data)
    // {
    //     this->insertSafe(pair.first.first, pair.first.second, pair.second);
    // }
    return true;
}