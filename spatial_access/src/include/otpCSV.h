// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#pragma once

#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>
#include "csvParser.h"

template <class row_label_type, class col_label_type, class value_type>
class otpCSVReader
{
public:
    std::vector<value_type> data;
    std::vector<row_label_type> row_labels;
    std::vector<col_label_type> col_labels;


    otpCSVReader(const std::string& filename)
    {
        std::ifstream fileIN;
        fileIN.open(filename);
        if (fileIN.fail()) {
            throw std::runtime_error("unable to read file");
        }
        std::string line;
        std::string row_label;
        std::string col_label;
        std::string value;


        while (getline(fileIN, line))
        {
            std::istringstream stream(line);
            getline(stream, row_label,',');
            getline(stream, col_label,',');
            getline(stream, value);
            row_labels.push_back(csvParser<row_label_type>::parse(row_label));
            col_labels.push_back(csvParser<col_label_type>::parse(col_label));
            data.push_back((value_type) std::stof(value));
        }

        fileIN.close();
    }

};
