#include <sstream>
#include <iostream>
#include <fstream>
#include <string>
#include <unordered_map>
#include <stdexcept>
#include <vector>
#include <algorithm>
#include <sys/stat.h>

#include "dataFrame.h"
#include <climits>

#define UNDEFINED (USHRT_MAX)

// Initialization:
template <class row_label_type, class col_label_type>
 dataFrame<row_label_type, col_label_type>::dataFrame(bool isSymmetric, unsigned long int rows, unsigned long int cols)
{
    setIsSymmetric(isSymmetric);
    setRows(rows);

    if (isSymmetric)
    {

        setCols(rows);
        dataset_size = (rows * (rows + 1)) / 2;
        std::vector<unsigned short int> data(dataset_size, UNDEFINED);
        dataset.push_back(data);
    }
    else
    {

        dataset_size = rows * cols;
        setCols(cols);
        for (unsigned int row_loc = 0; row_loc < rows; row_loc++)
        {
            std::vector<unsigned short int> data(cols, UNDEFINED);
            dataset.push_back(data);
        }
    }

}


template <class row_label_type, class col_label_type>
void dataFrame<row_label_type, col_label_type>::setRows(unsigned long int rows)
{
    this->rows = rows;
}

template <class row_label_type, class col_label_type>
void dataFrame<row_label_type, col_label_type>::setCols(unsigned long int cols)
{
    this->cols = cols;
}

template <class row_label_type, class col_label_type>
unsigned long int dataFrame<row_label_type, col_label_type>::getRows() const
{
    return rows;
}

template <class row_label_type, class col_label_type>
unsigned long int dataFrame<row_label_type, col_label_type>::getCols() const
{
    return cols;

}

template <class row_label_type, class col_label_type>
void dataFrame<row_label_type, col_label_type>::setDataset(const std::vector<std::vector<unsigned short int>>& dataset)
{
    this->dataset = dataset;
}

template <class row_label_type, class col_label_type>
void dataFrame<row_label_type, col_label_type>::setDatasetRow(const std::vector<unsigned short int>& datasetRow, unsigned long int row)
{
    this->dataset.at(row) = datasetRow;
}


template <class row_label_type, class col_label_type>
const std::vector<unsigned short int>& dataFrame<row_label_type, col_label_type>::getDatasetRow(unsigned long int row) const
{
    return dataset.at(row);
}

template <class row_label_type, class col_label_type>
const std::vector<std::vector<unsigned short int>>& dataFrame<row_label_type, col_label_type>::getDataset() const
{
    return dataset;
}

template <class row_label_type, class col_label_type>
unsigned long int dataFrame<row_label_type, col_label_type>::symmetricEquivalentLoc(unsigned long int row_loc, unsigned long int col_loc) const
{
    unsigned long int row_delta = rows - row_loc;
    return dataset_size - row_delta * (row_delta + 1) / 2 + col_loc - row_loc;
}

// Getters/Setters
template <class row_label_type, class col_label_type>
unsigned short int dataFrame<row_label_type, col_label_type>::getValueByLoc(unsigned long int row_loc, unsigned long int col_loc) const
{
    if (getIsSymmetric())
    {
        unsigned long int index;
        if (isUnderDiagonal(row_loc, col_loc))
        {
            index = symmetricEquivalentLoc(col_loc, row_loc);
        } else
        {
            index = symmetricEquivalentLoc(row_loc, col_loc);
        }
        return dataset.at(0).at(index);
    }
    return dataset.at(row_loc).at(col_loc);
}

template <class row_label_type, class col_label_type>
void dataFrame<row_label_type, col_label_type>::setValueById(const row_label_type& row_id, const col_label_type& col_id,
                                                             unsigned short int value)
{
    unsigned long int row_loc = rowIdsToLoc.at(row_id);
    unsigned long int col_loc = colIdsToLoc.at(col_id);
    setValueByLoc(row_loc, col_loc, value);
}

