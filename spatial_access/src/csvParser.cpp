// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science


#include "include/csvParser.h"


bool isUndefined(const std::string& item)
{
    return item.find("-1") != item.npos;
}

template <>
const std::string csvParser<std::string>::parse(const std::string& item)
{
    return item;
}

template <>
const unsigned short csvParser<unsigned short>::parse(const std::string& item)
{
    if (isUndefined(item)) {
        return std::numeric_limits<unsigned short>::max();
    }
     return (unsigned short) std::stoul(item);
}

template <>
const unsigned int csvParser<unsigned int>::parse(const std::string& item)
{;
    if (isUndefined(item)) {
        return std::numeric_limits<unsigned int>::max();
    }
    return (unsigned int) std::stoul(item);
}

template <>
const unsigned long csvParser<unsigned long>::parse(const std::string& item)
{
    if (isUndefined(item)) {
        return std::numeric_limits<unsigned long>::max();
    }
    return std::stoul(item);
}
