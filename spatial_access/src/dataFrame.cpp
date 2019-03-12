// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#include "dataFrame.h"

template<>
void dataFrame<unsigned long int, unsigned long int>::writeTMX(const std::string& filename) const
{
    std::cerr << "starting to write tmx" << std::endl;
    Serializer s(filename);

    // Mode
    MatrixType mode = IxI;
    s.writeShortInt(mode);

    // isSymmetric
    s.writeShortInt(isSymmetric);

    // rows
    s.writeLongInt(rows);

    // cols
    s.writeLongInt(cols);

    // rowIds
    s.writeVectorLongInt(rowIds);

    // colIds
    s.writeVectorLongInt(colIds);

    s.writeVectorVector(dataset);
    std::cerr << "done writing tmx" << std::endl;
}

template<>
void dataFrame<unsigned long int, unsigned long int>::readTMX(const std::string& filename)
{
    std::cerr << "starting to read tmx" << std::endl;
    Deserializer d(filename);

    // Mode
    auto mode = (MatrixType) d.readShortInt();
    std::cerr << "mode " << mode << std::endl;
    if (mode != IxI) {
        throw std::runtime_error("Unexpected mode");
    }

    // isSymmetric
    isSymmetric = (bool) d.readShortInt();
    std::cerr << "isSymmetric " << isSymmetric << std::endl;
    // rows
    rows = d.readLongInt();
    std::cerr << "rows " << rows << std::endl;
    // cols
    cols = d.readLongInt();
    std::cerr << "cols " << cols << std::endl;
    // rowIds

    d.readVectorLongInt(rowIds);
    std::cerr << "a " << std::endl;
    // colIds
    d.readVectorLongInt(colIds);
    std::cerr << "b "  <<std::endl;
    // data
    d.readVectorVector(dataset);
    std::cerr << "c " << std::endl;
    for (auto i = 0; i < rows; i++) {
        rowIdsToLoc.insert(std::make_pair(rowIds.at(i), i));
    }

    for (auto i = 0; i < cols; i++) {
        colIdsToLoc.insert(std::make_pair(colIds.at(i), i));
    }
    if (isSymmetric) {
        dataset_size = (rows * (rows + 1)) / 2;
    }
    else {
        dataset_size = rows * cols;
    }
    std::cerr << "done reading tmx" << std::endl;
}