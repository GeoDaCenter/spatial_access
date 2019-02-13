# distutils: language=c++
from libcpp.string cimport string
from libcpp cimport bool
from libcpp.vector cimport vector
from libcpp.unordered_map cimport unordered_map
from libcpp.utility cimport pair

ctypedef unsigned short int value
ctypedef unsigned long ulong
cdef extern from "src/transitMatrix.cpp" namespace "lmnoel":

    cdef cppclass transitMatrix[int_label, string]:
        ctypedef unsigned long int int_label

        transitMatrix(bool, unsigned int, unsigned int) except +

        void prepareGraphWithVertices(int V) except +
        void addToUserSourceDataContainer(unsigned int, unsigned long, unsigned short int) except +
        void addToUserDestDataContainer(unsigned int, string, unsigned short int) except +
        void addEdgeToGraph(int, int, int, bool) except +
        void addToCategoryMap(string, string) except +

        void compute(int) except +
        vector[pair[ulong, value]] getValuesByDest(string, bool) except +
        vector[pair[string, value]] getValuesBySource(unsigned long, bool) except +
        unordered_map[ulong, vector[string]] getDestsInRange(unsigned int, int) except +
        unordered_map[string, vector[ulong]] getSourcesInRange(unsigned int, int) except +
        unsigned short int timeToNearestDestPerCategory(unsigned long, string) except +
        unsigned short int countDestsInRangePerCategory(unsigned long, string, unsigned short int) except +
        unsigned short int timeToNearestDest(unsigned long) except +
        unsigned short int countDestsInRange(unsigned long, unsigned short int) except +


        unsigned short int getValueById(unsigned long, string) except +
        unsigned int getRows() except +
        unsigned int getCols() except +
        bool getIsSymmetric() except +
        vector[unsigned short] getDatasetRow(unsigned int) except +
        vector[vector[value]] getDataset() except +
        vector[unsigned long int] getPrimaryDatasetIds() except+
        vector[string] getSecondaryDatasetIds() except+

        void setRows(unsigned int) except +
        void setCols(unsigned int) except +
        void setIsSymmetric(bool) except +
        void setDatasetRow(vector[unsigned short], unsigned int) except +
        void setDataset(vector[vector[value]]) except +
        void setPrimaryDatasetIds(vector[unsigned long int]) except +
        void setSecondaryDatasetIds(vector[string]) except +

        bool writeCSV(string) except +
        void printDataFrame() except +



cdef class pyTransitMatrix:
    cdef transitMatrix *thisptr

    def __cinit__(self, bool isSymmetric, unsigned int rows, unsigned int columns):
        self.thisptr = new transitMatrix(isSymmetric, rows, columns)
        return

    def __dealloc__(self):
        del self.thisptr

    def getDestsInRange(self, range_, numThreads):
        cdef unordered_map[ulong, vector[string]] py_res = self.thisptr.getDestsInRange(range_, numThreads)
        return py_res

    def getSourcesInRange(self, range_, numThreads):
        cdef unordered_map[string, vector[ulong]] py_res = self.thisptr.getSourcesInRange(range_, numThreads)
        return py_res

    def getValuesBySource(self, source_id, sort):
        cdef vector[pair[string, value]] cpp_result = self.thisptr.getValuesBySource(source_id, sort)
        return cpp_result

    def getValuesByDest(self, dest_id, sort):
        cdef string dest_id_string = str.encode(dest_id)
        return self.thisptr.getValuesByDest(dest_id_string, sort)

    def addToUserSourceDataContainer(self, networkNodeId, source_id, lastMileDistance):
        self.thisptr.addToUserSourceDataContainer(networkNodeId, source_id, lastMileDistance)

    def addToUserDestDataContainer(self, networkNodeId, dest_id, lastMileDistance):
        cdef string dest_id_string = str.encode(dest_id)
        self.thisptr.addToUserDestDataContainer(networkNodeId, dest_id_string, lastMileDistance)


    def addEdgeToGraph(self, src, dst, weight, isBidirectional):
        self.thisptr.addEdgeToGraph(src, dst, weight, isBidirectional)

    def compute(self, numThreads):
        self.thisptr.compute(numThreads)

    def getValueById(self, source, dest):
        cdef string dest_string = str.encode(source)
        return self.thisptr.getValueById(source, dest_string)

    def writeCSV(self, outfile):
        cdef string outfile_string = str.encode(outfile)
        return self.thisptr.writeCSV(outfile_string)

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

    def setRows(self, rows):
        self.thisptr.setRows(rows)

    def setCols(self, cols):
        self.thisptr.setCols(cols)

    def setIsSymmetric(self, isSymmetric):
        self.thisptr.setIsSymmetric(isSymmetric)

    def setDatasetRow(self, datasetRow, rowNum):
        self.thisptr.setDatasetRow(datasetRow, rowNum)

    def setDataset(self, dataset):
        cdef vector[vector[value]] cpp_input = dataset
        self.thisptr.setDataset(cpp_input)

    def setPrimaryDatasetIds(self, primaryDatasetIds):
        self.thisptr.setPrimaryDatasetIds(primaryDatasetIds)

    def setSecondaryDatasetIds(self, secondaryDatasetIds):
        cdef vector[string] cpp_input = []
        for element in secondaryDatasetIds:
            cpp_input.push_back(element)
        self.thisptr.setSecondaryDatasetIds(cpp_input)

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
        cdef vector[string] py_result = self.thisptr.getSecondaryDatasetIds()
        return py_result