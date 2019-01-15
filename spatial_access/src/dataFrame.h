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
#include <sys/stat.h>

#include "protobuf/p2p.pb.h"

#define UNDEFINED (0)

/* a pandas-like dataFrame */
class dataFrame {
private:

    // TODO: Eliminate redundancy with templates
    std::unordered_map <unsigned long int, p2p::dataRow> row_id_map_int;
    std::unordered_map <std::string, p2p::dataRow> row_id_map_string;

    // Map the column id to a location in an array
    std::unordered_map<unsigned long int, unsigned long int> col_id_int_to_loc;
    std::unordered_map<std::string, unsigned long int> col_id_string_to_loc;

    p2p::metaData metaData;

public:
    unsigned long int sizeOfData;

    // Initialization:
    dataFrame();
    void reserve(const std::vector<unsigned long int> &primary_ids, const std::vector<unsigned long int> &secondary_ids);
    void reserve(const std::vector<std::string> &primary_ids, const std::vector<std::string> &secondary_ids);
    
    // Getters and Setters:
    unsigned short int retrieveValue(unsigned long int row_id, unsigned long int col_id);
    unsigned short int retrieveValue(const std::string& row_id, const std::string& col_id);
    void insertValue(unsigned short int value, unsigned long int row_id, unsigned long int col_id);
    void insertValue(unsigned short int value, const std::string& row_id, const std::string& col_id);
    bool isSymmetric();
    void setSymmetric(bool isSymmetric);
    void insertRow(const std::unordered_map<unsigned long int, unsigned short int> &row_data, unsigned long int source_id);
    void insertRow(const std::unordered_map<std::string, unsigned short int> &row_data, const std::string& source_id);

    // Input/Output:
    bool readCSV(const std::string &infile);
    bool readTMX(const std::string &infile);
    bool writeCSV(const std::string &outfile);
    bool writeTMX(const std::string &outfile);
    bool writeMetadata(const std::string &outfile);
    bool writeRowdata(const std::string &outfile, unsigned long int row_id);
    bool writeRowdata(const std::string &outfile, const std::string &row_id);
    bool readMetadata(const std::string &outfile);
    bool readRowdata(const std::string &outfile, unsigned long int row_id);
    bool readRowdata(const std::string &outfile, const std::string &row_id);
    void printDataFrame();
    bool readTransitCSV(const std::string& infile);

    // Utility
    bool isUnderDiagonal(unsigned long int row_id, unsigned long int col_id);
    bool isUnderDiagonal(const std::string& row_id, const std::string& col_id);

private:
    // Input/Output
    bool writeToStream(std::ostream& streamToWrite);

};

// Initialization:

/* void constructor */
dataFrame::dataFrame() 
{
}

/* reserve a data frame according to the given indeces */
void dataFrame::reserve(const std::vector<unsigned long int> &primary_ids, const std::vector<unsigned long int> &secondary_ids) 
{
    // initialize metaData
    for (auto row_id : primary_ids)
    {
        metaData.add_row_label_int(row_id);
    }

    // build col_id -> col_loc map
    for (unsigned long int col_loc = 0; col_loc < secondary_ids.size(); col_loc++)
    {
        metaData.add_col_label_int(secondary_ids.at(col_loc));
        col_id_int_to_loc[secondary_ids.at(col_loc)] = col_loc;
    }

    // preallocate row map row_id -> dataRow
    auto numberOfRows = primary_ids.size();
    auto numberOfCols = secondary_ids.size();
    for (unsigned long int row_idx = 0; row_idx < numberOfRows; row_idx++) {

        // if the dataFrame is symmetric, the size of each dataRow depends on
        // the current row
        if (metaData.is_symmetric())
        {
            auto columnsToAllocate = numberOfCols - row_idx;
            row_id_map_int[primary_ids.at(row_idx)].mutable_value()->Resize(columnsToAllocate, UNDEFINED);    
        }
        else
        {
            row_id_map_int[primary_ids.at(row_idx)].mutable_value()->Resize(numberOfCols, UNDEFINED);
        }
        
    }

    metaData.set_row_label_type(p2p::metaData::INT);
    metaData.set_col_label_type(p2p::metaData::INT);
}

