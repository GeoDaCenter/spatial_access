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


cdef extern from "include/transitMatrix.h":
    cdef cppclass transitMatrixIxI "transitMatrix<unsigned long int, unsigned long int>":
        ctypedef unsigned long int int_label

        transitMatrixIxI(bool, bool, unsigned int, unsigned int) except +
        transitMatrixIxI() except +

        void prepareGraphWithVertices(int V) except +
        void addToUserSourceDataContainer(unsigned int, unsigned long, unsigned short int) except +
        void addToUserDestDataContainer(unsigned int, unsigned long, unsigned short int) except +
        void addEdgesToGraph(vector[ulong], vector[ulong], vector[ushort], vector[bool]) except +
        void addToCategoryMap(unsigned long, string) except +
        void setMockDataFrame(vector[vector[ushort]], vector[ulong], vector[ulong]) except +

        void compute(int) except +
        vector[pair[ulong, ushort]] getValuesByDest(unsigned long, bool) except +
        vector[pair[ulong, ushort]] getValuesBySource(unsigned long, bool) except +
        unordered_map[ulong, vector[ulong]] getDestsInRange(unsigned int) except +
        unordered_map[ulong, vector[ulong]] getSourcesInRange(unsigned int) except +
        unsigned short int timeToNearestDestPerCategory(unsigned long, string) except +
        unsigned short int countDestsInRangePerCategory(unsigned long, string, unsigned short int) except +
        unsigned short int timeToNearestDest(unsigned long) except +
        unsigned short int countDestsInRange(unsigned long, unsigned short int) except +

        void writeCSV(string) except +
        void writeTMX(string) except +
        void readTMX(string) except +
        void readOTPCSV(string) except +
        void printDataFrame() except +

cdef extern from "include/transitMatrix.h":
    cdef cppclass transitMatrixIxS "transitMatrix<unsigned long int, std::string>":

        transitMatrixIxS(bool, bool, unsigned int, unsigned int) except +
        transitMatrixIxS() except +

        void prepareGraphWithVertices(int V) except +
        void addToUserSourceDataContainer(unsigned int, unsigned long, unsigned short int) except +
        void addToUserDestDataContainer(unsigned int, string, unsigned short int) except +
        void addEdgesToGraph(vector[ulong], vector[ulong], vector[ushort], vector[bool]) except +
        void addToCategoryMap(string, string) except +
        void setMockDataFrame(vector[vector[ushort]], vector[ulong], vector[string]) except +

        void compute(int) except +
        vector[pair[ulong, ushort]] getValuesByDest(string, bool) except +
        vector[pair[string, ushort]] getValuesBySource(unsigned long, bool) except +
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

cdef extern from "include/transitMatrix.h":
    cdef cppclass transitMatrixSxI "transitMatrix<std::string, unsigned long int>":
        ctypedef unsigned long int int_label

        transitMatrixSxI(bool, bool, unsigned int, unsigned int) except +
        transitMatrixSxI() except +

        void prepareGraphWithVertices(int V) except +
        void addToUserSourceDataContainer(unsigned int, string, unsigned short int) except +
        void addToUserDestDataContainer(unsigned int, unsigned long, unsigned short int) except +
        void addEdgesToGraph(vector[ulong], vector[ulong], vector[ushort], vector[bool]) except +
        void addToCategoryMap(unsigned long, string) except +
        void setMockDataFrame(vector[vector[ushort]], vector[string], vector[ulong]) except +

        void compute(int) except +
        vector[pair[string, ushort]] getValuesByDest(unsigned long, bool) except +
        vector[pair[ulong, ushort]] getValuesBySource(string, bool) except +
        unordered_map[string, vector[ulong]] getDestsInRange(unsigned int) except +
        unordered_map[ulong, vector[string]] getSourcesInRange(unsigned int) except +
        unsigned short int timeToNearestDestPerCategory(string, string) except +
        unsigned short int countDestsInRangePerCategory(string, string, unsigned short int) except +
        unsigned short int timeToNearestDest(string) except +
        unsigned short int countDestsInRange(string, unsigned short int) except +

        void writeCSV(string) except +
        void writeTMX(string) except +
        void readTMX(string) except +
        void printDataFrame() except +

