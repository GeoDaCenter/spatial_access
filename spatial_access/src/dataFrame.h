#pragma once
#include <unordered_map>

#include "protobuf/p2p.pb.h"

/* a pandas-like dataFrame */
class dataFrame {
public:

    // TODO: Remove string label remnants
    std::unordered_map <unsigned long int, p2p::dataRow> row_id_map_int;
    std::unordered_map <std::string, p2p::dataRow> row_id_map_string;

    // Map the column id to a location in an array
    std::unordered_map<unsigned long int, unsigned long int> col_id_int_to_loc;
    std::unordered_map<std::string, unsigned long int> col_id_string_to_loc;

    p2p::metaData metaData;

public:

    // Initialization:
    dataFrame();
    void reserve(const std::vector<unsigned long int> &primary_ids, const std::vector<unsigned long int> &secondary_ids);
    void reserve(const std::vector<std::string> &primary_ids, const std::vector<std::string> &secondary_ids);
    
    // Getters and Setters:
    unsigned short int retrieveValue(unsigned long int row_id, unsigned long int col_id) const;
    unsigned short int retrieveValue(const std::string& row_id, const std::string& col_id) const;
    void insertValue(unsigned short int value, unsigned long int row_id, unsigned long int col_id);
    void insertValue(unsigned short int value, const std::string& row_id, const std::string& col_id);
    bool isSymmetric() const;
    void setSymmetric(bool isSymmetric);
    void insertRow(const std::unordered_map<unsigned long int, unsigned short int> &row_data, unsigned long int source_id);
    void insertRow(const std::unordered_map<std::string, unsigned short int> &row_data, const std::string& source_id);
    const std::vector<std::pair<unsigned long int, unsigned short int>> getValuesByRow(unsigned long int row_id, bool sort);
    const std::vector<std::pair<unsigned long int, unsigned short int>> getValuesByCol(unsigned long int row_id, bool sort);

    // Input/Output:
    bool readCSV(const std::string &infile);
    bool readTMX(const std::string &infile);
    bool writeCSV(const std::string &outfile) const;
    bool writeTMX(const std::string &outfile) const;
    bool writeMetadata(const std::string &outfile) const;
    bool writeRowdata(const std::string &outfile, unsigned long int row_id) const;
    bool writeRowdata(const std::string &outfile, const std::string &row_id) const;
    bool readMetadata(const std::string &outfile);
    bool readRowdata(const std::string &outfile, unsigned long int row_id);
    bool readRowdata(const std::string &outfile, const std::string &row_id);
    void printDataFrame() const;
    bool readOTPMatrix(const std::string& infile);

    // Utility
    bool isUnderDiagonal(unsigned long int row_id, unsigned long int col_id) const;
    bool isUnderDiagonal(const std::string& row_id, const std::string& col_id) const;

private:
    // Input/Output
    bool writeToStream(std::ostream& streamToWrite) const;

};
