# distutils: language=c++
from libcpp.string cimport string
from libcpp cimport bool
from libcpp.vector cimport vector
from libcpp.unordered_map cimport unordered_map
from libcpp.utility cimport pair

cdef extern from "src/transitMatrix.cpp" namespace "lmnoel":

    cdef cppclass transitMatrix[string,string]:
        ctypedef unsigned short int value

        transitMatrix(bool, unsigned int, unsigned int) except +

        void prepareGraphWithVertices(int V) except +
        void addToUserSourceDataContainer(unsigned int, string, unsigned short int) except +
        void addToUserDestDataContainer(unsigned int, string, unsigned short int) except +
        void addEdgeToGraph(int, int, int, bool) except +
        void addToCategoryMap(string, string) except +

        void compute(int) except +
        vector[pair[string, value]] getValuesByDest(string, bool) except +
        vector[pair[string, value]] getValuesBySource(string, bool) except +
        unordered_map[string, vector[string]] getDestsInRange(string, int) except +
        unordered_map[string, vector[string]] getSourcesInRange(string, int) except +
        unsigned short int timeToNearestDestPerCategory(string, string) except +
        unsigned short int countDestsInRangePerCategory(string, string, unsigned short int) except +
        unsigned short int timeToNearestDest(string) except +
        unsigned short int countDestsInRange(string, unsigned short int) except +


        unsigned short int getValueById(unsigned long, unsigned long) except +
        unsigned int getRows() except +
        unsigned int getCols() except +
        bool getIsSymmetric() except +
        vector[unsigned short] getDatasetRow(unsigned int) except +
        vector[vector[value]] getDataset() except +
        vector[string] getPrimaryDatasetIds() except+
        vector[string] getSecondaryDatasetIds() except+

        void setRows(unsigned int) except +
        void setCols(unsigned int) except +
        void setIsSymmetric(bool) except +
        void setDatasetRow(vector[unsigned short], unsigned int) except +
        void setPrimaryDatasetIds(vector[string]) except +
        void setSecondaryDatasetIds(vector[string]) except +

        bool writeCSV(string) except +
        void printDataFrame() except +



cdef class pyTransitMatrix:
    cdef transitMatrix *thisptr

    def __cinit__(self, bool isSymmetric, unsigned int rows, unsigned int columns):
        self.thisptr = new transitMatrix(isSymmetric, rows, columns)
        return

    def __dealloc__(self):
        if self.thisptr is not NULL:
            del self.thisptr
            self.thisptr = NULL

    def getDestsInRange(self, range_, numThreads):
        return self.thisptr.getDestsInRange(range_, numThreads)

    def getSourcesInRange(self, range_, numThreads):
        return self.thisptr.getSourcesInRange(range_, numThreads)

    def getValuesBySource(self, source_id, sort):
        return self.thisptr.getValuesBySource(source_id, sort)

    def getValuesByDest(self, dest_id, sort):
        return self.thisptr.getValuesByDest(dest_id, sort)

    def addToUserSourceDataContainer(self, networkNodeId, id_, lastMileDistance):
        self.thisptr.addToUserSourceDataContainer(networkNodeId, id_, lastMileDistance)

    def addToUserDestDataContainer(self, networkNodeId, id_, lastMileDistance):
        self.thisptr.addToUserDestDataContainer(networkNodeId, id_, lastMileDistance)


    def addEdgeToGraph(self, src, dst, weight, isBidirectional):
        self.thisptr.addEdgeToGraph(src, dst, weight, isBidirectional)

    def compute(self, numThreads):
        self.thisptr.compute(numThreads)

    def getValueById(self, source, dest):
        return self.thisptr.getValueById(source, dest)

    def writeCSV(self, outfile):
        return self.thisptr.writeCSV(outfile)

    def printDataFrame(self):
        self.thisptr.printDataFrame()

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

    def setRows(self, rows):
        self.thisptr.setRows(rows)

    def setCols(self, cols):
        self.thisptr.setCols(cols)

    def setIsSymmetric(self, isSymmetric):
        self.thisptr.setIsSymmetric(isSymmetric)

    def setDatasetRow(self, datasetRow, rowNum):
        self.thisptr.setDatasetRow(datasetRow, rowNum)

    def setPrimaryDatasetIds(self, primaryDatasetIds):
        self.thisptr.setPrimaryDatasetIds(primaryDatasetIds)

    def setSecondaryDatasetIds(self, secondaryDatasetIds):
        self.thisptr.setSecondaryDatasetIds(secondaryDatasetIds)

    def getRows(self):
        return self.thisptr.getRows()

    def getCols(self):
        return self.thisptr.getCols()

    def getIsSymmetric(self):
        return self.thisptr.getIsSymmetric()

    def getDatasetRow(self, rowNum):
        return self.thisptr.getDatasetRow(rowNum)

    def getDataset(self):
        return self.thisptr.getDataset()

    def getPrimaryDatasetIds(self):
        return self.thisptr.getPrimaryDatasetIds()

    def getSecondaryDatasetIds(self):
        return self.thisptr.getSecondaryDatasetIds()