# distutils: language=c++
from libcpp.string cimport string
from libcpp cimport bool
from libcpp.vector cimport vector
from libcpp.unordered_map cimport unordered_map
from libcpp.utility cimport pair

ctypedef unsigned short int matrix
cdef extern from "src/transitMatrix.cpp" namespace "lmnoel":

    cdef cppclass transitMatrix[int_label, int_label]:
        ctypedef unsigned short int value
        ctypedef unsigned long int int_label

        transitMatrix(bool, unsigned int, unsigned int) except +

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


        unsigned short int getValueById(unsigned long, unsigned long) except +
        unsigned int getRows() except +
        unsigned int getCols() except +
        bool getIsSymmetric() except +
        vector[unsigned short] getDatasetRow(unsigned int) except +
        vector[vector[value]] getDataset() except +
        vector[unsigned long int] getPrimaryDatasetIds() except+
        vector[unsigned long int] getSecondaryDatasetIds() except+

        void setRows(unsigned int) except +
        void setCols(unsigned int) except +
        void setIsSymmetric(bool) except +
        void setDatasetRow(vector[unsigned short], unsigned int) except +
        void setDataset(vector[vector[matrix]]) except +
        void setPrimaryDatasetIds(vector[unsigned long int]) except +
        void setSecondaryDatasetIds(vector[unsigned long int]) except +

        bool writeCSV(string) except +
        void printDataFrame() except +



cdef class pyTransitMatrix:
    cdef transitMatrix *thisptr

    def __cinit__(self, bool isSymmetric, unsigned int rows, unsigned int columns):
        self.thisptr = new transitMatrix(isSymmetric, rows, columns)
        return

    def __dealloc__(self):
        del self.thisptr

    def prepareGraphWithVertices(self, vertices):
        self.thisptr.prepareGraphWithVertices(vertices)

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

    def setDataset(self, dataset):
        cdef vector[vector[matrix]] cpp_input = dataset
        self.thisptr.setDataset(cpp_input)

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