cdef extern from "include/transitMatrix.h":

    cdef cppclass transitMatrixSxS "transitMatrix<std::string, std::string>":

        transitMatrixSxS(bool, bool, unsigned int, unsigned int) except +
        transitMatrixSxS() except +

        void prepareGraphWithVertices(int V) except +
        void addToUserSourceDataContainer(unsigned int, string, unsigned short int) except +
        void addToUserDestDataContainer(unsigned int, string, unsigned short int) except +
        void addEdgesToGraph(vector[ulong], vector[ulong], vector[ushort], vector[bool]) except +
        void addToCategoryMap(string, string) except +
        void setMockDataFrame(vector[vector[ushort]], vector[string], vector[string]) except +

        void compute(int) except +
        vector[pair[string, ushort]] getValuesByDest(string, bool) except +
        vector[pair[string, ushort]] getValuesBySource(string, bool) except +
        unordered_map[string, vector[string]] getDestsInRange(unsigned int) except +
        unordered_map[string, vector[string]] getSourcesInRange(unsigned int) except +
        unsigned short int timeToNearestDestPerCategory(string, string) except +
        unsigned short int countDestsInRangePerCategory(string, string, unsigned short int) except +
        unsigned short int timeToNearestDest(string) except +
        unsigned short int countDestsInRange(string, unsigned short int) except +

        void writeCSV(string) except +
        void writeTMX(string) except +
        void readTMX(string) except +
        void printDataFrame() except +

cdef extern from "include/networkUtility.h":
    ctypedef unsigned long int unsigned_long;
    cdef cppclass NetworkUtility[unsigned_long]:
        ctypedef unsigned long int unsigned_long;
        NetworkUtility(vector[pair[unsigned_long, unsigned_long]], vector[unsigned_long]) except +
        unordered_set[unsigned long int] getConnectedNetworkNodes() except +


cdef extern from "include/TMXUtils.h":
    cdef cppclass TMXUtils:
        int getTypeOfTMX(string) except +


# Python classes
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

cdef class pyTransitMatrixIxI:
    cdef transitMatrixIxI *thisptr

    def __cinit__(self, bool isCompressible=False, bool isSymmetric=False, unsigned int rows=0, unsigned int columns=0):
        if rows == 0 and columns == 0:
            self.thisptr = new transitMatrixIxI()
        else:
            self.thisptr = new transitMatrixIxI(isCompressible, isSymmetric, rows, columns)

    def __dealloc__(self):
        del self.thisptr

    def prepareGraphWithVertices(self, vertices):
        self.thisptr.prepareGraphWithVertices(vertices)


    def addToUserSourceDataContainer(self, networkNodeId, id_, lastMileDistance):
        self.thisptr.addToUserSourceDataContainer(networkNodeId, id_, lastMileDistance)

    def addToUserDestDataContainer(self, networkNodeId, id_, lastMileDistance):
        self.thisptr.addToUserDestDataContainer(networkNodeId, id_, lastMileDistance)

    def addEdgesToGraph(self, from_column, to_column, edge_weight_column, is_bidirectional_column):
        self.thisptr.addEdgesToGraph(from_column, to_column, edge_weight_column, is_bidirectional_column)

    def setMockDataFrame(self, dataset, row_ids, col_ids):
        self.thisptr.setMockDataFrame(dataset, row_ids, col_ids)

    def compute(self, numThreads):
        self.thisptr.compute(numThreads)

    def writeCSV(self, outfile):
        cdef string outfile_string = str.encode(outfile)
        self.thisptr.writeCSV(outfile_string)

    def writeTMX(self, outfile):
        cdef string outfile_string = str.encode(outfile)
        self.thisptr.writeTMX(outfile_string)

    def readTMX(self, infile):
        cdef string infile_string = str.encode(infile)
        self.thisptr.readTMX(infile_string)

    def readOTPCSV(self, infile):
        cdef string infile_string = str.encode(infile)
        self.thisptr.readOTPCSV(infile_string)

    def printDataFrame(self):
        self.thisptr.printDataFrame()

    def getValuesBySource(self, source_id, sort):
        return self.thisptr.getValuesBySource(source_id, sort)

    def getValuesByDest(self, dest_id, sort):
        return self.thisptr.getValuesByDest(dest_id, sort)

    def addToCategoryMap(self, dest_id, category):
        cdef string string_category = str.encode(category)
        self.thisptr.addToCategoryMap(dest_id, string_category)

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

    def getSourcesInRange(self, range_):
        return self.thisptr.getSourcesInRange(range_)

    def getDestsInRange(self, range_):
        return self.thisptr.getDestsInRange(range_)

