#include <iostream>
#include <fstream>
#include <sstream>
#include <vector>
#include <string>


class CSV
{
public:
    // Constructor
    CSV(const std::string& filename);

    // Getters
    unsigned int num_rows() const;
    unsigned int num_cols() const;
    const std::vector<std::string>& get_row_labels() const;
    const std::vector<std::string>& get_col_labels() const;
    std::vector<unsigned long int> get_row_labels_as_int() const;
    std::vector<unsigned long int> get_col_labels_as_int() const;
    const std::vector<std::string>& get_row_by_index(unsigned int index) const;
    std::vector<unsigned long int> get_row_by_index_as_int(unsigned int index) const;
    const std::string& get_filename() const;

    // IO
    void print() const;

private:
    std::vector<std::vector<std::string>> data;
    std::vector<std::string> row_labels;
    std::vector<std::string> col_labels;
    std::string filename;
};

// Constructor

CSV::CSV(const std::string& filename)
{
    this->filename = filename;
    std::ifstream fileIN;
    fileIN.open(filename);
    if (fileIN.fail()) {
        throw std::runtime_error("unable to read file");
    }
    int rowNumber = 0;
    int colNumber = 0;
    std::string line;
    while (getline(fileIN, line)) {
        data.resize(rowNumber + 1);
        std::istringstream stream(line);
        if (rowNumber == 0) {
            std::string col_label;
            while (getline(stream, col_label, ',')) {
                if (colNumber != 0) {
                    // std::cout << "adding col:" << col_label << std::endl;
                    col_labels.push_back(col_label);
                }
                colNumber++;
            }
            
        } else {
            std::string row_label;
            getline(stream, row_label,',');
            if (!row_label.size())
            {
                break;
            }
            row_labels.push_back(row_label);
            std::string value;
            while (getline(stream, value, ',')) {
                data.at(rowNumber - 1).push_back(value);
            }
            
        }
    rowNumber++;
    }
}

// Getters

const std::vector<std::string>& CSV::get_row_labels() const
{
    return row_labels;

}
const std::vector<std::string>& CSV::get_col_labels() const
{
    return col_labels;
}

std::vector<unsigned long int> CSV::get_row_labels_as_int() const
{
    std::vector<unsigned long int> labels;
    for (auto element : this->row_labels)
    {
        labels.push_back(std::stoul(element));
    }
    return labels;
}

std::vector<unsigned long int> CSV::get_col_labels_as_int() const
{
    std::vector<unsigned long int> labels;
    for (auto element : this->col_labels)
    {
        labels.push_back(std::stoul(element));
    }
    return labels;
}

const std::vector<std::string>& CSV::get_row_by_index(unsigned int index) const
{
    return data.at(index);
}

std::vector<unsigned long int> CSV::get_row_by_index_as_int(unsigned int index) const
{
    std::vector<unsigned long int> values;
    for (auto value : data.at(index))
    {
        values.push_back(std::stoul(value));
    }
    return values;
}

const std::string& CSV::get_filename() const
{
    return this->filename;
}

unsigned int CSV::num_rows() const
{
    return row_labels.size();
}

unsigned int CSV::num_cols() const
{
    return col_labels.size();
}


// IO
void CSV::print() const
{
    for (auto label : col_labels)
    {
        std::cout << "," << label;
    }
    std::cout << std::endl;
    for (unsigned int row_number = 0; row_number < num_rows(); row_number++)
    {
        std::cout << row_labels.at(row_number);
        for (auto element : data.at(row_number))
        {
            std::cout << "," << element;
        }
        std::cout << std::endl;
    }
}
