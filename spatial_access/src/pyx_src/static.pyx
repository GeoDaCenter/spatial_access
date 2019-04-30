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
ctypedef unsigned int uint

cdef extern from "include/networkUtility.h":
    cdef cppclass NetworkUtility "NetworkUtility<unsigned long int>":
        NetworkUtility(vector[pair[ulong, ulong]], vector[ulong]) except +
        unordered_set[ulong] getConnectedNetworkNodes() except +


cdef extern from "include/tmxParser.h":
    cdef cppclass tmxTypeReader:
        tmxTypeReader(string) except +
        ushort readUshort() except +


cdef class pyNetworkUtility:
    cdef NetworkUtility *thisptr

    def __cinit__(self, edges, nodes):
        self.thisptr = new NetworkUtility(edges, nodes)

    def __dealloc__(self):
        del self.thisptr

    def getConnectedNetworkNodes(self):
        return self.thisptr.getConnectedNetworkNodes()

cdef class pyTMXTypeReader:
    cdef tmxTypeReader *thisptr
    cdef int tmxVersion
    cdef int rowTypeEnum
    cdef int colTypeEnum
    cdef int valueTypeEnum

    def __cinit__(self, filename):
        self.thisptr = new tmxTypeReader(filename)
        self.tmxVersion = self.thisptr.readUshort()
        self.rowTypeEnum = self.thisptr.readUshort()
        self.colTypeEnum = self.thisptr.readUshort()
        self.valueTypeEnum = self.thisptr.readUshort()

    def __dealloc__(self):
        del self.thisptr

    def get_tmx_version(self):
        return self.tmxVersion

    def get_row_type_enum(self):
        return self.rowTypeEnum

    def get_col_type_enum(self):
        return self.colTypeEnum

    def get_value_type_enum(self):
        return self.valueTypeEnum
