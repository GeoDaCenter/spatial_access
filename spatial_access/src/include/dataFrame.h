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
#include <limits>

#include "Serializer.h"
#include "tmxParser.h"
#include "csvParser.h"
#include "otpCSV.h"

#define TMX_VERSION (2)

/* a pandas-like dataFrame */
template <class row_label_type, class col_label_type, class value_type>
class dataFrame {
public:
    static constexpr value_type UNDEFINED = std::numeric_limits<value_type>::max();
    std::vector<std::vector<value_type>> dataset;
    bool isCompressible;
    bool isSymmetric;
    unsigned long int rows;
    unsigned long int cols;
    std::vector<row_label_type> rowIds;
    std::vector<col_label_type> colIds; // TODO: eliminate redundant labels if symmetric
    std::unordered_map<row_label_type, unsigned long int> rowIdsToLoc;
    std::unordered_map<col_label_type, unsigned long int> colIdsToLoc;
    unsigned long int dataset_size;

private:
    void indexRows()
    {
        for (unsigned long int row_loc = 0; row_loc < rows; row_loc++)
        {
            this->rowIdsToLoc.emplace(std::make_pair(rowIds.at(row_loc), row_loc));
        }
    }

    void indexCols()
    {
        for (unsigned long int col_loc = 0; col_loc < cols; col_loc++)
        {
            this->colIdsToLoc.emplace(std::make_pair(colIds.at(col_loc), col_loc));
        }
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
    void readOTPCSV(const std::string& filename)
    {
        isCompressible = false;
        isSymmetric = false;
        otpCSVReader<row_label_type, col_label_type, value_type> reader(filename);
        auto reader_row_labels = reader.row_labels;
        auto reader_col_labels = reader.col_labels;

        std::unordered_set<row_label_type> unique_row_labels_set(reader_row_labels.begin(), reader_row_labels.end());
        std::unordered_set<col_label_type> unique_col_labels_set(reader_col_labels.begin(), reader_col_labels.end());

        rowIds.assign(unique_row_labels_set.begin(), unique_row_labels_set.end());
        colIds.assign(unique_col_labels_set.begin(), unique_col_labels_set.end());
        this->rows = rowIds.size();
        this->cols = colIds.size();
        indexRows();
        indexCols();
        initializeDatatsetSize();

        for (unsigned int row_loc = 0; row_loc < rows; row_loc++)
        {
            std::vector<value_type> data(cols, UNDEFINED);
            dataset.push_back(data);
        }
        for (unsigned long int i = 0; i < reader.data.size(); i++)
        {
            setValueById(reader_row_labels.at(i), reader_col_labels.at(i), reader.data.at(i));
        }

    }

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
            std::vector<value_type> data(dataset_size, UNDEFINED);
            dataset.push_back(data);
        }
        else
        {
            this->cols = cols;
            initializeDatatsetSize();
            for (unsigned int row_loc = 0; row_loc < rows; row_loc++)
            {
                std::vector<value_type> data(cols, UNDEFINED);
                dataset.push_back(data);
            }
        }

    }

    void setMockDataFrame(const std::vector<std::vector<value_type>>& dataset,
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

    value_type
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


    value_type
    getValueById(const row_label_type& row_id, const col_label_type& col_id) const
    {
        unsigned long int row_loc = rowIdsToLoc.at(row_id);
        unsigned long int col_loc = colIdsToLoc.at(col_id);
        return getValueByLoc(row_loc, col_loc);
    }

    void
    setValueById(const row_label_type& row_id, const col_label_type& col_id, value_type value)
    {
        unsigned long int row_loc = rowIdsToLoc.at(row_id);
        unsigned long int col_loc = colIdsToLoc.at(col_id);
        setValueByLoc(row_loc, col_loc, value);
    }


    const std::vector<std::pair<col_label_type, value_type>>
    getValuesByRowId(const row_label_type& row_id, bool sort) const
    {
        std::vector<std::pair<col_label_type, value_type>> returnValue;
        unsigned long int row_loc = rowIdsToLoc.at(row_id);
        for (unsigned long int col_loc = 0; col_loc < cols; col_loc++)
        {
            returnValue.push_back(std::make_pair(colIds.at(col_loc), getValueByLoc(row_loc, col_loc)));
        }
        if (sort)
        {
            std::sort(returnValue.begin(), returnValue.end(), [](std::pair<col_label_type, value_type> &left, std::pair<col_label_type, value_type> &right) {
                return left.second < right.second;
            });
        }
        return returnValue;
    }


    const std::vector<std::pair<row_label_type, value_type>>
    getValuesByColId(const col_label_type& col_id, bool sort) const
    {
        std::vector<std::pair<row_label_type, value_type>> returnValue;
        unsigned long int col_loc = colIdsToLoc.at(col_id);
        for (unsigned long int row_loc = 0; row_loc < rows; row_loc++)
        {
            returnValue.push_back(std::make_pair(rowIds.at(row_loc), getValueByLoc(row_loc, col_loc)));
        }
        if (sort)
        {
            std::sort(returnValue.begin(), returnValue.end(), [](std::pair<row_label_type, value_type> &left, std::pair<row_label_type, value_type> &right) {
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
    setValueByLoc(unsigned long int row_loc, unsigned long int col_loc, value_type value)
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
    setRowByRowLoc(const std::vector<value_type> &row_data, unsigned long int source_loc)
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
        this->rowIds = row_ids;
        indexRows();
    }


    void
    setColIds(const std::vector<col_label_type>& col_ids)
    {
        this->colIds = col_ids;
        indexCols();
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

    void readCSV(const std::string& infile)
    {
        isCompressible = false;
        isSymmetric = false;
        std::ifstream fileIN;
        fileIN.open(infile);
        if (fileIN.fail())
        {
            throw std::runtime_error("unable to read file");
        }

        csvParser<row_label_type> rowReader(fileIN);
        csvParser<col_label_type> colReader(fileIN);
        csvParser<value_type> valueReader(fileIN);

        colReader.readLine(colIds);
        indexCols();

        std::string line;
        std::string row_label;
        std::string value;

        while (getline(fileIN, line))
        {
            this->dataset.emplace_back(std::vector<value_type>());
            std::istringstream stream(line);

            getline(stream, row_label,',');
            rowIds.push_back(rowReader.parse(row_label));
            while(getline(stream, value, ','))
            {
                this->dataset.at(this->dataset.size() - 1).push_back(valueReader.parse(value));
            }
        }
        fileIN.close();
        rows = this->rowIds.size();
        cols = this->colIds.size();
        indexRows();
        initializeDatatsetSize();
    }


    void writeTMX(const std::string& filename) const
    {
        Serializer serializer(filename);
        tmxWriter<row_label_type> rowWriter(serializer);
        tmxWriter<col_label_type> colWriter(serializer);
        tmxWriter<value_type> dataWriter(serializer);

        rowWriter.writeTMXVersion(TMX_VERSION);
        rowWriter.writeIdTypeEnum();
        colWriter.writeIdTypeEnum();
        dataWriter.writeValueTypeEnum();

        rowWriter.writeIsCompressible(isCompressible);
        rowWriter.writeIsSymmetric(isSymmetric);

        rowWriter.writeNumberOfRows(rows);
        colWriter.writeNumberOfCols(cols);

        rowWriter.writeIds(rowIds);
        colWriter.writeIds(colIds);
        dataWriter.writeData(dataset);
    }

    void readTMX(const std::string& filename)
    {
        Deserializer deserializer(filename);

        tmxReader<row_label_type> rowReader(deserializer);
        tmxReader<col_label_type> colReader(deserializer);
        tmxReader<value_type> dataReader(deserializer);

        auto tmx_version = rowReader.readTMXVersion();
        if (tmx_version != TMX_VERSION)
        {
            auto error = std::string("file is an older version of tmx: ") + std::to_string(tmx_version);
            error += std::string("expected: ") + std::to_string(TMX_VERSION);
            throw std::runtime_error(error);
        }

        // row_enum_type
        rowReader.readIdTypeEnum();

        // col_enum_type
        colReader.readIdTypeEnum();

        // value_enum_type
        dataReader.readValueTypeEnum();

        isCompressible = rowReader.readIsCompressible();
        isSymmetric = rowReader.readIsSymmetric();

        rows = rowReader.readNumberOfRows();
        cols = colReader.readNumberOfCols();

        rowReader.readIds(rowIds);
        colReader.readIds(colIds);
        dataReader.readData(dataset);

        indexRows();
        indexCols();
        initializeDatatsetSize();

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
                value_type value = this->getValueByLoc(row_loc, col_loc);
                if (value < UNDEFINED) {
                    streamToWrite << value << ",";
                } else {
                    streamToWrite << "-1" << ",";
                }
            }
            streamToWrite << std::endl;
        }
        return true;
    }


public:
// Utilities

    bool
    isUnderDiagonal(unsigned long int row_loc, unsigned long int col_loc) const
    {
        return row_loc > col_loc;
    }

};
