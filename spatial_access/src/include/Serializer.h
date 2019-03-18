// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#pragma once

#include <string>
#include <fstream>
#include <vector>
#include <istream>

class Serializer {
public:
    Serializer(const std::string &filename);
    ~Serializer();
    void close();

    std::ofstream output;
    void writeLongInt(unsigned long int value);
    void writeShortInt(unsigned short int value);
    void writeVectorLongInt(const std::vector<unsigned long int>& value);
    void writeVectorShortInt(const std::vector<unsigned short int>& value);
    void writeVectorString(const std::vector<std::string>& value);
    void writeVectorVector(const std::vector<std::vector<unsigned short int>>& value);
    void checkStreamIsGood();
};

class Deserializer {
public:
    Deserializer(const std::string &filename);
    ~Deserializer();
    void close();

    std::ifstream input;
    unsigned long int readLongInt();
    unsigned short int readShortInt();
    void readVectorLongInt( std::vector<unsigned long int>& value);
    void readVectorShortInt( std::vector<unsigned short int>& value);
    void readVectorString( std::vector<std::string>& value);
    void readVectorVector( std::vector<std::vector<unsigned short int>>& value);
    void checkStreamIsGood();
};