template <class row_label_type, class col_label_type>
unsigned short int dataFrame<row_label_type, col_label_type>::getValueById(const row_label_type& row_id, const col_label_type& col_id) const
{
    unsigned long int row_loc = rowIdsToLoc.at(row_id);
    unsigned long int col_loc = colIdsToLoc.at(col_id);
    return getValueByLoc(row_loc, col_loc);
}

template <class row_label_type, class col_label_type>
const std::vector<std::pair<col_label_type, unsigned short int>> dataFrame<row_label_type, col_label_type>::getValuesByRowId(const row_label_type& row_id,
        bool sort) const
{
    std::vector<std::pair<col_label_type, unsigned short int>> returnValue;
    unsigned long int row_loc = rowIdsToLoc.at(row_id);
    for (unsigned long int col_loc = 0; col_loc < getCols(); col_loc++)
    {
        returnValue.push_back(std::make_pair(colIds.at(col_loc), getValueByLoc(row_loc, col_loc)));
    }
    if (sort)
    {
        std::sort(returnValue.begin(), returnValue.end(), [](std::pair<col_label_type, unsigned short int> &left, std::pair<col_label_type, unsigned short int> &right) {
            return left.second < right.second;
        });
    }
    return returnValue;
}

template <class row_label_type, class col_label_type>
const std::vector<std::pair<row_label_type, unsigned short int>> dataFrame<row_label_type, col_label_type>::getValuesByColId(const col_label_type& col_id,
        bool sort) const
{
    std::vector<std::pair<row_label_type, unsigned short int>> returnValue;
    unsigned long int col_loc = colIdsToLoc.at(col_id);
    for (unsigned long int row_loc = 0; row_loc < getRows(); row_loc++)
    {
        returnValue.push_back(std::make_pair(rowIds.at(row_loc), getValueByLoc(row_loc, col_loc)));
    }
    if (sort)
    {
        std::sort(returnValue.begin(), returnValue.end(), [](std::pair<row_label_type, unsigned short int> &left, std::pair<row_label_type, unsigned short int> &right) {
            return left.second < right.second;
        });
    }
    return returnValue;
}

template <class row_label_type, class col_label_type>
const std::vector<row_label_type>& dataFrame<row_label_type, col_label_type>::getRowIds() const
{
    return rowIds;
}

template <class row_label_type, class col_label_type>
const std::vector<col_label_type>& dataFrame<row_label_type, col_label_type>::getColIds() const
{
    return colIds;
}

template <class row_label_type, class col_label_type>
const row_label_type& dataFrame<row_label_type, col_label_type>::getRowIdForLoc(unsigned long int row_loc) const
{
    return rowIds.at(row_loc);
}

template <class row_label_type, class col_label_type>
const col_label_type& dataFrame<row_label_type, col_label_type>::getColIdForLoc(unsigned long int col_loc) const
{
    return colIds.at(col_loc);
}

template <class row_label_type, class col_label_type>
unsigned long int dataFrame<row_label_type, col_label_type>::getRowLocForId(const row_label_type& row_id) const
{
    return rowIdsToLoc.at(row_id);
}

template <class row_label_type, class col_label_type>
unsigned long int dataFrame<row_label_type, col_label_type>::getColLocForId(const col_label_type& col_id) const
{
    return colIdsToLoc.at(col_id);
}

template <class row_label_type, class col_label_type>
void dataFrame<row_label_type, col_label_type>::setValueByLoc(unsigned long int row_loc, unsigned long int col_loc, unsigned short int value)
{
    if (getIsSymmetric())
    {
        unsigned long int index;
        if (isUnderDiagonal(row_loc, col_loc))
        {
            index = symmetricEquivalentLoc(col_loc, row_loc);
        } else
        {
            index = symmetricEquivalentLoc(row_loc, col_loc);
        }
        dataset.at(0).at(index) = value;
        return;
    }
    dataset.at(row_loc).at(col_loc) = value;
}

