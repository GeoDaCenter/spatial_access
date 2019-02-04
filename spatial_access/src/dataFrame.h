#pragma once
#include <unordered_map>

#include "protobuf/p2p.pb.h"

/* a pandas-like dataFrame */
class dataFrame {
public:
    std::unordered_map <unsigned long int, p2p::dataRow> row_id_map;

    // Map the column id to a location in an array
    std::unordered_map<unsigned long int, unsigned long int> col_id_to_loc;

    p2p::metaData metaData;

public:

    // Initialization:
    dataFrame();
    void reserve(const std::vector<unsigned long int> &primary_ids, const std::vector<unsigned long int> &secondary_ids);
    
    // Getters and Setters:
    unsigned short int retrieveValue(unsigned long int row_id, unsigned long int col_id) const;
    void insertValue(unsigned short int value, unsigned long int row_id, unsigned long int col_id);
    bool isSymmetric() const;
    void setSymmetric(bool isSymmetric);
    void insertRow(const std::unordered_map<unsigned long int, unsigned short int> &row_data, unsigned long int source_id);
    const std::vector<std::pair<unsigned long int, unsigned short int>> getValuesByRow(unsigned long int row_id, bool sort);
    const std::vector<std::pair<unsigned long int, unsigned short int>> getValuesByCol(unsigned long int row_id, bool sort);
    unsigned long int cacheUserStringId(const std::string& user_string_id, bool isRow);
    std::unordered_map<std::string, unsigned long int> getUserRowIdCache() const;
    std::unordered_map<std::string, unsigned long int> getUserColIdCache() const;

    // Input/Output:
    bool readCSV(const std::string &infile);
    bool readTMX(const std::string &infile);
    bool writeCSV(const std::string &outfile) const;
    bool writeTMX(const std::string &outfile) const;
    bool writeMetadata(const std::string &outfile) const;
    bool writeRowdata(const std::string &outfile, unsigned long int row_id) const;
    bool readMetadata(const std::string &outfile);
    bool readRowdata(const std::string &outfile, unsigned long int row_id);
    void printDataFrame() const;
    bool readOTPMatrix(const std::string& infile);

    // Utility
    bool isUnderDiagonal(unsigned long int row_id, unsigned long int col_id) const;

private:
    // Input/Output
    bool writeToStream(std::ostream& streamToWrite) const;

    unsigned long int row_label_remap_counter;
    unsigned long int col_label_remap_counter;

};
