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

#include "csv.h"
#include "dataFrame.h"
#include <climits>

#define UNDEFINED (USHRT_MAX)

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

unsigned short int dataFrame::retrieveValue(unsigned long int row_id, unsigned long int col_id) const
{
    if (metaData.is_symmetric())
    {
        // flip the row_id and col_id if under the diagonal
        if (this->isUnderDiagonal(row_id, col_id))
        {
            auto rowData = row_id_map_int.at(col_id);
            // real col_loc is current col_loc - current row_loc (to account for diagonal)
            auto col_loc = col_id_int_to_loc.at(row_id) - col_id_int_to_loc.at(col_id);
            return rowData.value(col_loc);
        }
        else
        {
            auto rowData = row_id_map_int.at(row_id);
            // real col_loc is current col_loc - current row_loc (to account for diagonal)
            auto col_loc = col_id_int_to_loc.at(col_id) - col_id_int_to_loc.at(row_id);
            return rowData.value(col_loc);
        }
    } else
    {
        auto rowData = row_id_map_int.at(row_id);
        auto col_loc = col_id_int_to_loc.at(col_id);
        return rowData.value(col_loc);
    }
}

unsigned short int dataFrame::retrieveValue(const std::string& row_id, const std::string& col_id) const
{
    if (metaData.is_symmetric())
    {
        // flip the row_id and col_id if under the diagonal
        if (this->isUnderDiagonal(row_id, col_id))
        {
            auto rowData = row_id_map_string.at(col_id);
            // real col_loc is current col_loc - current row_loc (to account for diagonal)
            auto col_loc = col_id_string_to_loc.at(row_id) - col_id_string_to_loc.at(col_id);
            return rowData.value(col_loc);
        }
        else
        {
            auto rowData = row_id_map_string.at(row_id);
            // real col_loc is current col_loc - current row_loc (to account for diagonal)
            auto col_loc = col_id_string_to_loc.at(col_id) - col_id_string_to_loc.at(row_id);
            return rowData.value(col_loc);
        }
    } else
    {
        auto rowData = row_id_map_string.at(row_id);
        auto col_loc = col_id_string_to_loc.at(col_id);
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
            auto col_loc = col_id_int_to_loc.at(col_id) - col_id_int_to_loc.at(row_id);
            row_id_map_int.at(row_id).set_value(col_loc, value);
        }
    } else
    {
        auto col_loc = col_id_int_to_loc.at(col_id);
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
            auto col_loc = col_id_string_to_loc.at(col_id) - col_id_string_to_loc.at(row_id);
            row_id_map_string.at(row_id).set_value(col_loc, value);
        }
    } else
    {
        auto col_loc = col_id_string_to_loc.at(col_id);
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


bool dataFrame::isSymmetric() const
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
bool dataFrame::isUnderDiagonal(unsigned long int row_id, unsigned long int col_id) const
{
    return this->col_id_int_to_loc.at(row_id) > this->col_id_int_to_loc.at(col_id);
}

/* return true if position is under the diagonal, else false */
/* note: calling this method for an unsymmetric matrix will cause segfault */
bool dataFrame::isUnderDiagonal(const std::string& row_id, const std::string& col_id) const
{
    return this->col_id_string_to_loc.at(row_id) > this->col_id_string_to_loc.at(col_id);
}



// Input/Output:

bool dataFrame::writeMetadata(const std::string &outfile) const
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

bool dataFrame::writeRowdata(const std::string &outfile, const std::string &row_id) const
{
    std::string filename = outfile + "/" + row_id;
    std::fstream output(filename, std::ios::out | std::ios::trunc | std::ios::binary);
    if (!row_id_map_string.at(row_id).SerializeToOstream(&output)) {
        std::cerr << "Failed to write to " << filename << std::endl;
        return false;
    }
    output.close();
    return true;
}

bool dataFrame::writeRowdata(const std::string &outfile, unsigned long int row_id) const
{
    std::string filename = outfile + "/" + std::to_string(row_id);
    std::fstream output(filename, std::ios::out | std::ios::trunc | std::ios::binary);
    if (!row_id_map_int.at(row_id).SerializeToOstream(&output)) {
        std::cerr << "Failed to write to " << filename << std::endl;
        return false;
    }
    output.close();
    return true;
}

/* Write the dataFrame to a .tmx (a custom binary format) */
bool dataFrame::writeTMX(const std::string &outfile) const
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
        for (signed long int col_loc = 0; col_loc < metaData.col_label_string_size(); col_loc++)
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
        for (signed long int col_loc = 0; col_loc < metaData.col_label_int_size(); col_loc++)
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


bool dataFrame::writeCSV(const std::string &outfile) const
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

bool dataFrame::writeToStream(std::ostream& streamToWrite) const
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

void dataFrame::printDataFrame() const
{
    writeToStream(std::cout);
} 

/* Read the dataFrame from a .csv */
bool dataFrame::readCSV(const std::string &infile) 
{
    CSV file(infile);
    auto row_labels = file.get_row_labels_as_int();
    auto col_labels = file.get_col_labels_as_int();
    metaData.set_is_symmetric(false);
    metaData.set_row_label_type(p2p::metaData::INT);
    metaData.set_col_label_type(p2p::metaData::INT);
    reserve(row_labels, col_labels);
    for (unsigned int row_loc = 0; row_loc < file.num_rows(); row_loc++)
    {
        auto row = file.get_row_by_index_as_int(row_loc);
        for (unsigned int col_loc = 0; col_loc < file.num_cols(); col_loc++)
        {
            auto row_id = row_labels.at(row_loc);
            auto col_id = col_labels.at(col_loc);
            unsigned long int value = row.at(col_loc);
            insertValue(value, row_id, col_id);
        }
    }
    return true;

}

bool dataFrame::readOTPMatrix(const std::string& infile)
{
    std::ifstream fileIN;
    fileIN.open(infile);
    if (fileIN.fail()) {
        throw std::runtime_error("unable to read OTPTransitMatrix");
    }

    std::string line;
    std::string row_label_string;
    std::string col_label_string;
    std::unordered_set<unsigned long int> row_label_set;
    std::unordered_set<unsigned long int> col_label_set;

    unsigned long int row_label_int;
    unsigned long int col_label_int;

    // read through the first n rows to read in all columns
    while (getline(fileIN, line)) 
    {
        std::istringstream stream(line);
        if (not getline(stream, row_label_string, ','))
        {
            throw std::runtime_error("expected row label");
        }
        if (not getline(stream, col_label_string, ','))
        {
            throw std::runtime_error("expected col label");
        }

        col_label_int = stoul(col_label_string);
        row_label_int = stoul(row_label_string);
        row_label_set.insert(row_label_int);
        col_label_set.insert(col_label_int);
    }
    std::vector<unsigned long int> row_labels(row_label_set.begin(), row_label_set.end());
    std::vector<unsigned long int> col_labels(col_label_set.begin(), col_label_set.end());

    fileIN.close(); 
    reserve(row_labels, col_labels);
    metaData.set_is_symmetric(false);
    metaData.set_row_label_type(p2p::metaData::INT);
    metaData.set_col_label_type(p2p::metaData::INT);
    fileIN.open(infile);
    if (fileIN.fail()) {
        throw std::runtime_error("unable to read OTPTransitMatrix");
    }

    // read through the table a second time to load values into
    // memory
    std::string value_string;
    unsigned short int value_int;
    while (getline(fileIN, line)) 
    {
        std::istringstream stream(line);
        if (not getline(stream, row_label_string, ','))
        {
            throw std::runtime_error("expected row label");
        }
        if (not getline(stream, col_label_string, ','))
        {
            throw std::runtime_error("expected col label");
        }
        if (not getline(stream, value_string, ','))
        {
            throw std::runtime_error("expected value");
        }
        col_label_int = stoul(col_label_string);
        row_label_int = stoul(row_label_string);
        value_int = std::stoi(value_string);
        this->insertValue(value_int, row_label_int, col_label_int);
    }

    fileIN.close(); 
    return true;
}