// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#pragma once

#include <fstream>
#include <vector>
#include <sstream>
#include <type_traits>
#include <limits>

template <class T>
class csvParser {
private:
    std::ifstream& sharedFile;
public:
    csvParser(std::ifstream& sharedFile) : sharedFile(sharedFile) {}
    void readLine(std::vector<T>& row)
    {
        std::string line;
        std::string item;

        getline(sharedFile, line);
        std::istringstream stream(line);

        getline(stream, item, ',');

        while (getline(stream, item, ','))
        {
            row.push_back(parse(item));
        }
    }

    static const T parse(const std::string& item);


};
