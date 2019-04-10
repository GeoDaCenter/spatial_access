// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#include "include/dataFrame.h"

// TODO: encode isSymmetric to eliminate redundant labels
template<>
void dataFrame<unsigned long int, unsigned long int>::writeTMX(const std::string& filename) const
{

    Serializer s(filename);

    // Mode
    MatrixType mode = IxI;
    s.writeShortInt(mode);

    // isCompressible
    s.writeShortInt(isCompressible);

    // rows
    s.writeLongInt(rows);

    // cols
    s.writeLongInt(cols);

    // rowIds
    s.writeVectorLongInt(rowIds);

    // colIds
    s.writeVectorLongInt(colIds);

    s.writeVectorVector(dataset);

}

template<>
void dataFrame<unsigned long int, unsigned long int>::readTMX(const std::string& filename)
{
    Deserializer d(filename);

    // Mode
    auto mode = (MatrixType) d.readShortInt();

    if (mode != IxI) {
        throw std::runtime_error("Unexpected mode");
    }

    // isCompressible
    isCompressible = (bool) d.readShortInt();

    // rows
    rows = d.readLongInt();

    // cols
    cols = d.readLongInt();

    // rowIds
    d.readVectorLongInt(rowIds);

    // colIds
    d.readVectorLongInt(colIds);

    // data
    d.readVectorVector(dataset);

    for (unsigned long int i = 0; i < rows; i++) {
        rowIdsToLoc.insert(std::make_pair(rowIds.at(i), i));
    }

    for (unsigned long int i = 0; i < cols; i++) {
        colIdsToLoc.insert(std::make_pair(colIds.at(i), i));
    }
    if (isCompressible) {
        dataset_size = (rows * (rows + 1)) / 2;
    }
    else {
        dataset_size = rows * cols;
    }

}

template<>
void dataFrame<std::string, std::string>::writeTMX(const std::string& filename) const
{

    Serializer s(filename);

    // Mode
    MatrixType mode = SxS;
    s.writeShortInt(mode);

    // isCompressible
    s.writeShortInt(isCompressible);

    // rows
    s.writeLongInt(rows);

    // cols
    s.writeLongInt(cols);

    // rowIds
    s.writeVectorString(rowIds);

    // colIds
    s.writeVectorString(colIds);

    s.writeVectorVector(dataset);

}

template<>
void dataFrame<std::string, std::string>::readTMX(const std::string& filename)
{
    Deserializer d(filename);

    // Mode
    auto mode = (MatrixType) d.readShortInt();

    if (mode != SxS) {
        throw std::runtime_error("Unexpected mode");
    }

    // isCompressible
    isCompressible = (bool) d.readShortInt();

    // rows
    rows = d.readLongInt();

    // cols
    cols = d.readLongInt();

    // rowIds
    d.readVectorString(rowIds);

    // colIds
    d.readVectorString(colIds);

    // data
    d.readVectorVector(dataset);

    for (unsigned long int i = 0; i < rows; i++) {
        rowIdsToLoc.insert(std::make_pair(rowIds.at(i), i));
    }

    for (unsigned long int i = 0; i < cols; i++) {
        colIdsToLoc.insert(std::make_pair(colIds.at(i), i));
    }
    if (isCompressible) {
        dataset_size = (rows * (rows + 1)) / 2;
    }
    else {
        dataset_size = rows * cols;
    }

}

template<>
void dataFrame<std::string, unsigned long int>::writeTMX(const std::string& filename) const
{

    Serializer s(filename);

    // Mode
    MatrixType mode = SxI;
    s.writeShortInt(mode);

    // isCompressible
    s.writeShortInt(isCompressible);

    // rows
    s.writeLongInt(rows);

    // cols
    s.writeLongInt(cols);

    // rowIds
    s.writeVectorString(rowIds);

    // colIds
    s.writeVectorLongInt(colIds);

    s.writeVectorVector(dataset);

}

template<>
void dataFrame<std::string, unsigned long int>::readTMX(const std::string& filename)
{
    Deserializer d(filename);

    // Mode
    auto mode = (MatrixType) d.readShortInt();

    if (mode != SxI) {
        throw std::runtime_error("Unexpected mode");
    }

    // isCompressible
    isCompressible = (bool) d.readShortInt();

    // rows
    rows = d.readLongInt();

    // cols
    cols = d.readLongInt();

    // rowIds
    d.readVectorString(rowIds);

    // colIds
    d.readVectorLongInt(colIds);

    // data
    d.readVectorVector(dataset);

    for (unsigned long int i = 0; i < rows; i++) {
        rowIdsToLoc.insert(std::make_pair(rowIds.at(i), i));
    }

    for (unsigned long int i = 0; i < cols; i++) {
        colIdsToLoc.insert(std::make_pair(colIds.at(i), i));
    }
    if (isCompressible) {
        dataset_size = (rows * (rows + 1)) / 2;
    }
    else {
        dataset_size = rows * cols;
    }

}

template<>
void dataFrame<unsigned long int, std::string>::writeTMX(const std::string& filename) const
{

    Serializer s(filename);

    // Mode
    MatrixType mode = IxS;
    s.writeShortInt(mode);

    // isCompressible
    s.writeShortInt(isCompressible);

    // rows
    s.writeLongInt(rows);

    // cols
    s.writeLongInt(cols);

    // rowIds
    s.writeVectorLongInt(rowIds);

    // colIds
    s.writeVectorString(colIds);

    s.writeVectorVector(dataset);

}

template<>
void dataFrame<unsigned long int, std::string>::readTMX(const std::string& filename)
{
    Deserializer d(filename);

    // Mode
    auto mode = (MatrixType) d.readShortInt();

    if (mode != IxS) {
        throw std::runtime_error("Unexpected mode");
    }

    // isCompressible
    isCompressible = (bool) d.readShortInt();

    // rows
    rows = d.readLongInt();

    // cols
    cols = d.readLongInt();

    // rowIds
    d.readVectorLongInt(rowIds);

    // colIds
    d.readVectorString(colIds);

    // data
    d.readVectorVector(dataset);

    for (unsigned long int i = 0; i < rows; i++) {
        rowIdsToLoc.insert(std::make_pair(rowIds.at(i), i));
    }

    for (unsigned long int i = 0; i < cols; i++) {
        colIdsToLoc.insert(std::make_pair(colIds.at(i), i));
    }
    if (isCompressible) {
        dataset_size = (rows * (rows + 1)) / 2;
    }
    else {
        dataset_size = rows * cols;
    }

}