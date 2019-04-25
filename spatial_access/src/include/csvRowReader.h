// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#pragma once

#include <string>

template <class row_type>
class csvRowReader {
public:
    row_type readLine(const std::string& line);
};