template <class row_label_type, class col_label_type>
void dataFrame<row_label_type, col_label_type>::setRowByRowLoc(const std::vector<unsigned short int> &row_data, unsigned long int source_loc)
{
    if (source_loc > getRows())
    {
        throw std::runtime_error("row loc exceeds index of dataframe");
    }
    if (!getIsSymmetric())
    {

        this->dataset.at(source_loc) = row_data;

    }
    else
    {

        unsigned long int left_index = this->symmetricEquivalentLoc(source_loc, source_loc);
        std::copy(row_data.begin(), row_data.end(), this->dataset.at(0).begin() + left_index);

    }
}

template <class row_label_type, class col_label_type>
void dataFrame<row_label_type, col_label_type>::setRowIds(const std::vector<row_label_type>& row_ids)
{
    for (unsigned long int row_loc = 0; row_loc < getRows(); row_loc++)
    {
        this->rowIdsToLoc.emplace(std::make_pair(row_ids.at(row_loc), row_loc));
    }
    this->rowIds = row_ids;
}

template <class row_label_type, class col_label_type>
void dataFrame<row_label_type, col_label_type>::setColIds(const std::vector<col_label_type>& col_ids)
{
    for (unsigned long int col_loc = 0; col_loc < getCols(); col_loc++)
    {
        this->colIdsToLoc.emplace(std::make_pair(col_ids.at(col_loc), col_loc));
    }
    this->colIds = col_ids;
}

template <class row_label_type, class col_label_type>
unsigned long int dataFrame<row_label_type, col_label_type>::addToRowIndex(const row_label_type& row_id)
{
    unsigned long int index = rowIds.size();
    rowIds.push_back(row_id);
    rowIdsToLoc.emplace(std::make_pair(row_id, index));
    return index;
}

template <class row_label_type, class col_label_type>
unsigned long int dataFrame<row_label_type, col_label_type>::addToColIndex(const col_label_type& col_id)
{
    unsigned long int index = colIds.size();
    colIds.push_back(col_id);
    colIdsToLoc.emplace(std::make_pair(col_id, index));
    return index;
}

template <class row_label_type, class col_label_type>
bool dataFrame<row_label_type, col_label_type>::getIsSymmetric() const {
    return isSymmetric;
}

template <class row_label_type, class col_label_type>
void dataFrame<row_label_type, col_label_type>::setIsSymmetric(bool isSymmetric)
{
    this->isSymmetric = isSymmetric;
}

// Utilities

template <class row_label_type, class col_label_type>
bool dataFrame<row_label_type, col_label_type>::isUnderDiagonal(unsigned long int row_loc, unsigned long int col_loc) const
{
    return row_loc > col_loc;
}



// Input/Output:
template <class row_label_type, class col_label_type>
bool dataFrame<row_label_type, col_label_type>::writeCSV(const std::string &outfile) const
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

template <class row_label_type, class col_label_type>
bool dataFrame<row_label_type, col_label_type>::writeToStream(std::ostream& streamToWrite) const
{

    streamToWrite << ",";
    // write the top row of column labels
    for (col_label_type col_label : colIds)
    {
        streamToWrite << col_label << ",";
    }

    streamToWrite << std::endl;
    // write the body of the table, each row has a row label and values
    for (unsigned long int row_loc = 0; row_loc < getRows(); row_loc++)
    {
        streamToWrite << rowIds.at(row_loc) << ",";
        for (unsigned long int col_loc = 0; col_loc < getCols(); col_loc++)
        {
            streamToWrite << this->getValueByLoc(row_loc, col_loc) << ",";
        }
        streamToWrite << std::endl;
    }



    return true;
}

template <class row_label_type, class col_label_type>
void dataFrame<row_label_type, col_label_type>::printDataFrame() const
{
    writeToStream(std::cout);
}