/* reserve a data frame according to the given indeces */
void dataFrame::reserve(const std::vector<std::string> &primary_ids, const std::vector<std::string> &secondary_ids) 
{
    // initialize metaData
    for (auto row_id : primary_ids)
    {
        metaData.add_row_label_string(row_id);
    }

    // build col_id -> col_loc map
    for (unsigned long int col_loc = 0; col_loc < secondary_ids.size(); col_loc++)
    {
        metaData.add_col_label_string(secondary_ids.at(col_loc));
        col_id_string_to_loc[secondary_ids.at(col_loc)] = col_loc;
    }

    // preallocate row map row_id -> dataRow
    auto numberOfRows = primary_ids.size();
    auto numberOfCols = secondary_ids.size();
    for (unsigned long int row_idx = 0; row_idx < numberOfRows; row_idx++) {

        // if the dataFrame is symmetric, the size of each dataRow depends on
        // the current row
        if (metaData.is_symmetric())
        {
            auto columnsToAllocate = numberOfCols - row_idx;
            row_id_map_string[primary_ids.at(row_idx)].mutable_value()->Resize(columnsToAllocate, UNDEFINED);    
        }
        else
        {
            row_id_map_string[primary_ids.at(row_idx)].mutable_value()->Resize(numberOfCols, UNDEFINED);
        }
        
    }

    metaData.set_row_label_type(p2p::metaData::STRING);
    metaData.set_col_label_type(p2p::metaData::STRING);
}

// Getters/Setters

unsigned short int dataFrame::retrieveValue(unsigned long int row_id, unsigned long int col_id)
{
    if (metaData.is_symmetric())
    {
        // flip the row_id and col_id if under the diagonal
        if (this->isUnderDiagonal(row_id, col_id))
        {
            auto rowData = row_id_map_int.at(col_id);
            // real col_loc is current col_loc - current row_loc (to account for diagonal)
            auto col_loc = col_id_int_to_loc[row_id] - col_id_int_to_loc[col_id];
            return rowData.value(col_loc);
        }
        else
        {
            auto rowData = row_id_map_int.at(row_id);
            // real col_loc is current col_loc - current row_loc (to account for diagonal)
            auto col_loc = col_id_int_to_loc[col_id] - col_id_int_to_loc[row_id];
            return rowData.value(col_loc);
        }
    } else
    {
        auto rowData = row_id_map_int.at(row_id);
        auto col_loc = col_id_int_to_loc[col_id];
        return rowData.value(col_loc);
    }
}

unsigned short int dataFrame::retrieveValue(const std::string& row_id, const std::string& col_id)
{
    if (metaData.is_symmetric())
    {
        // flip the row_id and col_id if under the diagonal
        if (this->isUnderDiagonal(row_id, col_id))
        {
            auto rowData = row_id_map_string.at(col_id);
            // real col_loc is current col_loc - current row_loc (to account for diagonal)
            auto col_loc = col_id_string_to_loc[row_id] - col_id_string_to_loc[col_id];
            return rowData.value(col_loc);
        }
        else
        {
            auto rowData = row_id_map_string.at(row_id);
            // real col_loc is current col_loc - current row_loc (to account for diagonal)
            auto col_loc = col_id_string_to_loc[col_id] - col_id_string_to_loc[row_id];
            return rowData.value(col_loc);
        }
    } else
    {
        auto rowData = row_id_map_string.at(row_id);
        auto col_loc = col_id_string_to_loc[col_id];
        return rowData.value(col_loc);
    }
}

