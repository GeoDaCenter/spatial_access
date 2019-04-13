# distutils: language=c++
# cython: language_level=3
from libcpp.string cimport string
from libcpp cimport bool
from libcpp.vector cimport vector
from libcpp.unordered_map cimport unordered_map
from libcpp.utility cimport pair

ctypedef unsigned short int value
ctypedef unsigned long ulong
cdef extern from "include/transitMatrix.h" namespace "lmnoel":

    cdef cppclass transitMatrix[int_label, string]:
        ctypedef unsigned long int int_label

        transitMatrix(bool, bool, unsigned int, unsigned int) except +
        transitMatrix() except +

        void prepareGraphWithVertices(int V) except +
        void addToUserSourceDataContainer(unsigned int, unsigned long, unsigned short int) except +
        void addToUserDestDataContainer(unsigned int, string, unsigned short int) except +
        void addEdgesToGraph(vector[ulong], vector[ulong], vector[value], vector[bool]) except +
        void addToCategoryMap(string, string) except +
        void setMockDataFrame(vector[vector[value]], vector[ulong], vector[string]) except +

        void compute(int) except +
        vector[pair[ulong, value]] getValuesByDest(string, bool) except +
        vector[pair[string, value]] getValuesBySource(unsigned long, bool) except +
        unordered_map[ulong, vector[string]] getDestsInRange(unsigned int) except +
        unordered_map[string, vector[ulong]] getSourcesInRange(unsigned int) except +
        unsigned short int timeToNearestDestPerCategory(unsigned long, string) except +
        unsigned short int countDestsInRangePerCategory(unsigned long, string, unsigned short int) except +
        unsigned short int timeToNearestDest(unsigned long) except +
        unsigned short int countDestsInRange(unsigned long, unsigned short int) except +

        void writeCSV(string) except +
        void writeTMX(string) except +
        void readTMX(string) except +
        void printDataFrame() except +



cdef class pyTransitMatrix:
    cdef transitMatrix *thisptr

    def __cinit__(self, bool isCompressible=False, bool isSymmetric=False, unsigned int rows=0, unsigned int columns=0):
        if rows == 0 and columns == 0:
            self.thisptr = new transitMatrix()
        else:
            self.thisptr = new transitMatrix(isCompressible, isSymmetric, rows, columns)

    def __dealloc__(self):
        del self.thisptr

    def prepareGraphWithVertices(self, vertices):
        self.thisptr.prepareGraphWithVertices(vertices)

    def getDestsInRange(self, range_):
        cdef unordered_map[ulong, vector[string]] py_res = self.thisptr.getDestsInRange(range_)
        rv = {}
        for key, value in py_res:
            rv[key] = [item.decode() for item in value]
        return rv


    def getSourcesInRange(self, range_):
        cdef unordered_map[string, vector[ulong]] py_res = self.thisptr.getSourcesInRange(range_)
        rv = {}
        for key, value in py_res:
            rv[key.decode()] = value
        return rv

    def getValuesBySource(self, source_id, sort):
        cdef vector[pair[string, value]] cpp_result = self.thisptr.getValuesBySource(source_id, sort)
        rv = []
        for a, b in cpp_result:
            rv.append((a.decode(), b))
        return rv

    def getValuesByDest(self, dest_id, sort):
        cdef string dest_id_string = str.encode(dest_id)
        return self.thisptr.getValuesByDest(dest_id_string, sort)

    def addToUserSourceDataContainer(self, networkNodeId, source_id, lastMileDistance):
        self.thisptr.addToUserSourceDataContainer(networkNodeId, source_id, lastMileDistance)

    def addToUserDestDataContainer(self, networkNodeId, dest_id, lastMileDistance):
        cdef string dest_id_string = str.encode(dest_id)
        self.thisptr.addToUserDestDataContainer(networkNodeId, dest_id_string, lastMileDistance)

    def addEdgesToGraph(self, from_column, to_column, edge_weight_column, is_bidirectional_column):
        self.thisptr.addEdgesToGraph(from_column, to_column, edge_weight_column, is_bidirectional_column)

    def setMockDataFrame(self, dataset, row_ids, col_ids):
        cdef vector[string] col_ids_string = []
        for col_id in col_ids:
            col_ids_string.push_back(col_id.encode())
        self.thisptr.setMockDataFrame(dataset, row_ids, col_ids_string)

    def compute(self, numThreads):
        self.thisptr.compute(numThreads)

    def writeCSV(self, outfile):
        cdef string outfile_string = str.encode(outfile)
        return self.thisptr.writeCSV(outfile_string)

    def writeTMX(self, outfile):
        cdef string outfile_string = str.encode(outfile)
        self.thisptr.writeTMX(outfile_string)

    def readTMX(self, infile):
        cdef string infile_string = str.encode(infile)
        self.thisptr.readTMX(infile_string)

    def printDataFrame(self):
        self.thisptr.printDataFrame()

    def addToCategoryMap(self, dest_id, category):
        cdef string string_category = str.encode(category)
        cdef string string_dest_id = str.encode(dest_id)
        self.thisptr.addToCategoryMap(string_dest_id, string_category)

    def timeToNearestDestPerCategory(self, source_id, category):
        cdef string string_category = str.encode(category)
        return self.thisptr.timeToNearestDestPerCategory(source_id, string_category)

    def countDestsInRangePerCategory(self, source_id, category, range):
        cdef string string_category = str.encode(category)
        return self.thisptr.countDestsInRangePerCategory(source_id, string_category, range)

    def timeToNearestDest(self, source_id):
        return self.thisptr.timeToNearestDest(source_id)

    def countDestsInRange(self, source_id, range):
        return self.thisptr.countDestsInRange(source_id, range)
