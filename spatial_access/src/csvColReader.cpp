// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#include "include/csvColReader.h"

template <>
std::vector<unsigned long int> csvColReader<unsigned long int>::readLine(const std::string& line)
{
    std::vector<unsigned long int> return_value;
    std::string col_id;
    std::istringstream stream(line);

    // throw away first
    getline(stream, col_id, ',');
    while (getline(stream, col_id, ','))
    {
        return_value.push_back(std::stoull(col_id));
    }
    return return_value;
}

template <>
std::vector<std::string> csvColReader<std::string>::readLine(const std::string& line)
{
    std::vector<std::string> return_value;
    std::string col_id;
    std::istringstream stream(line);
    // throw away first
    getline(stream, col_id, ',');
    while (getline(stream, col_id, ','))
    {
        return_value.push_back(col_id);
    }
    return return_value;
}