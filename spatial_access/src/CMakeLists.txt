set(CMAKE_CXX_STANDARD 11)
set (CMAKE_CXX_FLAGS -pthread)
project(matrix)
add_executable(matrix Matrix.cpp)