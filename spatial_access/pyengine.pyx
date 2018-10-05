# distutils: language = c++

from transitMatrix cimport transitMatrix

cdef class pyTransitMatrix:
    cdef transitMatrix cpp_transit_matrix

    def __cinit__(self, string infile):
        self.cpp_transit_matrix = transitMatrix(infile)

    def __cinit__(self, int V):
        self.cpp_transit_matrix = transitMatrix(V)

    def addToUserSourceDataContainer(self, networkNodeId, id_, lastMileDistance):
        self.cpp_transit_matrix.addToUserSourceDataContainer(networkNodeId, id_, lastMileDistance)

    def addToUserDestDataContainer(self, networkNodeId, id_, lastMileDistance):
        self.cpp_transit_matrix.addToUserDestDataContainer(networkNodeId, id_, lastMileDistance)

    def addEdgeToGraph(self, src, dst, weight, isBidirectional):
        self.cpp_transit_matrix.addEdgeToGraph(src, dst, weight, isBidirectional)

    def compute(self, impedence, numThreads, outfile):
        self.cpp_transit_matrix.start(impedence, numThreads, outfile)

    def compute(self, impedence, numThreads):
        self.cpp_transit_matrix.start(impedence, numThreads)

    def get(self, source, dest):
        cdef string cpp_source = str.encode(source)
        cdef string cpp_dest = str.encode(dest)
        return self.cpp_transit_matrix.get(cpp_source, cpp_dest)