cdef class pyTransitMatrixIxS:
    cdef transitMatrixIxS *thisptr

    def __cinit__(self, bool isCompressible=False, bool isSymmetric=False, unsigned int rows=0, unsigned int columns=0):
        if rows == 0 and columns == 0:
            self.thisptr = new transitMatrixIxS()
        else:
            self.thisptr = new transitMatrixIxS(isCompressible, isSymmetric, rows, columns)

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
        cdef vector[pair[string, ushort]] cpp_result = self.thisptr.getValuesBySource(source_id, sort)
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

cdef class pyTransitMatrixSxI:
    cdef transitMatrixSxI *thisptr

    def __cinit__(self, bool isCompressible=False, bool isSymmetric=False, unsigned int rows=0, unsigned int columns=0):
        if rows == 0 and columns == 0:
            self.thisptr = new transitMatrixSxI()
        else:
            self.thisptr = new transitMatrixSxI(isCompressible, isSymmetric, rows, columns)

    def __dealloc__(self):
        del self.thisptr

    def prepareGraphWithVertices(self, vertices):
        self.thisptr.prepareGraphWithVertices(vertices)

    def getDestsInRange(self, range_):
        cdef unordered_map[string, vector[ulong]] py_res = self.thisptr.getDestsInRange(range_)
        rv = {}
        for key, value in py_res:
            rv[key.decode()] = value
        return rv

    def getSourcesInRange(self, range_):
        cdef unordered_map[ulong, vector[string]] py_res = self.thisptr.getSourcesInRange(range_)
        rv = {}
        for key, value in py_res:
            key_rv = []
            for element in value:
                key_rv.append(element.decode())
            rv[key] = key_rv
        return rv

    def getValuesBySource(self, source_id, sort):
        cdef string source_id_string = str.encode(source_id)
        return self.thisptr.getValuesBySource(source_id_string, sort)

    def getValuesByDest(self, dest_id, sort):
        cdef vector[pair[string, ushort]] cpp_result = self.thisptr.getValuesByDest(dest_id, sort)
        rv = []
        for a, b in cpp_result:
            rv.append((a.decode(), b))
        return rv

    def addToUserSourceDataContainer(self, networkNodeId, source_id, lastMileDistance):
        cdef string source_id_string = str.encode(source_id)
        self.thisptr.addToUserSourceDataContainer(networkNodeId, source_id_string, lastMileDistance)

    def addToUserDestDataContainer(self, networkNodeId, id_, lastMileDistance):
        self.thisptr.addToUserDestDataContainer(networkNodeId, id_, lastMileDistance)

    def addEdgesToGraph(self, from_column, to_column, edge_weight_column, is_bidirectional_column):
        self.thisptr.addEdgesToGraph(from_column, to_column, edge_weight_column, is_bidirectional_column)

    def setMockDataFrame(self, dataset, row_ids, col_ids):
        cdef vector[string] row_ids_string = []
        for row_id in row_ids:
            row_ids_string.push_back(row_id.encode())
        self.thisptr.setMockDataFrame(dataset, row_ids_string, col_ids)

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
        self.thisptr.addToCategoryMap(dest_id, string_category)

    def timeToNearestDestPerCategory(self, source_id, category):
        cdef string string_source_id = str.encode(source_id)
        cdef string string_category = str.encode(category)
        return self.thisptr.timeToNearestDestPerCategory(string_source_id, string_category)

    def countDestsInRangePerCategory(self, source_id, category, range):
        cdef string string_source_id = str.encode(source_id)
        cdef string string_category = str.encode(category)
        return self.thisptr.countDestsInRangePerCategory(string_source_id, string_category, range)

    def timeToNearestDest(self, source_id):
        cdef string string_source_id = str.encode(source_id)
        return self.thisptr.timeToNearestDest(string_source_id)

    def countDestsInRange(self, source_id, range):
        cdef string string_source_id = str.encode(source_id)
        return self.thisptr.countDestsInRange(string_source_id, range)


