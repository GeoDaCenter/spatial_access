cmake_minimum_required(VERSION 3.13)
set(CMAKE_CXX_STANDARD 11)
set (CMAKE_CXX_FLAGS "-O3")
#set(CMAKE_CXX_FLAGS -march=native)
include_directories(include)
set(SOURCE_FILES
        Serializer.cpp
        Matrix.cpp
        threadUtilities.cpp
        csvParser.cpp
        tmxParser.cpp)
project(matrix)
add_executable(matrix ${SOURCE_FILES})