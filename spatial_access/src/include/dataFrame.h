// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#pragma once

#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <iostream>
#include <string>
#include <stdexcept>
#include <algorithm>
#include <climits>

#include "Serializer.h"
#include "otpCSV.h"

#define UNDEFINED (USHRT_MAX)
#define TMX_VERSION (1)

/* a pandas-like dataFrame */
template <class row_label_type, class col_label_type>
class dataFrame {
private:
    enum Type {
        IxI,
        IxS,
        SxI,
        SxS
    };

public:

    // Public Members
    std::vector<std::vector<unsigned short int>> dataset;
    bool isCompressible;
    bool isSymmetric;
    unsigned long int rows;
    unsigned long int cols;
    std::vector<row_label_type> rowIds;
    std::vector<col_label_type> colIds; // TODO: eliminate redundant labels if symmetric
    std::unordered_map<row_label_type, unsigned long int> rowIdsToLoc;
    std::unordered_map<col_label_type, unsigned long int> colIdsToLoc;
    unsigned long int dataset_size;

    // Specialized Methods
    void writeTMX(const std::string& filename) const;
    void readTMX(const std::string& filename);
    void readOTPCSV(const std::string& filename);

    // Methods
    dataFrame() = default;
    dataFrame(bool isCompressible, bool isSymmetric, unsigned long int rows, unsigned long int cols)
    {
        this->isCompressible = isCompressible;
        this->isSymmetric = isSymmetric;
        this->rows = rows;
        if (isCompressible)
        {
            this->cols = rows;
            initializeDatatsetSize();
            std::vector<unsigned short int> data(dataset_size, UNDEFINED);
            dataset.push_back(data);
        }
        else
        {
            this->cols = cols;
            initializeDatatsetSize();
            for (unsigned int row_loc = 0; row_loc < rows; row_loc++)
            {
                std::vector<unsigned short int> data(cols, UNDEFINED);
                dataset.push_back(data);
            }
        }

    }

    void setMockDataFrame(const std::vector<std::vector<unsigned short int>>& dataset,
                          const std::vector<row_label_type>& row_ids,
                          const std::vector<col_label_type>& col_ids)
    {
        setRowIds(row_ids);
        setColIds(col_ids);
        for (unsigned long int i = 0; i < row_ids.size(); i++)
        {
            setRowByRowLoc(dataset.at(i), i);
        }

    }

    unsigned long int
    compressedEquivalentLoc(unsigned long int row_loc, unsigned long int col_loc) const
    {
        unsigned long int row_delta = rows - row_loc;
        return dataset_size - row_delta * (row_delta + 1) / 2 + col_loc - row_loc;
    }

// Getters/Setters

    unsigned short int
    getValueByLoc(unsigned long int row_loc, unsigned long int col_loc) const
    {
        if (isCompressible)
        {
            unsigned long int index;
            if (isUnderDiagonal(row_loc, col_loc))
            {
                index = compressedEquivalentLoc(col_loc, row_loc);
            } else
            {
                index = compressedEquivalentLoc(row_loc, col_loc);
            }
            return dataset.at(0).at(index);
        }
        return dataset.at(row_loc).at(col_loc);
    }


    unsigned short int
    getValueById(const row_label_type& row_id, const col_label_type& col_id) const
    {
        unsigned long int row_loc = rowIdsToLoc.at(row_id);
        unsigned long int col_loc = colIdsToLoc.at(col_id);
        return getValueByLoc(row_loc, col_loc);
    }

    void
    setValueById(const row_label_type& row_id, const col_label_type& col_id, unsigned short int value)
    {
        unsigned long int row_loc = rowIdsToLoc.at(row_id);
        unsigned long int col_loc = colIdsToLoc.at(col_id);
        setValueByLoc(row_loc, col_loc, value);
    }


