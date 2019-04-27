// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#include "include/csvRowReader.h"


template <>
unsigned long int csvRowReader<unsigned long int>::readLine(const std::string& line)
{
    return std::stoull(line);
}

template<>
std::string csvRowReader<std::string>::readLine(const std::string& line)
{
    return line;
}