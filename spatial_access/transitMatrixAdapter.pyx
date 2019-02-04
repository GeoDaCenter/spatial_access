# distutils: language=c++
from libcpp.string cimport string
from libcpp cimport bool
from libcpp.vector cimport vector
from libcpp.unordered_map cimport unordered_map
from libcpp.utility cimport pair

cdef extern from "src/protobuf/p2p.pb.cc" namespace "p2p":
    cdef cppclass dataFrame:
        dataFrame()

cdef extern from "src/transitMatrix.h" namespace "lmnoel":
    cdef cppclass transitMatrix:
        ctypedef unsigned long int label
        ctypedef unsigned short int value
        transitMatrix(int, bool isSymmetric) except +
        transitMatrix(string, bool isSymmetric, bool isOTPMatrix) except +
        void addToUserSourceDataContainerInt(int, unsigned long int, int, bool) except +
        void addToUserDestDataContainerInt(int, unsigned long int, int) except +
        void addToUserSourceDataContainerString(int, string, int, bool) except +
        void addToUserDestDataContainerString(int, string, int) except +
        void addEdgeToGraph(int, int, int, bool) except +
        void compute(int) except +
        int get(unsigned long int, unsigned long int) except +
        bool writeCSV(string) except +
        bool writeTMX(string) except +
        void printDataFrame() except +
        unordered_map[unsigned long int, vector[label]] getDestsInRange(int, int) except +
        unordered_map[unsigned long int, vector[label]] getSourcesInRange(int, int) except +
        vector[pair[label, value]] getValuesByDest(unsigned long int, bool) except +
        vector[pair[label, value]] getValuesBySource(unsigned long int, bool) except +
        unordered_map[string, unsigned long int] getUserRowIdCache() except +
        unordered_map[string, unsigned long int] getUserColIdCache() except +
        void addToCategoryMap(unsigned long int, string) except +
        unsigned short int timeToNearestDestPerCategory(unsigned long int, string) except +
        unsigned short int countDestsInRangePerCategory(unsigned long int, string, unsigned short int) except +
        unsigned short int timeToNearestDest(unsigned long int) except +
        unsigned short int countDestsInRange(unsigned long int, unsigned short int) except +


cdef class pyTransitMatrix:
    cdef transitMatrix *thisptr

    def __cinit__(self, string infile = "", int vertices = -1, bool isSymmetric = False, isOTPMatrix = False):
        if vertices > 0:
            self.thisptr = new transitMatrix(vertices, isSymmetric)
        else:
            # pass
            self.thisptr = new transitMatrix(infile, isSymmetric, isOTPMatrix)

    def __dealloc__(self):
        del self.thisptr

    def getDestsInRange(self, range_, numThreads):
        return self.thisptr.getDestsInRange(range_, numThreads)

    def getSourcesInRange(self, range_, numThreads):
        return self.thisptr.getSourcesInRange(range_, numThreads)

    def getValuesBySource(self, source_id, sort):
        return self.thisptr.getValuesBySource(source_id, sort)

    def getValuesByDest(self, dest_id, sort):
        return self.thisptr.getValuesByDest(dest_id, sort)

    def addToUserSourceDataContainerInt(self, networkNodeId, id_, lastMileDistance, isBidirectional):
        self.thisptr.addToUserSourceDataContainerInt(networkNodeId, id_, lastMileDistance, isBidirectional)

    def addToUserDestDataContainerInt(self, networkNodeId, id_, lastMileDistance):
        self.thisptr.addToUserDestDataContainerInt(networkNodeId, id_, lastMileDistance)

    def addToUserSourceDataContainerString(self, networkNodeId, id_, lastMileDistance, isBidirectional):
        self.thisptr.addToUserSourceDataContainerString(networkNodeId, id_, lastMileDistance, isBidirectional)

    def addToUserDestDataContainerString(self, networkNodeId, id_, lastMileDistance):
        self.thisptr.addToUserDestDataContainerString(networkNodeId, id_, lastMileDistance)

    def addEdgeToGraph(self, src, dst, weight, isBidirectional):
        self.thisptr.addEdgeToGraph(src, dst, weight, isBidirectional)

    def compute(self, numThreads):
        self.thisptr.compute(numThreads)

    def get(self, source, dest):
        return self.thisptr.get(source, dest)

    def writeCSV(self, outfile):
        return self.thisptr.writeCSV(outfile)

    def writeTMX(self, outfile):
        return self.thisptr.writeTMX(outfile)

    def printDataFrame(self):
        self.thisptr.printDataFrame()

    def getUserRowIdCache(self):
        return self.thisptr.getUserRowIdCache()

    def getUserColIdCache(self):
        return self.thisptr.getUserColIdCache()

    def addToCategoryMap(self, dest_id, category):
        self.thisptr.addToCategoryMap(dest_id, category)

    def timeToNearestDestPerCategory(self, source_id, category):
        return self.thisptr.timeToNearestDestPerCategory(source_id, category)

    def countDestsInRangePerCategory(self, source_id, category, range):
        return self.thisptr.countDestsInRangePerCategory(source_id, category, range)

    def timeToNearestDest(self, source_id):
        return self.thisptr.timeToNearestDest(source_id)

    def countDestsInRange(self, source_id, range):
        return self.thisptr.countDestsInRange(source_id, range)