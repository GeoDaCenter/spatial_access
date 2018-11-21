# distutils: language=c++
from libcpp.string cimport string
from libcpp cimport bool

cdef extern from "src/utils/serializer/p2p.pb.cc" namespace "p2p":
    cdef cppclass dataFrame:
        dataFrame()

cdef extern from "src/transitMatrix.h" namespace "lmnoel":

    cdef cppclass transitMatrix:
        transitMatrix(string, bool isSymmetric) except +
        transitMatrix(int, bool isSymmetric) except +
        void addToUserSourceDataContainer(int, unsigned long int, int, bool) except +
        void addToUserDestDataContainer(int, unsigned long int, int) except +
        void addEdgeToGraph(int, int, int, bool) except +
        void compute(int) except +
        int get(unsigned long int, unsigned long int) except +
        bool writeCSV(string) except +
        bool writeTMX(string) except +
        void printDataFrame() except +

cdef class pyTransitMatrix:
    cdef transitMatrix *thisptr

    def __cinit__(self, string infile = "", int vertices = -1, bool isSymmetric = False):
        if vertices > 0:
            self.thisptr = new transitMatrix(vertices, isSymmetric)
        else:

            self.thisptr = new transitMatrix(infile, isSymmetric)

    def __dealloc__(self):
        del self.thisptr

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

