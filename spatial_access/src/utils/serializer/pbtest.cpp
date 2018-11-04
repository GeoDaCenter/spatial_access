#include "p2p.pb.h"
#include <iostream>
#include <fstream>


int main() {

p2p::transit_matrix matrix;

// matrix.set_type(p2p::transit_matrix::DRIVE);

matrix.add_row_label(10);
matrix.add_row_label(11);
matrix.add_col_label(110);
matrix.add_col_label(111);
matrix.add_col_label(112);

auto row_0 = matrix.add_row();

row_0->add_column(0);
row_0->add_column(1);
row_0->add_column(2);

auto row_1 = matrix.add_row();

row_1->add_column(0);
row_1->add_column(1);
row_1->add_column(2);

auto row_2 = matrix.add_row();

row_2->add_column(0);
row_2->add_column(1);
row_2->add_column(2);

std::string filename("sample.tmx");
 std::fstream output(filename, std::ios::out | std::ios::trunc | std::ios::binary);
if (!matrix.SerializeToOstream(&output)) {
  std::cerr << "Failed to write transit_matrix." << std::endl;
  return -1;
}
output.close();

std::fstream inputFile(filename, std::ios::in | std::ios::binary);
p2p::transit_matrix matrix2;
// std::string inputString;

// if (!matrix.SerializeToString(&inputString)) {
//   std::cerr << "Failed to write transit_matrix." << std::endl;
//   return -1;
// }

if (!matrix2.ParseFromIstream(&inputFile)) {
      std::cerr << "Failed to parse transit_matrix." << std::endl;
      return -1;
    }

// std::cout << "networkType:" << matrix2.type() << std::endl;
std::cout << "write network dimensions:" << matrix.row_label_size() << "x" << matrix.col_label_size() << std::endl;
std::cout << "read network dimensions:" << matrix2.row_label_size() << "x" << matrix2.col_label_size() << std::endl;

for (auto i=0 ; i <matrix2.row_label_size(); i++)
{
    auto row_label = matrix2.row_label(i);
    std::cout << row_label << "," << std::endl;
}

}
