// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#pragma once
#include <unordered_map>
#include <vector>


/* a pandas-like dataFrame */
template <class row_label_type, class col_label_type>
class dataFrame {

public:
    // Public Members
    std::vector<std::vector<unsigned short int>> dataset;

    // Initialization:
    dataFrame(bool isSymmetric, unsigned long int rows, unsigned long int cols);
    
    // Getters:
    unsigned short int getValueByLoc(unsigned long int row_loc, unsigned long int col_loc) const;
    unsigned short int getValueById(const row_label_type& row_id, const col_label_type& col_id) const;

    bool getIsSymmetric() const;
    unsigned long int getRows() const;
    unsigned long int getCols() const;
    const std::vector<std::pair<col_label_type, unsigned short int>> getValuesByRowId(const row_label_type &row_id, bool sort) const;
    const std::vector<std::pair<row_label_type, unsigned short int>> getValuesByColId(const col_label_type &col_id, bool sort) const;
    const std::vector<row_label_type>& getRowIds() const;
    const std::vector<col_label_type>& getColIds() const;
    const row_label_type& getRowIdForLoc(unsigned long int row_loc) const;
    const col_label_type& getColIdForLoc(unsigned long int col_loc) const;
    unsigned long int getRowLocForId(const row_label_type& row_id) const;
    unsigned long int getColLocForId(const col_label_type& col_id) const;
    const std::vector<unsigned short int>& getDatasetRow(unsigned long int row) const;
    const std::vector<std::vector<unsigned short int>>& getDataset() const;

    // Setters
    void setValueByLoc(unsigned long int row_loc, unsigned long int col_loc, unsigned short int value);
    void setValueById(const row_label_type& row_id, const col_label_type& col_id, unsigned short int value);
    void setIsSymmetric(bool isSymmetric);
    void setRows(unsigned long int rows);
    void setCols(unsigned long int cols);
    void setRowByRowLoc(const std::vector<unsigned short int> &row_data, unsigned long int row_loc);
    void setRowIds(const std::vector<row_label_type>& row_ids);
    void setColIds(const std::vector<col_label_type>& col_ids);
    unsigned long int addToRowIndex(const row_label_type& row_id);
    unsigned long int addToColIndex(const col_label_type& col_id);
    void setDatasetRow(const std::vector<unsigned short int>& datasetRow, unsigned long int row);
    void setDataset(const std::vector<std::vector<unsigned short int>>& dataset);

    // Input/Output:
    bool writeCSV(const std::string &outfile) const;
    void printDataFrame() const;

    // Utility
    bool isUnderDiagonal(unsigned long int row_loc, unsigned long int col_loc) const;


private:
    // Input/Output
    bool writeToStream(std::ostream& streamToWrite) const;

    // Private Members
    bool isSymmetric;
    unsigned long int rows;
    unsigned long int cols;
    std::vector<row_label_type> rowIds;
    std::vector<col_label_type> colIds;

    std::unordered_map<row_label_type, unsigned long int> rowIdsToLoc;
    std::unordered_map<col_label_type, unsigned long int> colIdsToLoc;

    // Utility
    unsigned long int symmetricEquivalentLoc(unsigned long int row_loc, unsigned long int col_loc) const;
    unsigned long int dataset_size;
};
