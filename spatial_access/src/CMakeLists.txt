cmake_minimum_required(VERSION 3.13)
set(CMAKE_CXX_STANDARD 11)
set (CMAKE_CXX_FLAGS "-O3")
#set(CMAKE_CXX_FLAGS -march=native)
include_directories(include)
set(SOURCE_FILES
        dataFrame.cpp
        Serializer.cpp
        Matrix.cpp
        userDataContainer.cpp
        Graph.cpp
        threadUtilities.cpp)
project(matrix)
add_executable(matrix ${SOURCE_FILES})