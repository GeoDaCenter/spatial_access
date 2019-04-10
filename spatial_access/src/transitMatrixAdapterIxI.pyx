# distutils: language=c++
# cython: language_level=3
from libcpp.string cimport string
from libcpp cimport bool
from libcpp.vector cimport vector
from libcpp.unordered_map cimport unordered_map
from libcpp.utility cimport pair

ctypedef unsigned short int matrix

cdef extern from "include/transitMatrix.h" namespace "lmnoel":
    cdef cppclass transitMatrix[int_label, int_label]:
        ctypedef unsigned short int value
        ctypedef unsigned long int int_label

        transitMatrix(bool, bool, unsigned int, unsigned int) except +
        transitMatrix() except +

        void prepareGraphWithVertices(int V) except +
        void addToUserSourceDataContainer(unsigned int, unsigned long, unsigned short int) except +
        void addToUserDestDataContainer(unsigned int, unsigned long, unsigned short int) except +
        void addEdgeToGraph(int, int, int, bool) except +
        void addToCategoryMap(unsigned long, string) except +

        void compute(int) except +
        vector[pair[int_label, value]] getValuesByDest(unsigned long, bool) except +
        vector[pair[int_label, value]] getValuesBySource(unsigned long, bool) except +
        unordered_map[int_label, vector[int_label]] getDestsInRange(unsigned int, int) except +
        unordered_map[int_label, vector[int_label]] getSourcesInRange(unsigned int, int) except +
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


    def addToUserSourceDataContainer(self, networkNodeId, id_, lastMileDistance):
        self.thisptr.addToUserSourceDataContainer(networkNodeId, id_, lastMileDistance)

    def addToUserDestDataContainer(self, networkNodeId, id_, lastMileDistance):
        self.thisptr.addToUserDestDataContainer(networkNodeId, id_, lastMileDistance)


    def addEdgeToGraph(self, src, dst, weight, isBidirectional):
        self.thisptr.addEdgeToGraph(src, dst, weight, isBidirectional)

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

    def printDataFrame(self):
        self.thisptr.printDataFrame()

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

    def getSourcesInRange(self, range_, numThreads):
        return self.thisptr.getSourcesInRange(range_, numThreads)

    def getDestsInRange(self, range_, numThreads):
        return self.thisptr.getDestsInRange(range_, numThreads)