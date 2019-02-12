set(CMAKE_CXX_STANDARD 11)
project(matrix)
add_executable(matrix Matrix.cpp)
target_link_libraries(matrix pthread)