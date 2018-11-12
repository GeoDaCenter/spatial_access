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

#define UNDEFINED (0)

/* a pandas-like dataFrame */
class dataFrame {
private:
    std::vector<unsigned short int> data;
    std::unordered_map <unsigned long int, unsigned long int> rows;
    std::unordered_map <unsigned long int, unsigned long int> cols;

    std::vector<unsigned long int> row_labels;
    std::vector<unsigned long int> col_labels;
    std::unordered_set<unsigned long int> row_contents;
    std::unordered_set<unsigned long int> col_contents;

    unsigned long int n_rows;
    unsigned long int n_cols;

public:
    bool isSymmetric;
    unsigned long int sizeOfData;
    dataFrame();
    unsigned long int getRowIndexLoc(unsigned long int row_index);
    unsigned long int getColIndexLoc(unsigned long int col_index);
    bool readCSV(const std::string &infile);
    bool readTMX(const std::string &infile);
    void insert(unsigned short int val, unsigned long int row_id, unsigned long int col_id);
    void insertSafe(unsigned short int val, unsigned long int row_id, unsigned long int col_id);
    void insertRow(const std::unordered_map<unsigned long int, unsigned short int> &row_data, unsigned long int source_id);
    void insertLoc(unsigned short int val, unsigned long int row_loc, unsigned long int col_loc);
    void reserve(const std::vector<unsigned long int> &primary_ids, const std::vector<unsigned long int> &secondary_ids);
    unsigned short int retrieve(unsigned long int row_id, unsigned long int col_id);
    unsigned short int retrieveLoc(unsigned long int row_id, unsigned long int col_id);
    unsigned short int retrieveSafe(unsigned long int row_id, unsigned long int col_id);
    bool validKey(unsigned long int row_id, unsigned long int col_id);
    bool writeCSV(const std::string &outfile);
    bool writeTMX(const std::string &outfile);
    void printDataFrame();
    void printCols();
    void printRows();
    void setSymmetric(bool isSymmetric);
    unsigned long int symmetricEquivalentLoc(unsigned long int row_loc, unsigned long int col_loc);
    bool readTransitCSV(const std::string& infile);
};

unsigned long int dataFrame::getRowIndexLoc(unsigned long int row_index)
{
    return rows.at(row_index);
}

unsigned long int dataFrame::getColIndexLoc(unsigned long int col_index)
{
    return cols.at(col_index);
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

void dataFrame::printCols()
{
    for (auto element : cols)
    {
        std::cout << element.first << std::endl;
    }
}

void dataFrame::printRows()
{
    for (auto element : rows)
    {
        std::cout << element.first << std::endl;
    }
}

void dataFrame::setSymmetric(bool isSymmetric)
{
    this->isSymmetric = isSymmetric;
}


void dataFrame::printDataFrame()
{

    std::cout << ",";
    for (auto col_label : col_labels)
    {
        std::cout << col_label << ",";
    }
    std::cout << std::endl;
    for (unsigned long int row_index = 0; row_index < n_rows; row_index++)
    {
        std::cout << row_labels[row_index] << ",";
        for (unsigned long int col_index = 0; col_index < n_cols; col_index++)
        {
            std::cout << this->retrieveLoc(row_index, col_index) << ","; 
        }
        std::cout << std::endl;
    }

} 


/* void constructor */
dataFrame::dataFrame() 
{
}



void printArray(const std::vector<unsigned long int> &data)
{
    for (auto element : data)
    {
        std::cout << element << std::endl;
    }
}


// use when creating a new data frame
void dataFrame::reserve(const std::vector<unsigned long int> &primary_ids, const std::vector<unsigned long int> &secondary_ids) {

    n_rows = primary_ids.size();
    n_cols = secondary_ids.size();


    unsigned long int row_id, col_id;
    for (unsigned long int row_idx = 0; row_idx < n_rows; row_idx++) {
        row_id = primary_ids.at(row_idx);
        rows[row_id] = row_idx;
        row_contents.insert(row_id);
        row_labels.push_back(row_id);
    }

    for (unsigned long int col_idx = 0; col_idx < n_cols; col_idx++) {
        col_id = secondary_ids.at(col_idx);
        cols[col_id] = col_idx;
        col_contents.insert(col_id);
        col_labels.push_back(col_id);
    }

    // determine the size of the flat array
    if (this->isSymmetric)
    {
        this->sizeOfData = n_rows * (n_rows + 1) / 2;
    }
    else
    {
        this->sizeOfData = n_rows * n_cols;
    }
    this->data.reserve(this->sizeOfData);
    for (unsigned long int i = 0; i < this->sizeOfData; i++)
    {
        this->data.push_back(UNDEFINED);
    }
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
    if (rows.find(row_id) == rows.end())
    {
        throw std::runtime_error("row_id does not exist:" + std::to_string(row_id));
    }
    if (cols.find(col_id) == cols.end())
    {
        throw std::runtime_error("col_id does not exist:" + std::to_string(col_id));
    }
    try
    {
        insertLoc(val, rows.at(row_id), cols.at(col_id));
    }
    catch (...)
    {
        auto errorMessage = "index is out of bounds:" + std::to_string(row_id) + "," + std::to_string(col_id) + "\n";
        errorMessage += "row_loc:" + std::to_string(rows.at(row_id)) + "\n";
        errorMessage += "col_loc:" + std::to_string(cols.at(col_id)) + "\n";
        if (this->isSymmetric)
        {
            if (cols.at(col_id) >= rows.at(row_id))
            {
                errorMessage += "symmetric equivalent (over diagonal):" + std::to_string(symmetricEquivalentLoc(rows.at(row_id), cols.at(col_id))) + "\n";
            }
            else
            {
                errorMessage += "symmetric equivalent (under diagonal):" + std::to_string(symmetricEquivalentLoc(cols.at(col_id), rows.at(row_id))) + "\n";   
            }
            errorMessage += "out of: " + std::to_string(this->sizeOfData) + "\n"; 
        }
        throw std::runtime_error(errorMessage);
    }
}

/* insert a value with row_id, col_id. Undefined behavior if indeces don't exist */
void dataFrame::insert(unsigned short int val, unsigned long int row_id, unsigned long int col_id) 
{
    insertLoc(val, rows.at(row_id), cols.at(col_id));

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
            this->data.at(this->symmetricEquivalentLoc(row_loc, col_loc)) = val;
        }
    }
    else
    {
        this->data.at(row_loc * n_cols + col_loc) = val;
    }
}

