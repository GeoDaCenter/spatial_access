# distutils: language=c++
from libcpp.string cimport string
from libcpp cimport bool
from libcpp.vector cimport vector
from libcpp.map cimport map

cdef extern from "src/protobuf/p2p.pb.cc" namespace "p2p":
    cdef cppclass dataFrame:
        dataFrame()

cdef extern from "src/transitMatrix.h" namespace "lmnoel":
    cdef cppclass transitMatrix:
        ctypedef unsigned long int label
        transitMatrix(int, bool isSymmetric) except +
        transitMatrix(string, bool isSymmetric, bool isOTPTransitMatrix) except +
        void addToUserSourceDataContainer(int, unsigned long int, int, bool) except +
        void addToUserDestDataContainer(int, unsigned long int, int) except +
        void addEdgeToGraph(int, int, int, bool) except +
        void compute(int) except +
        int get(unsigned long int, unsigned long int) except +
        bool writeCSV(string) except +
        bool writeTMX(string) except +
        void printDataFrame() except +
        map[unsigned long int, vector[label]] getDestsInRange(int) except +

cdef class pyTransitMatrix:
    cdef transitMatrix *thisptr

    def __cinit__(self, string infile = "", int vertices = -1, bool isSymmetric = False, isOTPTransitMatrix = False):
        if vertices > 0:
            self.thisptr = new transitMatrix(vertices, isSymmetric)
        else:
            # pass
            self.thisptr = new transitMatrix(infile, isSymmetric, isOTPTransitMatrix)

    def __dealloc__(self):
        del self.thisptr

    def getDestsInRange(self, range_):
        return self.thisptr.getDestsInRange(range_)

    def addToUserSourceDataContainer(self, networkNodeId, id_, lastMileDistance, isBidirectional):
        self.thisptr.addToUserSourceDataContainer(networkNodeId, id_, lastMileDistance, isBidirectional)

    def addToUserDestDataContainer(self, networkNodeId, id_, lastMileDistance):
        self.thisptr.addToUserDestDataContainer(networkNodeId, id_, lastMileDistance)

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

