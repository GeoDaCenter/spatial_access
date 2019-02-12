#include <iostream>
#include "dataFrame.cpp"
#include <vector>
#include <unordered_map>

void printArray(std::vector<unsigned long int> array)
{
    for (auto element : array)
    {
        std::cout << element << ", ";
    }
    std::cout << std::endl;
}

void printMapOfArrays(std::unordered_map<long unsigned int, std::vector<long unsigned int>> map)
{
    for (auto element : map)
    {
        std::cout << "row " << element.first << ":" << std::endl;
        printArray(element.second);
    }
}

int main()
{
    dataFrame<int, int> df(true, 3, 3);

    std::vector<std::vector<unsigned short int>> data;
//    std::vector<unsigned short int> row0 = {0, 1};
//    std::vector<unsigned short int> row1 = {2, 3};
//    std::vector<unsigned short int> row2 = {4, 5};
    std::vector<unsigned short int> row0 = {0, 5, 6, 0, 7, 0};

    data.push_back(row0);
//    data.push_back(row1);
//    data.push_back(row2);
//    std::vector<std::string> row_ids = {"a", "b", "c"};
    std::vector<int> col_ids = {21, 22, 23};
    df.setRowIds(col_ids);
    df.setColIds(col_ids);
    df.setDataset(data);

    df.printDataFrame();

    df.setValueById(22,22, 3);
    df.printDataFrame();

    return 0;
};

  