/* retrieve a value with row_id, col_id */
/* warning: this method is UNSAFE. Results are undefined*/
/* if keys are not present in dataframe */
/* for safe retrieval, use retrieveSafe */
unsigned short int dataFrame::retrieve(unsigned long int row_id, unsigned long int col_id) 
{
    return retrieveLoc(rows.at(row_id), cols.at(col_id));
}


/* return the value by location. Respects return the converse if symmetric
 * and below the diagonal
 */
unsigned short int dataFrame::retrieveLoc(unsigned long int row_loc, unsigned long int col_loc)
{
    if (isSymmetric)
    {
        if (col_loc >= row_loc)
        {
            return this->data.at(this->symmetricEquivalentLoc(row_loc, col_loc));
        }
        else
        {   
            return this->data.at(this->symmetricEquivalentLoc(col_loc, row_loc));   
        }
    }
    return this->data.at(row_loc * n_cols + col_loc);
}


/* check if a key pair is valid (both are in the data frame) */
bool dataFrame::validKey(unsigned long int row_id, unsigned long int col_id) 
{
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
    try
    {
        return this->retrieve(row_id, col_id);    
    }
    catch (...)
    {
        throw std::runtime_error("index is out of bounds:" + std::to_string(row_id) + "," + std::to_string(col_id));
    }
   
}



/* Write the dataFrame to a .tmx (a custom binary format) */
bool dataFrame::writeTMX(const std::string &outfile)
{
    // p2p::dataFrame df;
    // for (auto row_label : this->row_labels)
    // {
    //     df.add_row_label(row_label);
    // }
    // for (auto col_label : this->col_labels)
    // {
    //     df.add_col_label(col_label);
    // }
    // for (unsigned long int i = 0; i < n_rows; i++)
    // {
    //     auto new_row = df.add_row();
    //     for (unsigned long int j = 0; j < n_cols; j++)
    //     {
    //         new_row->add_column(this->retrieveLoc(i, j));
    //     }
    // }
    // std::fstream output(outfile, std::ios::out | std::ios::trunc | std::ios::binary);
    // if (!df.SerializeToOstream(&output)) {
    //     std::cerr << "Failed to write .tmx" << std::endl;
    //     return false;
    // }
    // output.close();
    return true;

}


/* Read the dataFrame from a .tmx (a custom binary format) */
bool dataFrame::readTMX(const std::string& infile)
{
    // p2p::dataFrame df;
    // std::fstream inputFile(infile, std::ios::in | std::ios::binary);

    // if (!df.ParseFromIstream(&inputFile)) {
    //     std::cerr << "Failed to load .tmx" << std::endl;
    //     return false;
    // }    
    // std::vector<unsigned long int> infileRowLabels;
    // std::vector<unsigned long int> infileColLabels;

    // this->n_rows = df.row_label_size();
    // this->n_cols = df.col_label_size();
    // for (unsigned long int i = 0; i < this->n_rows; i++)
    // {
    //     infileRowLabels.push_back(df.row_label(i));
    // }
    // for (unsigned long int j = 0; j < this->n_cols; j++)
    // {
    //     infileColLabels.push_back(df.col_label(j));
    // }
    // this->reserve(infileRowLabels, infileColLabels);

    // for (unsigned long int i = 0; i < this->n_rows; i++)
    // {
    //     auto matrix_row = df.row(i);
    //     for (unsigned long int j = 0; j < this->n_cols; j++)
    //     {
    //         this->insertLoc(matrix_row.column(j), i, j);
    //     }
    // }
    // inputFile.close();
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
    for (unsigned long int row_index = 0; row_index < n_rows; row_index++)
    {
        Ofile << row_labels[row_index] << ",";
        for (unsigned long int col_index = 0; col_index < n_cols; col_index++)
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
bool dataFrame::readCSV(const std::string &infile) {
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
