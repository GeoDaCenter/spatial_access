// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#include <iostream>
#include "transitMatrix.cpp"
#include <vector>
#include <unordered_map>

#include "Serializer.h"



using namespace lmnoel;
int main()
{
    transitMatrix<unsigned long int, unsigned long int> matrix(true, 3, 3);

    matrix.prepareGraphWithVertices(5);

    matrix.addEdgeToGraph(0, 1, 2, true);
    matrix.addEdgeToGraph(1, 2, 1, true);
    matrix.addEdgeToGraph(2, 3, 3, true);
    matrix.addEdgeToGraph(3, 4, 4, true);
    matrix.addEdgeToGraph(2, 4, 1, true);
    matrix.addEdgeToGraph(4, 0, 1, true);

    matrix.addToUserSourceDataContainer(1, 10, 1);
    matrix.addToUserSourceDataContainer(4, 11, 2);
    matrix.addToUserSourceDataContainer(3, 12, 3);

    matrix.addToUserDestDataContainer(1, 10, 1);
    matrix.addToUserDestDataContainer(4, 11, 2);
    matrix.addToUserDestDataContainer(3, 12, 3);

    matrix.compute(10);
    matrix.printDataFrame();
    matrix.writeTMX("tmx_test.tmx");

//    int data_size = 10;
//    std::vector<std::string> v1;
//    std::vector<unsigned short int> v2;
//    std::vector<std::vector<unsigned short int>> v3;
//    v1.assign(data_size, "hi");
//    v2.assign(data_size, 99);
//    for (auto i = 0; i < 3; i++) {
//        std::vector<unsigned short int> a;
//        a.assign(5, i);
//        v3.push_back(a);
//    }
//
//    std::string filename("testfile.bin");
//    Serializer s(filename);
//    s.writeShortInt(1);
//    s.writeVectorString(v1);
//    s.writeVectorShortInt(v2);
//    s.writeVectorVector(v3);
//    s.close();
//
//    std::vector<std::string> v4;
//    std::vector<unsigned short int> v5;
//    std::vector<std::vector<unsigned short int>> v6;
//
//    Deserializer d(filename);
//    std::cout << d.readShortInt();
//
//    d.readVectorString(v4);
//    d.readVectorShortInt(v5);
//    d.readVectorVector(v6);
//
//    std::cout << "v4" << std::endl;
//    for (auto element : v4) {
//        std::cout << element <<std::endl;
//    }
//    std::cout << "v5" << std::endl;
//    for (auto element : v5) {
//        std::cout << element <<std::endl;
//    }
//
//    std::cout << "v6" << std::endl;
//    for (auto element : v6) {
//        for (auto entry : element) {
//            std::cout << entry <<std::endl;
//        }
//    }



    return 0;
};

  
