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
    dataFrame(bool isSymmetric, unsigned int rows, unsigned int cols);
    
    // Getters:
    unsigned short int getValueByLoc(unsigned int row_loc, unsigned int col_loc) const;
    unsigned short int getValueById(const row_label_type& row_id, const col_label_type& col_id) const;

    bool getIsSymmetric() const;
    unsigned int getRows() const;
    unsigned int getCols() const;
    const std::vector<std::pair<col_label_type, unsigned short int>> getValuesByRowId(const row_label_type &row_id, bool sort) const;
    const std::vector<std::pair<row_label_type, unsigned short int>> getValuesByColId(const col_label_type &col_id, bool sort) const;
    const std::vector<row_label_type>& getRowIds() const;
    const std::vector<col_label_type>& getColIds() const;
    const row_label_type& getRowIdForLoc(unsigned int row_loc) const;
    const col_label_type& getColIdForLoc(unsigned int col_loc) const;
    unsigned int getRowLocForId(const row_label_type& row_id) const;
    unsigned int getColLocForId(const col_label_type& col_id) const;
    const std::vector<unsigned short int>& getDatasetRow(unsigned int row) const;
    const std::vector<std::vector<unsigned short int>>& getDataset() const;

    // Setters
    void setValueByLoc(unsigned int row_loc, unsigned int col_loc, unsigned short int value);
    void setValueById(const row_label_type& row_id, const col_label_type& col_id, unsigned short int value);
    void setIsSymmetric(bool isSymmetric);
    void setRows(unsigned int rows);
    void setCols(unsigned int cols);
    void setRowByRowLoc(const std::vector<unsigned short int> &row_data, unsigned int row_loc);
    void setRowIds(const std::vector<row_label_type>& row_ids);
    void setColIds(const std::vector<col_label_type>& col_ids);
    unsigned int addToRowIndex(const row_label_type& row_id);
    unsigned int addToColIndex(const col_label_type& col_id);
    void setDatasetRow(const std::vector<unsigned short int>& datasetRow, unsigned int row);
    void setDataset(const std::vector<std::vector<unsigned short int>>& dataset);

    // Input/Output:
    bool writeCSV(const std::string &outfile) const;
    void printDataFrame() const;

    // Utility
    bool isUnderDiagonal(unsigned int row_loc, unsigned int col_loc) const;


private:
    // Input/Output
    bool writeToStream(std::ostream& streamToWrite) const;

    // Private Members
    bool isSymmetric;
    unsigned int rows;
    unsigned int cols;
    std::vector<row_label_type> rowIds;
    std::vector<col_label_type> colIds;

    std::unordered_map<row_label_type, unsigned int> rowIdsToLoc;
    std::unordered_map<col_label_type, unsigned int> colIdsToLoc;

    // Utility
    unsigned int symmetricEquivalentLoc(unsigned int row_loc, unsigned int col_loc) const;
    unsigned int dataset_size;
};
