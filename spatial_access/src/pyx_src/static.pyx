# distutils: language=c++
# cython: language_level=3
from libcpp.string cimport string
from libcpp cimport bool
from libcpp.vector cimport vector
from libcpp.unordered_map cimport unordered_map
from libcpp.utility cimport pair
from libcpp.unordered_set cimport unordered_set

ctypedef unsigned short int ushort
ctypedef unsigned long int ulong

cdef extern from "include/networkUtility.h":
    cdef cppclass NetworkUtility "NetworkUtility<unsigned long int>":
        NetworkUtility(vector[pair[ulong, ulong]], vector[ulong]) except +
        unordered_set[ulong] getConnectedNetworkNodes() except +


cdef extern from "include/TMXUtils.h":
    cdef cppclass TMXUtils:
        int getTypeOfTMX(string) except +


cdef class pyNetworkUtility:
    cdef NetworkUtility *thisptr

    def __cinit__(self, edges, nodes):
        self.thisptr = new NetworkUtility(edges, nodes)

    def __dealloc__(self):
        del self.thisptr

    def getConnectedNetworkNodes(self):
        return self.thisptr.getConnectedNetworkNodes()

cdef class pyTMXUtils:
    cdef TMXUtils *thisptr

    def __cinit__(self):
        self.thisptr = new TMXUtils()

    def __dealloc__(self):
        del self.thisptr

    def getTypeOfTMX(self, filename):
        cdef string filename_string = str.encode(filename)
        return self.thisptr.getTypeOfTMX(filename_string)
