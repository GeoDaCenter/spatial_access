# distutils: language=c++
# cython: language_level=3

from libcpp.vector cimport vector
from libcpp.utility cimport pair

ctypedef unsigned long int ulong;

cdef extern from "include/networkUtility.h":
    cdef cppclass NetworkUtility:
        NetworkUtility(vector[pair[ulong, ulong]], vector[ulong]) except +
        vector[pair[ulong, ulong]] getConnectedNetworkEdges() except +
        vector[unsigned long int] getConnectedNetworkNodes() except +

cdef class pyNetworkUtility:
    cdef NetworkUtility *thisptr

    def __cinit__(self, edges, nodes):
        self.thisptr = new NetworkUtility(edges, nodes)

    def __dealloc__(self):
        del self.thisptr

    def getConnectedNetworkEdges(self):
        return self.thisptr.getConnectedNetworkEdges()

    def getConnectedNetworkNodes(self):
        return self.thisptr.getConnectedNetworkNodes()