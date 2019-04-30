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

