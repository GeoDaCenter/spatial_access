# distutils: language = c++

from libcpp.string cimport string

cdef extern from "transitMatrix.h":
    cdef cppclass transitMatrix:
        transitMatrix(string) except +
        transitMatrix(int) except +
        int get(string, string) except +
        void addToUserSourceDataContainer(int, string, int);
        void addToUserDestDataContainer(int, string, int);
        void addEdgeToGraph(int, int, int, bool)
        void compute(float, int) except +
        void compute(float, string) except +
