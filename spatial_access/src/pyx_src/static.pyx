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


# cdef extern from "include/tmxParser.h":
#     cdef cppclass tmxReader "tmxReader<unsigned int>":
#         tmxReader(string) except +
#         ushort readTMXVersion() except +
#         ushort readIdTypeEnum() except +
#         ushort readValueTypeEnum() except +

cdef class pyNetworkUtility:
    cdef NetworkUtility *thisptr

    def __cinit__(self, edges, nodes):
        self.thisptr = new NetworkUtility(edges, nodes)

    def __dealloc__(self):
        del self.thisptr

    def getConnectedNetworkNodes(self):
        return self.thisptr.getConnectedNetworkNodes()

# cdef class pyTMXReader:
#     cdef tmxReader *thisptr
#
#     def __cinit__(self, filename):
#         self.thisptr = new tmxReader(filename)
#
#     def __dealloc__(self):
#         del self.thisptr
#
#     def readTMXVersion(self):
#         return self.thisptr.readTMXVersion()
#
#     def readIdTypeEnum(self):
#         return self.thisptr.readIdTypeEnum()
#
#     def readValueTypeEnum(self):
#         return self.thisptr.readValueTypeEnum()