cdef class pyTransitMatrixSxS:
    cdef transitMatrixSxS *thisptr

    def __cinit__(self, bool isCompressible=False, bool isSymmetric=False, unsigned int rows=0, unsigned int columns=0):
        if rows == 0 and columns == 0:
            self.thisptr = new transitMatrixSxS()
        else:
            self.thisptr = new transitMatrixSxS(isCompressible, isSymmetric, rows, columns)


    def __dealloc__(self):
        if self.thisptr is not NULL:
            del self.thisptr
            self.thisptr = NULL

    def prepareGraphWithVertices(self, vertices):
        self.thisptr.prepareGraphWithVertices(vertices)

    def getDestsInRange(self, range_):
        cdef unordered_map[string, vector[string]] py_res = self.thisptr.getDestsInRange(range_)
        rv = {}
        for key, value in py_res:
            rv_key = []
            for element in value:
                rv_key.append(element.decode())
            rv[key.decode()] = rv_key
        return rv


    def getSourcesInRange(self, range_):
        cdef unordered_map[string, vector[string]] py_res = self.thisptr.getSourcesInRange(range_)
        rv = {}
        for key, value in py_res:
            rv_key = []
            for element in value:
                rv_key.append(element.decode())
            rv[key.decode()] = rv_key
        return rv

    def getValuesBySource(self, source_id, sort):
        cdef string source_id_string = str.encode(source_id)
        cdef vector[pair[string, ushort]] cpp_result = self.thisptr.getValuesBySource(source_id_string, sort)
        rv = []
        for a, b in cpp_result:
            rv.append((a.decode(), b))
        return rv

    def getValuesByDest(self, dest_id, sort):
        cdef string dest_id_string = str.encode(dest_id)
        cdef vector[pair[string, ushort]] cpp_result = self.thisptr.getValuesByDest(dest_id_string, sort)
        rv = []
        for a, b in cpp_result:
            rv.append((a.decode(), b))
        return rv

    def addToUserSourceDataContainer(self, networkNodeId, source_id, lastMileDistance):
        cdef string source_id_string = str.encode(source_id)
        self.thisptr.addToUserSourceDataContainer(networkNodeId, source_id_string, lastMileDistance)

    def addToUserDestDataContainer(self, networkNodeId, dest_id, lastMileDistance):
        cdef string dest_id_string = str.encode(dest_id)
        self.thisptr.addToUserDestDataContainer(networkNodeId, dest_id_string, lastMileDistance)

    def addEdgesToGraph(self, from_column, to_column, edge_weight_column, is_bidirectional_column):
        self.thisptr.addEdgesToGraph(from_column, to_column, edge_weight_column, is_bidirectional_column)

    def setMockDataFrame(self, dataset, row_ids, col_ids):
        cdef vector[string] row_ids_string = []
        cdef vector[string] col_ids_string = []
        for row_id in row_ids:
            row_ids_string.push_back(row_id.encode())
        for col_id in col_ids:
            col_ids_string.push_back(col_id.encode())
        self.thisptr.setMockDataFrame(dataset, row_ids_string, col_ids_string)


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
        cdef string string_dest_id = str.encode(dest_id)
        cdef string string_category = str.encode(category)
        self.thisptr.addToCategoryMap(string_dest_id, string_category)

    def timeToNearestDestPerCategory(self, source_id, category):
        cdef string string_source_id = str.encode(source_id)
        cdef string string_category = str.encode(category)
        return self.thisptr.timeToNearestDestPerCategory(string_source_id, string_category)

    def countDestsInRangePerCategory(self, source_id, category, range):
        cdef string string_source_id = str.encode(source_id)
        cdef string string_category = str.encode(category)
        return self.thisptr.countDestsInRangePerCategory(string_source_id, string_category, range)

    def timeToNearestDest(self, source_id):
        cdef string string_source_id = str.encode(source_id)
        return self.thisptr.timeToNearestDest(string_source_id)

    def countDestsInRange(self, source_id, range):
        cdef string string_source_id = str.encode(source_id)
        return self.thisptr.countDestsInRange(string_source_id, range)
