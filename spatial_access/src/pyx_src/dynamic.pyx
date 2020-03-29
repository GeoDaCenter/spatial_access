cdef extern from "include/transitMatrix.h":
    cdef cppclass {{ class_name }} "transitMatrix<{{ row_type_full }}, {{ col_type_full }},{{ value_type_full }}>":


        {{ class_name }}(bool, bool, unsigned int, unsigned int) except +
        {{ class_name }}() except +

        void prepareGraphWithVertices(int V) except +
        void addToUserSourceDataContainer(unsigned int, {{ row_type }}, {{ value_type }}) except +
        void addToUserDestDataContainer(unsigned int, {{ col_type }}, {{ value_type }}) except +
        void addEdgesToGraph(vector[ulong], vector[ulong], vector[{{ value_type }}], vector[bool]) except +
        void addToCategoryMap({{ col_type }}, string) except +
        void setMockDataFrame(vector[vector[{{ value_type }}]], vector[{{ row_type }}], vector[{{ col_type }}]) except +

        void compute(int) except +
        vector[pair[{{ row_type }}, {{ value_type }}]] getValuesByDest({{ col_type }}, bool) except +
        vector[pair[{{ col_type }}, {{ value_type }}]] getValuesBySource({{ row_type }}, bool) except +
        unordered_map[{{ row_type }}, vector[{{ col_type }}]] getDestsInRange({{ value_type }}) except +
        unordered_map[{{ col_type }}, vector[{{ row_type }}]] getSourcesInRange({{ value_type }}) except +
        {{ value_type }} timeToNearestDestPerCategory({{ row_type }}, string) except +
        {{ value_type }} countDestsInRangePerCategory({{ row_type }}, string, {{ value_type }}) except +
        {{ value_type }} timeToNearestDest({{ row_type }}) except +
        {{ value_type }} countDestsInRange({{ row_type }}, {{ value_type }}) except +

        vector[{{ col_type }}] getColIds() except +
        vector[{{ row_type }}] getRowIds() except +

        void writeCSV(string) except +
        void writeTMX(string) except +
        void readTMX(string) except +
        void readCSV(string) except +
        void readOTPCSV(string) except +
        void printDataFrame() except +

cdef class  {{ py_class_name }}:
    cdef {{ class_name }} *thisptr

    def __cinit__(self, bool isCompressible=False, bool isSymmetric=False, unsigned int rows=0, unsigned int columns=0):
        if rows == 0 and columns == 0:
            self.thisptr = new {{ class_name }}()
        else:
            self.thisptr = new {{ class_name }}(isCompressible, isSymmetric, rows, columns)

    def __dealloc__(self):
        del self.thisptr

    def prepareGraphWithVertices(self, vertices):
        self.thisptr.prepareGraphWithVertices(vertices)


    def addToUserSourceDataContainer(self, networkNodeId, id_, lastMileDistance):
        self.thisptr.addToUserSourceDataContainer(networkNodeId, id_, lastMileDistance)

    def addToUserDestDataContainer(self, networkNodeId, id_, lastMileDistance):
        self.thisptr.addToUserDestDataContainer(networkNodeId, id_, lastMileDistance)

    def addEdgesToGraph(self, from_column, to_column, edge_weight_column, is_bidirectional_column):
        self.thisptr.addEdgesToGraph(from_column, to_column, edge_weight_column, is_bidirectional_column)

    def setMockDataFrame(self, dataset, row_ids, col_ids):
        self.thisptr.setMockDataFrame(dataset, row_ids, col_ids)

    def compute(self, numThreads):
        self.thisptr.compute(numThreads)

    def writeCSV(self, outfile):
        self.thisptr.writeCSV(outfile)

    def writeTMX(self, outfile):
        self.thisptr.writeTMX(outfile)

    def readTMX(self, infile):
        self.thisptr.readTMX(infile)

    def readCSV(self, infile):
        self.thisptr.readCSV(infile)

    def readOTPCSV(self, infile):
        self.thisptr.readOTPCSV(infile)

    def printDataFrame(self):
        self.thisptr.printDataFrame()

    def getValuesBySource(self, source_id, sort):
        return self.thisptr.getValuesBySource(source_id, sort)

    def getValuesByDest(self, dest_id, sort):
        return self.thisptr.getValuesByDest(dest_id, sort)

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

    def getColIds(self):
        return self.thisptr.getColIds()

    def getRowIds(self):
        return self.thisptr.getRowIds()

    def getSourcesInRange(self, range_):
        return self.thisptr.getSourcesInRange(range_)

    def getDestsInRange(self, range_):
        return self.thisptr.getDestsInRange(range_)