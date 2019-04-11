# distutils: language=c++
# cython: language_level=3

from libcpp.vector cimport vector
from libcpp.utility cimport pair
from libcpp.unordered_set cimport unordered_set


cdef extern from "include/networkUtility.h":
    ctypedef unsigned long int unsigned_long;
    cdef cppclass NetworkUtility[unsigned_long]:
        ctypedef unsigned long int unsigned_long;
        NetworkUtility(vector[pair[unsigned_long, unsigned_long]], vector[unsigned_long]) except +
        unordered_set[unsigned long int] getConnectedNetworkNodes() except +

cdef class pyNetworkUtility:
    cdef NetworkUtility *thisptr

    def __cinit__(self, edges, nodes):
        self.thisptr = new NetworkUtility(edges, nodes)

    def __dealloc__(self):
        del self.thisptr

    def getConnectedNetworkNodes(self):
        return self.thisptr.getConnectedNetworkNodes()