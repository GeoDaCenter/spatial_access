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
 dataFrame<row_label_type, col_label_type>::dataFrame(bool isSymmetric, unsigned int rows, unsigned int cols)
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
    std::cout << "dataset_size:" << dataset_size << std::endl;
}


template <class row_label_type, class col_label_type>
void dataFrame<row_label_type, col_label_type>::setRows(unsigned int rows)
{
    this->rows = rows;
}

template <class row_label_type, class col_label_type>
void dataFrame<row_label_type, col_label_type>::setCols(unsigned int cols)
{
    this->cols = cols;
}

template <class row_label_type, class col_label_type>
unsigned int dataFrame<row_label_type, col_label_type>::getRows(void) const
{
    return rows;
}

template <class row_label_type, class col_label_type>
unsigned int dataFrame<row_label_type, col_label_type>::getCols(void) const
{
    return cols;

}
template <class row_label_type, class col_label_type>
void dataFrame<row_label_type, col_label_type>::setDataset(const std::vector<std::vector<unsigned short int>>& data)
{
    this->dataset = data;
}

template <class row_label_type, class col_label_type>
const std::vector<std::vector<unsigned short int>>& dataFrame<row_label_type, col_label_type>::getDataset() const
{
    return dataset;
}

template <class row_label_type, class col_label_type>
unsigned int dataFrame<row_label_type, col_label_type>::symmetricEquivalentLoc(unsigned int row_loc, unsigned int col_loc) const
{
    unsigned int row_delta = rows - row_loc;
    return dataset_size - row_delta * (row_delta + 1) / 2 + col_loc - row_loc;
}

// Getters/Setters
template <class row_label_type, class col_label_type>
unsigned short int dataFrame<row_label_type, col_label_type>::getValueByLoc(unsigned int row_loc, unsigned int col_loc) const
{
    if (getIsSymmetric())
    {
        unsigned int index;
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
void dataFrame<row_label_type, col_label_type>::setValueById(row_label_type row_id, col_label_type col_id,
                                                             unsigned short int value)
{
    unsigned int row_loc = rowIdsToLoc.at(row_id);
    unsigned int col_loc = colIdsToLoc.at(col_id);
    setValueByLoc(row_loc, col_loc, value);
}

template <class row_label_type, class col_label_type>
unsigned short int dataFrame<row_label_type, col_label_type>::getValueById(row_label_type row_id, col_label_type col_id) const
{
    row_label_type row_loc = rowIdsToLoc(row_id);
    col_label_type col_loc = colIdsToLoc(col_id);
    return getValueByLoc(row_loc, col_loc);
}

template <class row_label_type, class col_label_type>
bool sortBySecondRows(const std::pair<row_label_type, unsigned short int> &a, const std::pair<row_label_type, unsigned short int> &b)
{
    return a.second < b.second;
}

template <class row_label_type, class col_label_type>
bool sortBySecondCols(const std::pair<col_label_type, unsigned short int> &a, const std::pair<col_label_type, unsigned short int> &b)
{
    return a.second < b.second;
}

template <class row_label_type, class col_label_type>
const std::vector<std::pair<col_label_type, unsigned short int>> dataFrame<row_label_type, col_label_type>::getValuesByRowId(row_label_type row_id,
        bool sort) const
{
    std::vector<std::pair<col_label_type, unsigned short int>> returnValue;
    unsigned int row_loc = rowIdsToLoc.at(row_id);
    for (unsigned int col_loc = 0; col_loc < getCols(); col_loc++)
    {
        returnValue.push_back(std::make_pair(colIds.at(col_loc), getValueByLoc(row_loc, col_loc)));
    }
    if (sort)
    {
        std::sort(returnValue.begin(), returnValue.end(), sortBySecondCols);
    }
    return returnValue;
}

template <class row_label_type, class col_label_type>
const std::vector<std::pair<row_label_type, unsigned short int>> dataFrame<row_label_type, col_label_type>::getValuesByColId(col_label_type col_id,
        bool sort) const
{
    std::vector<std::pair<row_label_type, unsigned short int>> returnValue;
    unsigned int col_loc = colIdsToLoc.at(col_id);
    for (unsigned int row_loc = 0; row_loc < getRows(); row_loc++)
    {
        returnValue.push_back(std::make_pair(rowIds.at(row_loc), getValueByLoc(row_loc, col_loc)));
    }
    if (sort)
    {
        std::sort(returnValue.begin(), returnValue.end(), sortBySecondRows);
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
const row_label_type& dataFrame<row_label_type, col_label_type>::getRowIdForLoc(unsigned int row_loc) const
{
    return rowIds.at(row_loc);
}

template <class row_label_type, class col_label_type>
const col_label_type& dataFrame<row_label_type, col_label_type>::getColIdForLoc(unsigned int col_loc) const
{
    return colIds.at(col_loc);
}

template <class row_label_type, class col_label_type>
unsigned int dataFrame<row_label_type, col_label_type>::getRowLocForId(row_label_type row_id) const
{
    return rowIdsToLoc.find(row_id);
}

template <class row_label_type, class col_label_type>
unsigned int dataFrame<row_label_type, col_label_type>::getColLocForId(col_label_type col_id) const
{
    return colIdsToLoc.find(col_id);
}

template <class row_label_type, class col_label_type>
void dataFrame<row_label_type, col_label_type>::setValueByLoc(unsigned int row_loc, unsigned int col_loc, unsigned short int value)
{
    if (getIsSymmetric())
    {
        unsigned int index;
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
void dataFrame<row_label_type, col_label_type>::setRowByRowLoc(const std::unordered_map<unsigned int, unsigned short int> &row_data, unsigned int source_loc)
{
    for (auto element : row_data)
    {
        this->setValueByLoc(source_loc, element.first, element.second);
    }
}

template <class row_label_type, class col_label_type>
void dataFrame<row_label_type, col_label_type>::setRowIds(const std::vector<row_label_type>& row_ids)
{
    for (unsigned int row_loc = 0; row_loc < getRows(); row_loc++)
    {
        this->rowIdsToLoc.emplace(std::make_pair(row_ids.at(row_loc), row_loc));
    }
    this->rowIds = row_ids;
}

template <class row_label_type, class col_label_type>
void dataFrame<row_label_type, col_label_type>::setColIds(const std::vector<col_label_type>& col_ids)
{
    for (unsigned int col_loc = 0; col_loc < getCols(); col_loc++)
    {
        this->colIdsToLoc.emplace(std::make_pair(col_ids.at(col_loc), col_loc));
    }
    this->colIds = col_ids;
}

template <class row_label_type, class col_label_type>
unsigned int dataFrame<row_label_type, col_label_type>::addToRowIndex(const row_label_type& row_id)
{
    rowIds.push_back(row_id);
    return rowIds.size() - 1;
}

template <class row_label_type, class col_label_type>
unsigned int dataFrame<row_label_type, col_label_type>::addToColIndex(const col_label_type& col_id)
{
    colIds.push_back(col_id);
    return colIds.size() - 1;
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
bool dataFrame<row_label_type, col_label_type>::isUnderDiagonal(unsigned int row_loc, unsigned int col_loc) const
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

    // write the top row of column labels
    for (col_label_type col_label : colIds)
    {
        streamToWrite << col_label << ",";
    }

    streamToWrite << std::endl;
    // write the body of the table, each row has a row label and values
    for (unsigned int row_loc = 0; row_loc < getRows(); row_loc++)
    {
        streamToWrite << rowIds.at(row_loc) << ",";
        for (unsigned int col_loc = 0; col_loc < getCols(); col_loc++)
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
