// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science


#pragma once

#include <string>
#include "Serializer.h"

class TMXUtils {
public:
    TMXUtils()=default;
    int getTypeOfTMX(const std::string& filename)
    {
        Deserializer d(filename);

        // throw away version number
        d.readShortInt();

        return d.readShortInt();
    }
};
