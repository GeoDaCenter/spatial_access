// This is a test file used for development of the package
// it should be removed prior to distribution

#include <iostream>
#include "transitMatrix.h"


int main()
{
//
    transitMatrix<unsigned long, unsigned long> tm2;
    tm2.readOTPCSV("generated.csv");
    tm2.printDataFrame();


    return 0;
};

  
