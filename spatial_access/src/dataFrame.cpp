// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#include "include/dataFrame.h"

template<>
void dataFrame<unsigned long int, unsigned long int>::readOTPCSV(const std::string& infile)
{

    isCompressible = false;
    isSymmetric = false;

    CSV csv(infile);
    auto row_labels = csv.get_row_labels();
    auto col_labels = csv.get_col_labels();

    std::unordered_set<unsigned long int> unique_row_labels_set(row_labels.begin(), row_labels.end());
    std::unordered_set<unsigned long int> unique_col_labels_set(col_labels.begin(), col_labels.end());

    std::vector<unsigned long int> unique_row_labels_vector;
    std::vector<unsigned long int> unique_col_labels_vector;

    unique_row_labels_vector.assign(unique_row_labels_set.begin(), unique_row_labels_set.end());
    unique_col_labels_vector.assign(unique_col_labels_set.begin(), unique_col_labels_set.end());
    this->rows = unique_row_labels_vector.size();
    this->cols = unique_col_labels_vector.size();
    initializeDatatsetSize();

    for (unsigned long int row_loc = 0; row_loc < rows; row_loc++)
    {
        this->rowIdsToLoc.emplace(std::make_pair(unique_row_labels_vector.at(row_loc), row_loc));
    }
    this->rowIds = unique_row_labels_vector;

    for (unsigned long int col_loc = 0; col_loc < cols; col_loc++)
    {
        this->colIdsToLoc.emplace(std::make_pair(unique_col_labels_vector.at(col_loc), col_loc));
    }
    this->colIds = unique_col_labels_vector;

    std::vector<float> values = csv.get_data();

    for (unsigned int row_loc = 0; row_loc < rows; row_loc++)
    {
        std::vector<unsigned short int> data(cols, UNDEFINED);
        dataset.push_back(data);
    }
    for (unsigned long int i = 0; i < row_labels.size(); i++)
    {
        setValueById(row_labels.at(i), col_labels.at(i), (unsigned short) values.at(i));
    }

}

template<>
void dataFrame<unsigned long int, unsigned long int>::writeTMX(const std::string& filename) const
{
    Serializer s(filename);

    Type mode = IxI;
    writeTMXHeader(s, mode);

    s.writeVectorLongInt(rowIds);

    s.writeVectorLongInt(colIds);

    s.writeVectorVector(dataset);

}

template<>
void dataFrame<unsigned long int, unsigned long int>::readTMX(const std::string& filename)
{
    Deserializer d(filename);

    Type expected_mode = IxI;

    readTMXHeader(d, expected_mode);

    d.readVectorLongInt(rowIds);

    d.readVectorLongInt(colIds);

    d.readVectorVector(dataset);

    setRowIds(rowIds);
    setColIds(colIds);

    initializeDatatsetSize();
}

template<>
void dataFrame<std::string, std::string>::writeTMX(const std::string& filename) const
{

    Serializer s(filename);

    Type mode = SxS;
    writeTMXHeader(s, mode);

    s.writeVectorString(rowIds);

    s.writeVectorString(colIds);

    s.writeVectorVector(dataset);

}

template<>
void dataFrame<std::string, std::string>::readTMX(const std::string& filename)
{
    Deserializer d(filename);

    Type expected_mode = SxS;

    readTMXHeader(d, expected_mode);

    d.readVectorString(rowIds);

    d.readVectorString(colIds);

    d.readVectorVector(dataset);

    setRowIds(rowIds);
    setColIds(colIds);

    initializeDatatsetSize();
}

template<>
void dataFrame<std::string, unsigned long int>::writeTMX(const std::string& filename) const
{

    Serializer s(filename);

    Type mode = SxI;
    writeTMXHeader(s, mode);

    s.writeVectorString(rowIds);

    s.writeVectorLongInt(colIds);

    s.writeVectorVector(dataset);
}

template<>
void dataFrame<std::string, unsigned long int>::readTMX(const std::string& filename)
{
    Deserializer d(filename);

    Type expected_mode = SxI;

    readTMXHeader(d, expected_mode);

    d.readVectorString(rowIds);

    d.readVectorLongInt(colIds);

    d.readVectorVector(dataset);

    setRowIds(rowIds);
    setColIds(colIds);

    initializeDatatsetSize();
}

template<>
void dataFrame<unsigned long int, std::string>::writeTMX(const std::string& filename) const
{

    Serializer s(filename);

    Type mode = IxS;
    writeTMXHeader(s, mode);

    s.writeVectorLongInt(rowIds);

    s.writeVectorString(colIds);

    s.writeVectorVector(dataset);

}

template<>
void dataFrame<unsigned long int, std::string>::readTMX(const std::string& filename)
{
    Deserializer d(filename);

    Type expected_mode = IxS;

    readTMXHeader(d, expected_mode);

    d.readVectorLongInt(rowIds);

    d.readVectorString(colIds);

    d.readVectorVector(dataset);

    setRowIds(rowIds);
    setColIds(colIds);

    initializeDatatsetSize();

}