void dataFrame::insertValue(unsigned short int value, unsigned long int row_id, unsigned long int col_id)
{
    if (metaData.is_symmetric())
    {
        // flip the row_id and col_id if under the diagonal
        if (this->isUnderDiagonal(row_id, col_id))
        {
            // no need to insert, it is duplicate
            return;
        }
        else
        {
            // real col_loc is current col_loc - current row_loc (to account for diagonal)
            auto col_loc = col_id_int_to_loc[col_id] - col_id_int_to_loc[row_id];
            row_id_map_int.at(row_id).set_value(col_loc, value);
        }
    } else
    {
        auto col_loc = col_id_int_to_loc[col_id];
        row_id_map_int.at(row_id).set_value(col_loc, value);
    }
}

void dataFrame::insertValue(unsigned short int value, const std::string& row_id, const std::string& col_id)
{
    if (metaData.is_symmetric())
    {
        // flip the row_id and col_id if under the diagonal
        if (this->isUnderDiagonal(row_id, col_id))
        {
            // no need to insert, it is duplicate
            return;
        }
        else
        {
            // real col_loc is current col_loc - current row_loc (to account for diagonal)
            auto col_loc = col_id_string_to_loc[col_id] - col_id_string_to_loc[row_id];
            row_id_map_string.at(row_id).set_value(col_loc, value);
        }
    } else
    {
        auto col_loc = col_id_string_to_loc[col_id];
        row_id_map_string.at(row_id).set_value(col_loc, value);
    }
}

void dataFrame::insertRow(const std::unordered_map<unsigned long int, unsigned short int> &row_data, unsigned long int source_id)
{
    for (auto element : row_data)
    {
        this->insertValue(element.second, source_id, element.first);
    }
}

void dataFrame::insertRow(const std::unordered_map<std::string, unsigned short int> &row_data, const std::string& source_id)
{
    for (auto element : row_data)
    {
        this->insertValue(element.second, source_id, element.first);
    }
}


bool dataFrame::isSymmetric()
{
    return metaData.is_symmetric();
}

void dataFrame::setSymmetric(bool isSymmetric)
{
    metaData.set_is_symmetric(isSymmetric);
}

// Utilities

/* return true if position is under the diagonal, else false */
/* note: calling this method for an unsymmetric matrix will cause segfault */
bool dataFrame::isUnderDiagonal(unsigned long int row_id, unsigned long int col_id)
{
    return this->col_id_int_to_loc[row_id] > this->col_id_int_to_loc[col_id];
}

/* return true if position is under the diagonal, else false */
/* note: calling this method for an unsymmetric matrix will cause segfault */
bool dataFrame::isUnderDiagonal(const std::string& row_id, const std::string& col_id)
{
    return this->col_id_string_to_loc[row_id] > this->col_id_string_to_loc[col_id];
}



// Input/Output:

bool dataFrame::writeMetadata(const std::string &outfile)
{
    std::string filename = outfile + "/meta";
    std::fstream output(filename, std::ios::out | std::ios::trunc | std::ios::binary);
    if (!metaData.SerializeToOstream(&output)) {
        std::cerr << "Failed to write to " << filename << std::endl;
        return false;
    }
    output.close();
    return true;
}

bool dataFrame::writeRowdata(const std::string &outfile, const std::string &row_id)
{
    std::string filename = outfile + "/" + row_id;
    std::fstream output(filename, std::ios::out | std::ios::trunc | std::ios::binary);
    if (!row_id_map_string[row_id].SerializeToOstream(&output)) {
        std::cerr << "Failed to write to " << filename << std::endl;
        return false;
    }
    output.close();
    return true;
}

bool dataFrame::writeRowdata(const std::string &outfile, unsigned long int row_id)
{
    std::string filename = outfile + "/" + std::to_string(row_id);
    std::fstream output(filename, std::ios::out | std::ios::trunc | std::ios::binary);
    if (!row_id_map_int[row_id].SerializeToOstream(&output)) {
        std::cerr << "Failed to write to " << filename << std::endl;
        return false;
    }
    output.close();
    return true;
}

