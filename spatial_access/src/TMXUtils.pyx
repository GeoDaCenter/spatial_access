# distutils: language=c++
# cython: language_level=3
from libcpp.string cimport string

cdef extern from "include/TMXUtils.h":
    cdef cppclass TMXUtils:
        int getTypeOfTMX(string) except +

cdef class pyTMXUtils:
    cdef TMXUtils *thisptr

    def __cinit__(self):
        self.thisptr = new TMXUtils()

    def __dealloc__(self):
        del self.thisptr

    def getTypeOfTMX(self, filename):
        cdef string filename_string = str.encode(filename)
        return self.thisptr.getTypeOfTMX(filename_string)
