// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#include "include/tmxParser.h"

// write data

template<>
void tmxWriter<unsigned long>::writeIdTypeEnum()
{
    sharedSerializer.writeNumericType<unsigned short>(UnsignedLongType);
}

template<>
void tmxWriter<std::string>::writeIdTypeEnum()
{
    sharedSerializer.writeNumericType<unsigned short>(StringType);
}

template<>
void tmxWriter<unsigned short>::writeValueTypeEnum()
{
    sharedSerializer.writeNumericType<unsigned short>(UnsignedShortType);
}

template<>
void tmxWriter<unsigned int>::writeValueTypeEnum()
{
    sharedSerializer.writeNumericType<unsigned short>(UnsignedIntType);
}
