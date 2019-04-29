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

void Serializer::checkStreamIsGood()
{
    if (!output.good()) {
        output.close();
        throw std::runtime_error("SerializerError: Serialization failed");
    }
}

void Serializer::writeBool(bool value)
{
    this->writeNumericType<unsigned short>((unsigned short) value);
}


template<>
void Serializer::writeVector(const std::vector<std::string>& value)
{
    typename std::vector<std::string>::size_type size = value.size();

    writeNumericType<unsigned long int>(size);

    for (typename std::vector<std::string>::size_type i = 0; i < size; ++i)
    {
        typename std::vector<std::string>::size_type element_size = value[i].size();
        output.write((char*)&element_size, sizeof(element_size));
        output.write(&value[i][0], element_size);
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

void Deserializer::checkStreamIsGood()
{
    if (!input.good()) {
        input.close();
        throw std::runtime_error("DeserializerError: Deserialization failed");
    }
}

bool Deserializer::readBool()
{
    return (bool) this->readNumericType<unsigned short>();
}


template<>
void Deserializer::readVector(std::vector<std::string>& value)
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