    const std::vector<std::pair<col_label_type, unsigned short int>>
    getValuesByRowId(const row_label_type& row_id, bool sort) const
    {
        std::vector<std::pair<col_label_type, unsigned short int>> returnValue;
        unsigned long int row_loc = rowIdsToLoc.at(row_id);
        for (unsigned long int col_loc = 0; col_loc < cols; col_loc++)
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


    const std::vector<std::pair<row_label_type, unsigned short int>>
    getValuesByColId(const col_label_type& col_id, bool sort) const
    {
        std::vector<std::pair<row_label_type, unsigned short int>> returnValue;
        unsigned long int col_loc = colIdsToLoc.at(col_id);
        for (unsigned long int row_loc = 0; row_loc < rows; row_loc++)
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


    const std::vector<row_label_type>&
    getRowIds() const
    {
        return rowIds;
    }


    const std::vector<col_label_type>&
    getColIds() const
    {
        return colIds;
    }


    const row_label_type&
    getRowIdForLoc(unsigned long int row_loc) const
    {
        return rowIds.at(row_loc);
    }


    const col_label_type&
    getColIdForLoc(unsigned long int col_loc) const
    {
        return colIds.at(col_loc);
    }


    unsigned long int
    getRowLocForId(const row_label_type& row_id) const
    {
        return rowIdsToLoc.at(row_id);
    }


    unsigned long int
    getColLocForId(const col_label_type& col_id) const
    {
        return colIdsToLoc.at(col_id);
    }


    void
    setValueByLoc(unsigned long int row_loc, unsigned long int col_loc, unsigned short int value)
    {
        if (isCompressible)
        {
            unsigned long int index;
            if (isUnderDiagonal(row_loc, col_loc))
            {
                index = compressedEquivalentLoc(col_loc, row_loc);
            } else
            {
                index = compressedEquivalentLoc(row_loc, col_loc);
            }
            dataset.at(0).at(index) = value;
            return;
        }
        dataset.at(row_loc).at(col_loc) = value;
    }


    void
    setRowByRowLoc(const std::vector<unsigned short int> &row_data, unsigned long int source_loc)
    {
        if (source_loc > rows)
        {
            throw std::runtime_error("row loc exceeds index of dataframe");
        }
        if (!isCompressible)
        {

            this->dataset.at(source_loc) = row_data;

        }
        else
        {
            unsigned long int left_index = this->compressedEquivalentLoc(source_loc, source_loc);
            std::copy(row_data.begin(), row_data.end(), this->dataset.at(0).begin() + left_index);

        }
    }


    void
    setRowIds(const std::vector<row_label_type>& row_ids)
    {
        for (unsigned long int row_loc = 0; row_loc < rows; row_loc++)
        {
            this->rowIdsToLoc.emplace(std::make_pair(row_ids.at(row_loc), row_loc));
        }
        this->rowIds = row_ids;
    }


    void
    setColIds(const std::vector<col_label_type>& col_ids)
    {
        for (unsigned long int col_loc = 0; col_loc < cols; col_loc++)
        {
            this->colIdsToLoc.emplace(std::make_pair(col_ids.at(col_loc), col_loc));
        }
        this->colIds = col_ids;
    }


    unsigned long int
    addToRowIndex(const row_label_type& row_id)
    {
        unsigned long int index = rowIds.size();
        rowIds.push_back(row_id);
        rowIdsToLoc.emplace(std::make_pair(row_id, index));
        return index;
    }


    unsigned long int
    addToColIndex(const col_label_type& col_id)
    {
        unsigned long int index = colIds.size();
        colIds.push_back(col_id);
        colIdsToLoc.emplace(std::make_pair(col_id, index));
        return index;
    }



// Input/Output:

    bool
    writeCSV(const std::string &outfile) const
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

    void
    printDataFrame() const
    {
        writeToStream(std::cout);
    }

private:
    bool
    writeToStream(std::ostream& streamToWrite) const
    {

        streamToWrite << ",";
        // write the top row of column labels
        for (col_label_type col_label : colIds)
        {
            streamToWrite << col_label << ",";
        }

        streamToWrite << std::endl;
        // write the body of the table, each row has a row label and values
        for (unsigned long int row_loc = 0; row_loc < rows; row_loc++)
        {
            streamToWrite << rowIds.at(row_loc) << ",";
            for (unsigned long int col_loc = 0; col_loc < cols; col_loc++)
            {
                streamToWrite << this->getValueByLoc(row_loc, col_loc) << ",";
            }
            streamToWrite << std::endl;
        }
        return true;
    }

    void writeTMXHeader(Serializer& s, Type mode) const
    {

        s.writeShortInt(TMX_VERSION);

        s.writeShortInt(mode);

        s.writeShortInt(isCompressible);

        s.writeShortInt(isSymmetric);

        s.writeLongInt(rows);

        s.writeLongInt(cols);
    }

    void readTMXHeader(Deserializer& d, Type expected_mode)
    {
        auto tmx_version = d.readShortInt();

        if (tmx_version != TMX_VERSION)
        {
            auto error = std::string("file is an older version of tmx: ") + std::to_string(tmx_version);
            error += std::string("expected: ") + std::to_string(TMX_VERSION);
            throw std::runtime_error(error);
        }

        auto mode = (Type) d.readShortInt();

        if (mode != expected_mode) {
            throw std::runtime_error("Unexpected mode");
        }

        // isCompressible
        isCompressible = (bool) d.readShortInt();

        // isSymmetric
        isSymmetric = (bool) d.readShortInt();

        // rows
        rows = d.readLongInt();

        // cols
        cols = d.readLongInt();
    }

    void initializeDatatsetSize()
    {
        if (isCompressible) {
            dataset_size = (rows * (rows + 1)) / 2;
        }
        else {
            dataset_size = rows * cols;
        }
    }

public:
// Utilities


    bool
    isUnderDiagonal(unsigned long int row_loc, unsigned long int col_loc) const
    {
        return row_loc > col_loc;
    }

};
