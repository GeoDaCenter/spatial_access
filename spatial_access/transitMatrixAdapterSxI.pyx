# distutils: language=c++
from libcpp.string cimport string
from libcpp cimport bool
from libcpp.vector cimport vector
from libcpp.unordered_map cimport unordered_map
from libcpp.utility cimport pair

ctypedef unsigned short int value
ctypedef unsigned long ulong
cdef extern from "src/transitMatrix.cpp" namespace "lmnoel":

    cdef cppclass transitMatrix[string, int_label]:
        ctypedef unsigned long int int_label

        transitMatrix(bool, unsigned int, unsigned int) except +

        void prepareGraphWithVertices(int V) except +
        void addToUserSourceDataContainer(unsigned int, string, unsigned short int) except +
        void addToUserDestDataContainer(unsigned int, unsigned long, unsigned short int) except +
        void addEdgeToGraph(int, int, int, bool) except +
        void addToCategoryMap(unsigned long, string) except +

        void compute(int) except +
        vector[pair[string, value]] getValuesByDest(unsigned long, bool) except +
        vector[pair[ulong, value]] getValuesBySource(string, bool) except +
        unordered_map[string, vector[ulong]] getDestsInRange(unsigned int, int) except +
        unordered_map[ulong, vector[string]] getSourcesInRange(unsigned int, int) except +
        unsigned short int timeToNearestDestPerCategory(string, string) except +
        unsigned short int countDestsInRangePerCategory(string, string, unsigned short int) except +
        unsigned short int timeToNearestDest(string) except +
        unsigned short int countDestsInRange(string, unsigned short int) except +


        unsigned short int getValueById(string, unsigned long) except +
        unsigned int getRows() except +
        unsigned int getCols() except +
        bool getIsSymmetric() except +
        vector[unsigned short] getDatasetRow(unsigned int) except +
        vector[vector[value]] getDataset() except +
        vector[string] getPrimaryDatasetIds() except+
        vector[unsigned long int] getSecondaryDatasetIds() except+

        void setRows(unsigned int) except +
        void setCols(unsigned int) except +
        void setIsSymmetric(bool) except +
        void setDatasetRow(vector[unsigned short], unsigned int) except +
        void setDataset(vector[vector[value]]) except +
        void setPrimaryDatasetIds(vector[string]) except +
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
        cdef unordered_map[string, vector[ulong]] py_res = self.thisptr.getDestsInRange(range_, numThreads)
        return py_res

    def getSourcesInRange(self, range_, numThreads):
        cdef unordered_map[ulong, vector[string]] py_res = self.thisptr.getSourcesInRange(range_, numThreads)
        return py_res

    def getValuesBySource(self, source_id, sort):
        cdef string source_id_string = str.encode(source_id)
        return self.thisptr.getValuesBySource(source_id_string, sort)

    def getValuesByDest(self, dest_id, sort):
        cdef vector[pair[string, value]] cpp_result = self.thisptr.getValuesByDest(dest_id, sort)
        return cpp_result

    def addToUserSourceDataContainer(self, networkNodeId, source_id, lastMileDistance):
        cdef string source_id_string = str.encode(source_id)
        self.thisptr.addToUserSourceDataContainer(networkNodeId, source_id_string, lastMileDistance)

    def addToUserDestDataContainer(self, networkNodeId, id_, lastMileDistance):
        self.thisptr.addToUserDestDataContainer(networkNodeId, id_, lastMileDistance)


    def addEdgeToGraph(self, src, dst, weight, isBidirectional):
        self.thisptr.addEdgeToGraph(src, dst, weight, isBidirectional)

    def compute(self, numThreads):
        self.thisptr.compute(numThreads)

    def getValueById(self, source, dest):
        cdef string source_string = str.encode(source)
        return self.thisptr.getValueById(source_string, dest)

    def writeCSV(self, outfile):
        cdef string outfile_string = str.encode(outfile)
        return self.thisptr.writeCSV(outfile_string)

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
        cdef vector[string] cpp_input = []
        for element in primaryDatasetIds:
            cpp_input.push_back(element)
        self.thisptr.setPrimaryDatasetIds(cpp_input)

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
        cdef vector[string] py_result = self.thisptr.getPrimaryDatasetIds()
        return py_result

    def getSecondaryDatasetIds(self):
        return self.thisptr.getSecondaryDatasetIds()