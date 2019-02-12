#include <iostream>
#include "transitMatrix.h"
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

using namespace lmnoel;
int main()
{
    transitMatrix<int, int> df(true, 3, 3);


    return 0;
};

  
