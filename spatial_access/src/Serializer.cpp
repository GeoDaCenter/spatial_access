// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#include <iostream>

#include "include/Serializer.h"

Serializer::Serializer(const std::string &filename)
{
    output.open(filename, std::ios::binary | std::ios::out);
}

Serializer::~Serializer()
{
    output.close();
}

void Serializer::close()
{
    output.close();
}

void Serializer::checkStreamIsGood()
{
    if (!output.good()) {
        close();
        throw std::runtime_error("SerializerError: Serialization failed");
    }
}

void Serializer::writeShortInt(unsigned short int value)
{
    output.write ( reinterpret_cast<char *>(&value),sizeof(unsigned short int) );
    checkStreamIsGood();
}

void Serializer::writeLongInt(unsigned long int value)
{
    output.write ( reinterpret_cast<char *>(&value),sizeof(unsigned long int) );
    checkStreamIsGood();
}

void Serializer::writeVectorShortInt(const std::vector<unsigned short int>& value)
{
    unsigned long int vec_size = value.size();
    writeLongInt(vec_size);
    output.write((char *) &value[0], vec_size * sizeof( unsigned short int));
    checkStreamIsGood();
}

void Serializer::writeVectorLongInt(const std::vector<unsigned long int>& value)
{
    unsigned long int vec_size = value.size();
    writeLongInt(vec_size);
    output.write((char *) &value[0], vec_size * sizeof( unsigned long int));
    checkStreamIsGood();
}

void Serializer::writeVectorString(const std::vector<std::string>& value)
{
    typename std::vector<std::string>::size_type size = value.size();

    writeLongInt(size);

    for (typename std::vector<std::string>::size_type i = 0; i < size; ++i)
    {
        typename std::vector<std::string>::size_type element_size = value[i].size();
        output.write((char*)&element_size, sizeof(element_size));
        output.write(&value[i][0], element_size);
    }
    checkStreamIsGood();
}

void Serializer::writeVectorVector(const std::vector<std::vector<unsigned short int>>& value)
{
    unsigned long int vec_size = value.size();
    writeLongInt(vec_size);
    for (const auto &element : value) {
        writeVectorShortInt(element);
    }
    checkStreamIsGood();
}

Deserializer::Deserializer(const std::string &filename)
{
    input.open(filename, std::ios::binary | std::ios::in);
}

Deserializer::~Deserializer()
{
    input.close();
}

void Deserializer::close()
{
    input.close();
}

void Deserializer::checkStreamIsGood()
{
    if (!input.good()) {
        close();
        throw std::runtime_error("DeserializerError: Deserialization failed");
    }
}

unsigned long int Deserializer::readLongInt()
{
    unsigned long int value;
    input.read( reinterpret_cast<char *>(&value), sizeof( unsigned long int));
    checkStreamIsGood();
    return value;

}

unsigned short int Deserializer::readShortInt()
{
    unsigned short int value;
    input.read( reinterpret_cast<char *>(&value), sizeof( unsigned short int));
    checkStreamIsGood();
    return value;
}

void Deserializer::readVectorLongInt(std::vector<unsigned long int>& value)
{
    unsigned long int vec_size = readLongInt();

    value.assign(vec_size, 0);
    input.read(reinterpret_cast<char *>(&value[0]), vec_size*sizeof( unsigned long int) );
    checkStreamIsGood();
}

void Deserializer::readVectorShortInt(std::vector<unsigned short int>& value)
{
    unsigned long int vec_size = readLongInt();

    value.assign(vec_size, 0);
    input.read(reinterpret_cast<char *>(&value[0]), vec_size*sizeof( unsigned short int) );
    checkStreamIsGood();
}


void Deserializer::readVectorString(std::vector<std::string>& value)
{
    typename std::vector<std::string>::size_type size = 0;
    input.read((char*)&size, sizeof(size));
    value.resize(size);
    checkStreamIsGood();
    for (typename std::vector<std::string>::size_type i = 0; i < size; ++i)
    {
        typename std::vector<std::string>::size_type element_size = 0;
        input.read((char*)&element_size, sizeof(element_size));
        value[i].resize(element_size);
        input.read(&value[i][0], element_size);
    }
    checkStreamIsGood();
}

void Deserializer::readVectorVector(std::vector<std::vector<unsigned short int>>& value)
{
    unsigned long int vec_size = readLongInt();
    for (unsigned long int i = 0; i < vec_size; i++)
    {

        std::vector<unsigned short int> element;
        readVectorShortInt(element);
        value.push_back(element);
    }
    checkStreamIsGood();
}