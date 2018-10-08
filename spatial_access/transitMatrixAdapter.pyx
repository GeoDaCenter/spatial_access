from libcpp.string cimport string
from libcpp cimport bool


cdef extern from "src/transitMatrix.h" namespace "lmnoel":

    cdef cppclass transitMatrix:
        transitMatrix(string) except +
        transitMatrix(int) except +
        void addToUserSourceDataContainer(int, string, int, bool) except +
        void addToUserDestDataContainer(int, string, int) except +
        void addEdgeToGraph(int, int, int, bool) except +
        void compute(float, int) except +
        int get(string, string) except +
        bool writeCSV(string) except +
        void printDataFrame() except +

cdef class pyTransitMatrix:
    cdef transitMatrix *thisptr

    def __cinit__(self, string infile = "", int vertices = -1):
        if vertices > 0:
            self.thisptr = new transitMatrix(vertices)
        else:

            self.thisptr = new transitMatrix(infile)

    def __dealloc__(self):
        del self.thisptr

    def addToUserSourceDataContainer(self, networkNodeId, id_, lastMileDistance, isBidirectional):
       #cdef string cpp_id = id_.encode('UTF-8')
        self.thisptr.addToUserSourceDataContainer(networkNodeId, id_, lastMileDistance, isBidirectional)

    def addToUserDestDataContainer(self, networkNodeId, id_, lastMileDistance):
        #cdef string cpp_id = id_.encode('UTF-8')
        self.thisptr.addToUserDestDataContainer(networkNodeId, id_, lastMileDistance)

    def addEdgeToGraph(self, src, dst, weight, isBidirectional):
        self.thisptr.addEdgeToGraph(src, dst, weight, isBidirectional)

    def compute(self, impedence, numThreads):
        self.thisptr.compute(impedence, numThreads)

    def get(self, source, dest):
        # cdef string cpp_source = source.encode('UTF-8')
        # cdef string cpp_dest = dest.encode('UTF-8')
        return self.thisptr.get(source, dest)

    def writeCSV(self, outfile):
        # cdef string cpp_outfile = outfile.encode('UTF-8')
        return self.thisptr.writeCSV(outfile)

    def printDataFrame(self):
        self.thisptr.printDataFrame()

