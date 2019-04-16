// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>


class CSV
{
private:
    std::vector<float> data;
    std::vector<unsigned long int> row_labels;
    std::vector<unsigned long int> col_labels;

public:
// Constructor

    CSV(const std::string& filename)
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
            row_labels.push_back(std::stoul(row_label));
            col_labels.push_back(std::stoul(col_label));
            data.push_back(std::stof(value));
        }

        fileIN.close();
    }

// Getters

    const std::vector<unsigned long int>& get_row_labels() const
    {
        return row_labels;

    }
    const std::vector<unsigned long int>& get_col_labels() const
    {
        return col_labels;
    }

    const std::vector<float>& get_data() const
    {
    return data;
    }


};