/* Write the dataFrame to a .tmx (a custom binary format) */
bool dataFrame::writeTMX(const std::string &outfile)
{
    const int dir_err = mkdir(outfile.c_str(), S_IRWXU | S_IRWXG | S_IROTH | S_IXOTH);
    if (-1 == dir_err)
    {
        if (errno != EEXIST)
        {
            throw std::runtime_error("error creating directory");
        }
    
    }
    writeMetadata(outfile);
    if (metaData.row_label_type() == p2p::metaData::STRING)
    {
        for (std::string row_id : metaData.row_label_string())
        {
            writeRowdata(outfile, row_id);
        }
    }   
    else
    {
        for (unsigned long int row_id : metaData.row_label_int())
        {
            writeRowdata(outfile, row_id);
        }
    }
    return true;
}

bool dataFrame::readMetadata(const std::string &outfile)
{
    std::string filename = outfile + "/meta";
    std::fstream input(filename, std::ios::in | std::ios::binary);
    if (!metaData.ParseFromIstream(&input)) {
        std::cerr << "Failed to read from " << filename << std::endl;
        return false;
    }
    input.close();
    return true;
}

bool dataFrame::readRowdata(const std::string &outfile, const std::string &row_id)
{
    std::string filename = outfile + "/" + row_id;
    std::fstream input(filename, std::ios::in | std::ios::binary);
    if (!row_id_map_string[row_id].ParseFromIstream(&input)) {
        std::cerr << "Failed to read from " << filename << std::endl;
        return false;
    }
    input.close();
    return true;
}

bool dataFrame::readRowdata(const std::string &outfile, unsigned long int row_id)
{
    std::string filename = outfile + "/" + std::to_string(row_id);
    std::fstream input(filename, std::ios::in | std::ios::binary);
    if (!row_id_map_int[row_id].ParseFromIstream(&input)) {
        std::cerr << "Failed to read from " << filename << std::endl;
        return false;
    }
    input.close();
    return true;
}

/* Read the dataFrame from a .tmx (a custom binary format) */
bool dataFrame::readTMX(const std::string& infile)
{
    readMetadata(infile);

    if (metaData.row_label_type() == p2p::metaData::STRING)
    {
        // build col_id -> col_loc map
        for (unsigned long int col_loc = 0; col_loc < metaData.col_label_string_size(); col_loc++)
        {
            col_id_string_to_loc[metaData.col_label_string(col_loc)] = col_loc;
        }
        for (std::string row_id : metaData.row_label_string())
        {
            readRowdata(infile, row_id);
        }

    }   
    else
    {
        // build col_id -> col_loc map
        for (unsigned long int col_loc = 0; col_loc < metaData.col_label_int_size(); col_loc++)
        {
            col_id_int_to_loc[metaData.col_label_int(col_loc)] = col_loc;
        }
        for (unsigned long int row_id : metaData.row_label_int())
        {
            readRowdata(infile, row_id);
        }
    }
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
    if (metaData.col_label_type() == p2p::metaData::STRING) 
    {
        for (auto col_label : metaData.col_label_string())
        {
            streamToWrite << col_label << ",";
        }
    } else {
        for (auto col_label : metaData.col_label_int())
        {
            streamToWrite << col_label << ",";
        }
    }
    streamToWrite << std::endl;

    // // write the body of the table, each row has a row label and values
    if (metaData.row_label_type() == p2p::metaData::STRING)
    {
        for (std::string row_id : metaData.row_label_string())
        {
            streamToWrite << row_id << ",";
            for (std::string col_id : metaData.col_label_string())
            {
                streamToWrite << this->retrieveValue(row_id, col_id) << ","; 
            }
            streamToWrite << std::endl;
        }

    } else 
    {
        for (unsigned long int row_id : metaData.row_label_int())
        {
            streamToWrite << std::to_string(row_id) << ",";
            for (unsigned long int col_id : metaData.col_label_int())
            {
                streamToWrite << this->retrieveValue(row_id, col_id) << ","; 
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
    return true;

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