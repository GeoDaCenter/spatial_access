// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science


#include "include/csvParser.h"

template <>
const std::string csvParser<std::string>::parse(const std::string& item)
{
    return item;
}

template <>
const unsigned short csvParser<unsigned short>::parse(const std::string& item)
{
     return (unsigned short) std::stoul(item);
}

template <>
const unsigned int csvParser<unsigned int>::parse(const std::string& item)
{
    return (unsigned int) std::stoul(item);
}

template <>
const unsigned long csvParser<unsigned long>::parse(const std::string& item)
{
    return (unsigned long) std::stoul(item);
}
