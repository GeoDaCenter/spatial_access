//
// Created by Logan Noel on 2019-03-11.
//

#include "dataFrame.h"

template class dataFrame<unsigned long int, unsigned long int>;

template<>
void dataFrame<unsigned long int, unsigned long int>::writeTMX(const std::string& filename)
{
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

    // data
    s.writeVectorVector(dataset);
}