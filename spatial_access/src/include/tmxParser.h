// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#pragma once

#include "Serializer.h"
#include <string>
#include <fstream>

enum ValidLabelTypes {
    UnsignedLongType,
    StringType
};

enum ValidValueTypes {
    UnsignedShortType,
    UnsignedIntType
};

template <class T>
class tmxWriter{

private:
    Serializer& sharedSerializer;
public:
    tmxWriter(Serializer& sharedSerializer) : sharedSerializer(sharedSerializer) {};

    void writeTMXVersion(unsigned short version)
    {
        sharedSerializer.writeNumericType<unsigned short>(version);
    }

    void writeIdTypeEnum();
    void writeValueTypeEnum();
    void writeIsCompressible(bool isCompressible)
    {
        sharedSerializer.writeBool(isCompressible);
    }

    void writeIsSymmetric(bool isSymmetric)
    {
        sharedSerializer.writeBool(isSymmetric);
    }

    void writeNumberOfRows(unsigned long int rows)
    {
        sharedSerializer.writeNumericType<unsigned long>(rows);
    }

    void writeNumberOfCols(unsigned long int cols)
    {
        sharedSerializer.writeNumericType<unsigned long>(cols);
    }

    void writeIds(const std::vector<T>& ids)
    {
        sharedSerializer.writeVector(ids);
    }

    void writeData(const std::vector<std::vector<T>>& data)
    {
        sharedSerializer.write2DVector(data);
    }
};

template <class T>
class tmxReader {
private:
    Deserializer& sharedDeserializer;
public:
    tmxReader(Deserializer& sharedDeserializer) : sharedDeserializer(sharedDeserializer) {};

    unsigned short readTMXVersion()
    {
        return sharedDeserializer.readNumericType<unsigned short>();
    }

    unsigned short readIdTypeEnum()
    {
        return sharedDeserializer.readNumericType<unsigned short>();
    }

    unsigned short readValueTypeEnum()
    {
        return sharedDeserializer.readNumericType<unsigned short>();
    }

    bool readIsCompressible()
    {
        return sharedDeserializer.readBool();
    }

    bool readIsSymmetric()
    {
        return sharedDeserializer.readBool();
    }

    unsigned long int readNumberOfRows()
    {
        return sharedDeserializer.readNumericType<unsigned long>();
    }

    unsigned long int readNumberOfCols()
    {
        return sharedDeserializer.readNumericType<unsigned long>();
    }

    void readIds(std::vector<T>& ids) {
        sharedDeserializer.readVector(ids);
    }

    void readData(std::vector<std::vector<T>>& data)
    {
        sharedDeserializer.read2DVector(data);
    }

};

class tmxTypeReader{
private:
    Deserializer deserializer;
public:
    tmxTypeReader(const std::string& filename) : deserializer(filename) {}
    unsigned short readUshort()
    {
        return deserializer.readNumericType<unsigned short>();
    }

};