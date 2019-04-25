// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#pragma once

#include <vector>
#include <string>
#include <sstream>

template <class col_type>
class csvColReader {
public:
    std::vector<col_type> readLine(const std::string& line);
};

