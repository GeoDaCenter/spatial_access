#include <sstream>
#include <iostream>
#include <fstream>
#include <string>
#include <string.h>
#include <mutex>
#include <thread>
#include <stdexcept>
#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <utility>

#include "utils/json.h"
#include "utils/LimitedQueue.h"
#include "utils/threadUtilities.h"
#include "utils/dataFrame.h"

using namespace std;

#define ID_MAX_LEN (20)

#define WRITE_ONLY (0)
#define WRITE_AND_LOAD (1)
#define LOAD_ONLY (2)
#define READ_ONLY (3)


/* struct to represent a single source associated with */
/* a single network node */
typedef struct nnSingleEntry {
    char* id;
    int dist;
    int pos;
} nnSingleEntry;


/* struct to represent the multiple possible sources associated */
/* with a single network node */
typedef struct nnMultiEntry {
    nnSingleEntry *entries;
    int n_entries;
} nnMultiEntry;


/* class to represent a single column entry*/
class nnCols {
public:
    nnMultiEntry* me;

    void addCol(int col_no, char* id, int dist);
    void init(string infile, int N);
    ~nnCols(void);
};


/* add a single colunmn entry to the sparse network from file*/
void nnCols::addCol(int col_no, char* id, int dist) {
    nnSingleEntry se;
    se.id = id;
    se.pos = col_no;
    se.dist = dist; 
    me->entries[me->n_entries] = se;
    me->n_entries++;
}


/* initialize the nnCols class from sparse network in file*/
void nnCols::init(string infile, int N) {
    ifstream fileIN;
    fileIN.open(infile);
    if (fileIN.fail()) {
        throw runtime_error("Could not load input nn_file");
    }
    me = (nnMultiEntry*) malloc(sizeof(nnMultiEntry));
    me->n_entries = 0;
    me->entries = (nnSingleEntry*) malloc(sizeof(nnSingleEntry) * (N + 1));
    int col_no, dist;
    const char* id;

    string line;
    while (getline(fileIN, line)) {
        istringstream stream(line);
        string input;
        getline(stream, input,',');
        col_no = (int) stoi(input);
        getline(stream, input,',');
        id = strndup(input.c_str(), ID_MAX_LEN);
        getline(stream, input,',');
        dist = (int) stoi(input);
        addCol(col_no, (char *) id, dist);
    }
}


/* destructor for the nnCols class*/
nnCols::~nnCols(void) {
    for (int i = 0; i < me->n_entries; i++) {
        //free(me->entries[i].id);
    } 
    free(me->entries);
    free(me);
}


/* class to represent the rows of a sparse network*/
class nnTable {
public:
    unordered_map<int, nnMultiEntry*> map;
    unordered_set <int> s;
    void addRow(int row_no, char* id, int dist);
    void init(string infile, int N);
    nnMultiEntry* findMatchingEntries(int row_no);
    ~nnTable();
};


/* add a single row entry to the sparse network from file*/
void nnTable::addRow(int row_no, char* id, int dist) {

    nnSingleEntry se;
    se.id = id;
    se.dist = dist;
    se.pos = row_no;

    nnMultiEntry *me;
    if (s.find(row_no) == s.end()) {
        me = (nnMultiEntry*) malloc(sizeof(nnMultiEntry));
        me->n_entries = 1;
        me->entries = (nnSingleEntry*) malloc(sizeof(nnSingleEntry));
        me->entries[0] = se;
        s.insert(row_no);

    } else {

        me = map[row_no];
        me->n_entries++;

        me->entries = (nnSingleEntry*) realloc(me->entries, 
            sizeof(nnSingleEntry) * (me->n_entries));
        me->entries[me->n_entries - 1] = se;
    }
    map[row_no] = me;
}


/*initialize the nnTable class with sparse network from file*/
void nnTable::init(string infile, int N) {
    map.reserve(N);
    ifstream fileIN;
    fileIN.open(infile);
    if (fileIN.fail()) {
        throw runtime_error("Could not load input nn_file");
    }
    int row_no, dist;
    const char* id;

    string line;
    while (getline(fileIN, line)) {
        istringstream stream(line);
        string input;
        getline(stream, input,',');
        row_no = (int) stoi(input);
        getline(stream, input,',');
        id = strndup(input.c_str(), ID_MAX_LEN);
        getline(stream, input,',');
        dist = (int) stoi(input);
        addRow(row_no, (char *)id, dist);
    }
    fileIN.close();

}


/*destructor for the nnTable class*/
nnTable::~nnTable(void) {
    unordered_map<int, nnMultiEntry*>::iterator itr;

    for (itr = map.begin(); itr != map.end(); itr++) {
        for (int i = 0; i < itr->second->n_entries; i++) {
            free(itr->second->entries[i].id);
        }
        free(itr->second->entries);
        free(itr->second);
    }
}


/* find all sources attached to the given node id*/
nnMultiEntry* nnTable::findMatchingEntries(int row_no) {
    if (s.find(row_no) != s.end()) {
        return map[row_no];
    } else {
        return NULL;
    }
}

 
/* A structure to represent a node in adjacency list*/
typedef struct AdjListNode
{
    int dest;
    int weight;
    struct AdjListNode* next;
} AdjListNode;
 

/* A structure to represent an adjacency list*/
typedef struct AdjList
{
    struct AdjListNode *head;  // pointer to head node of list
} AdjList;
 

/* A structure to represent a graph. A graph is an array of adjacency lists.*/
/* Size of array will be V (number of vertices in graph)*/
typedef struct Graph
{
    int V;
    struct AdjList* array;
} Graph;


/* Structure to represent a min heap node */
typedef struct MinHeapNode
{
    int  v;
    int dist;
} MinHeapNode;
 
/* Structure to represent a min heap */
typedef struct MinHeap
{
    int size;      // Number of heap nodes present currently
    int capacity;  // Capacity of min heap
    int *pos;     // This is needed for decreaseKey()
    struct MinHeapNode *array;
} MinHeap;


/* A utility function to create a new Min Heap Node */
void newMinHeapNode(int v, int dist, MinHeapNode *new_node)
{
    new_node->v = v;
    new_node->dist = dist;
}

 
/* A utility function to create a new adjacency list node*/
struct AdjListNode* newAdjListNode(int dest, int weight)
{
    struct AdjListNode* newNode =
            (struct AdjListNode*) malloc(sizeof(struct AdjListNode));
    newNode->dest = dest;
    newNode->weight = weight;
    newNode->next = NULL;
    return newNode;
}

 
/* A utility function that creates a graph of V vertices*/
struct Graph* createGraph(int V)
{
    struct Graph* graph = (struct Graph*) malloc(sizeof(struct Graph));
    graph->V = V;
 
    // Create an array of adjacency lists.  Size of array will be V
    graph->array = (struct AdjList*) malloc(V * sizeof(struct AdjList));
 
     // Initialize each adjacency list as empty by making head as NULL
    for (int i = 0; i < V; ++i)
        graph->array[i].head = NULL;
 
    return graph;
}

 
/* free a graph struct*/
void freeGraph(Graph* graph) {
    free(graph->array);
    free(graph);
}


/* Adds an edge to an undirected graph */
void addEdge(struct Graph* graph, int src, int dest, int weight)
{
    // Add an edge from src to dest.  A new node is added to the adjacency
    // list of src.  The node is added at the begining
    struct AdjListNode* newNode = newAdjListNode(dest, weight);
    newNode->next = graph->array[src].head;
    graph->array[src].head = newNode;
 
}

/* Utility function to read edge list from .csv*/
void readCSV(Graph* graph, string infile) {
    ifstream fileIN;

    int src, dst, edge_weight;

    fileIN.open(infile);
    if (fileIN.fail()) {
        throw runtime_error("Could not load input file");
    }

    string line;
    
    while (getline(fileIN, line)) {
        istringstream stream(line);
        string input;
        getline(stream, input,',');
        src = (int) stoi(input);
        getline(stream, input,',');
        dst = (int) stoi(input);
        getline(stream, input,',');
        edge_weight = (int) stoi(input);
        addEdge(graph, src, dst, edge_weight);

    }
}


/* write the header line for the output file */
void writeHeader(nnCols *snn, string outfile) {
    ofstream Ofile;

    Ofile.open(outfile);
    if (Ofile.fail()) {
        throw runtime_error("Could not open output file");
    }
    Ofile << ",";
    for (int i = 0; i < snn->me->n_entries; i++) {
        Ofile << snn->me->entries[i].id;
        if (i < snn->me->n_entries - 1) {
            Ofile << ",";
        }
    }
    Ofile << endl;
    Ofile.close();

}

/* class to manage worker thread data */
class workerArgs {
public:
    Graph* graph;
    jobQueue jq;
    nnTable primaryNN;
    nnCols secondaryNN;
    json_2d json;
    string outfile;
    dataFrame *df;
    float impedence;
    int mode;
    int N;
    int user_cols;
    int write_mode;
    mutex write_lock;
    mutex insert_data;
    workerArgs(string infile, string outfile_in, float impedence_in, 
        int mode_in, int N_in, int user_cols_in,
        string nn_prim_in, string nn_sec_in, dataFrame *df_in, int write_mode);
    workerArgs(void);
    ~workerArgs(void);

};

workerArgs::workerArgs(void) {

}


/* wa initializer */
workerArgs::workerArgs(string infile, string outfile_in, float impedence_in, 
    int mode_in, int N_in, int user_cols_in, string nn_prim_in, 
    string nn_sec_in, dataFrame *df_in, int write_mode_in) {

    //init values
    impedence = impedence_in;
    mode = mode_in;
    N = N_in;
    user_cols = user_cols_in;
    outfile = string(outfile_in);
    df = df_in;
    write_mode = write_mode_in;

    //init graph
    graph = createGraph(N);
    readCSV(graph, infile);
    //init input tables

    primaryNN.init(nn_prim_in, N);
    secondaryNN.init(nn_sec_in, user_cols);

    if (write_mode <= 1) {
       writeHeader(&secondaryNN, outfile); 
    }

    //initialize job queue
    for (int i = 0; i < N; i++) {
        jq.insert(i);
    }

 }


/* wa destructor */
workerArgs::~workerArgs(void) {

    //write data if json type
    if (mode) {
        if ((write_mode == WRITE_ONLY) || (write_mode == WRITE_AND_LOAD)) {
            json.write(outfile);
        }
    }

    //clean up
    
    struct AdjListNode *AdjListNode;
    struct AdjListNode *temp;
    for (int i = 0; i < graph->V; i++) {
        if (graph->array[i].head) {
            AdjListNode = graph->array[i].head;
            while (AdjListNode) {
                temp = AdjListNode->next;
                free(AdjListNode);
                AdjListNode = temp;
            }

        }
    }

    freeGraph(graph);

}

 
/* A utility function to create a Min Heap*/
struct MinHeap* createMinHeap(int capacity)
{
    struct MinHeap* minHeap =
         (struct MinHeap*) malloc(sizeof(struct MinHeap));
    minHeap->pos = (int *)malloc(capacity * sizeof(int));
    minHeap->size = 0;
    minHeap->capacity = capacity;
    minHeap->array =
         (struct MinHeapNode*) malloc(capacity * sizeof(struct MinHeapNode));
    return minHeap;
}


/* free a minHeap struct*/
void freeMinheap(MinHeap* minHeap) {
    free(minHeap->pos);
    free(minHeap->array);
    free(minHeap);
}


/* A utility function to swap two nodes of min heap. Needed for min heapify*/
void swapMinHeapNode(struct MinHeapNode* a, struct MinHeapNode* b)
{
    struct MinHeapNode t;
    t.v = a->v;
    t.dist = a->dist;

    a->v = b->v;
    a->dist = b->dist;

    b->v = t.v;
    b->dist = t.dist;

}
 

/* A standard function to heapify at given idx */
/* This function also updates position of nodes when they are swapped.*/
/* Position is needed for decreaseKey()*/
void minHeapify(struct MinHeap* minHeap, int idx)
{
    int smallest, left, right;
    smallest = idx;
    left = 2 * idx + 1;
    right = 2 * idx + 2;
 
    if (left < minHeap->size &&
        minHeap->array[left].dist < minHeap->array[smallest].dist )
      smallest = left;
 
    if (right < minHeap->size &&
        minHeap->array[right].dist < minHeap->array[smallest].dist )
      smallest = right;
 
    if (smallest != idx)
    {
        // The nodes to be swapped in min heap
        MinHeapNode smallestNode = minHeap->array[smallest];
        MinHeapNode idxNode = minHeap->array[idx];
 
        // Swap positions
        minHeap->pos[smallestNode.v] = idx;
        minHeap->pos[idxNode.v] = smallest;
 
        // Swap nodes
        swapMinHeapNode(&minHeap->array[smallest], &minHeap->array[idx]);
        minHeapify(minHeap, smallest);
    }
}
 

/* A utility function to check if the given minHeap is ampty or not*/
int isEmpty(struct MinHeap* minHeap)
{
    return minHeap->size == 0;
}

 
/* Standard function to extract minimum node from heap*/
void extractMin(struct MinHeap* minHeap, struct MinHeapNode *minHeapNode)
{
    if (isEmpty(minHeap))
        return ;
 
    // Store the root node
    struct MinHeapNode root = minHeap->array[0];
 
    // Replace root node with last node
    struct MinHeapNode lastNode = minHeap->array[minHeap->size - 1];
    minHeap->array[0] = lastNode;
 
    // Update position of last node
    minHeap->pos[root.v] = minHeap->size-1;
    minHeap->pos[lastNode.v] = 0;
 
    // Reduce heap size and heapify root
    --minHeap->size;
    minHeapify(minHeap, 0);
 
    *minHeapNode = root;
}

 
/* Function to decreasy dist value of a given vertex v. This function*/
/* uses pos[] of min heap to get the current index of node in min heap*/
void decreaseKey(struct MinHeap* minHeap, int v, int dist)
{
    // Get the index of v in  heap array
    int i = minHeap->pos[v];
 
    // Get the node and update its dist value
    minHeap->array[i].dist = dist;
 
    // Travel up while the complete tree is not heapified.
    // This is a O(Logn) loop
    while (i && minHeap->array[i].dist < minHeap->array[(i - 1) / 2].dist)
    {
        // Swap this node with its parent
        minHeap->pos[minHeap->array[i].v] = (i-1)/2;
        minHeap->pos[minHeap->array[(i-1)/2].v] = i;
        swapMinHeapNode(&minHeap->array[i],  &minHeap->array[(i - 1) / 2]);
 
        // move to parent index
        i = (i - 1) / 2;
    }
}

 
/* A utility function to check if a given vertex*/
/* 'v' is in min heap or not*/
bool isInMinHeap(struct MinHeap *minHeap, int v)
{
   if (minHeap->pos[v] < minHeap->size)
     return true;
   return false;
}


/*write_row: write a row to file*/
void writeRow(int* dist, nnMultiEntry* me_prim, workerArgs *wa) {
    ofstream Ofile;
    if ((wa->write_mode == WRITE_ONLY) || (wa->write_mode == WRITE_AND_LOAD)) {
        Ofile.open(wa->outfile, ios_base::app);
        wa->write_lock.lock();
    }
    int src_imp, dst_imp, calc_imp, fin_imp;
    for (int i = 0; i < me_prim->n_entries; i++) {
        src_imp = me_prim->entries[i].dist / wa->impedence;
        unordered_map<string, int> row_data;
        if ((wa->write_mode == WRITE_ONLY) || (wa->write_mode == WRITE_AND_LOAD)) {
            Ofile <<  me_prim->entries[i].id << ",";
        }
        for (int j = 0; j < wa->secondaryNN.me->n_entries; j++) {
            dst_imp = wa->secondaryNN.me->entries[j].dist * wa->impedence;
            calc_imp = dist[wa->secondaryNN.me->entries[j].pos];
            if (calc_imp == INT_MAX) {
                fin_imp = -1;
            } else if (me_prim->entries[i].pos == wa->secondaryNN.me->entries[j].pos) {
                fin_imp = 0;
            }
            else {
                fin_imp = dst_imp + calc_imp + src_imp;
            }
            if ((wa->write_mode == WRITE_ONLY) || (wa->write_mode == WRITE_AND_LOAD)) {
                Ofile << fin_imp;
            }
            if (j < wa->secondaryNN.me->n_entries - 1) {
                if ((wa->write_mode == WRITE_ONLY) || (wa->write_mode == WRITE_AND_LOAD)) {
                    Ofile << ",";
                }
            }
            row_data[wa->secondaryNN.me->entries[j].id] = fin_imp;

        }
        if ((wa->write_mode == LOAD_ONLY) || (wa->write_mode == WRITE_AND_LOAD)) {
            wa->insert_data.lock();
            wa->df->insertRow(row_data, me_prim->entries[i].id);
            wa->insert_data.unlock();
        }
        if ((wa->write_mode == WRITE_ONLY) || (wa->write_mode == WRITE_AND_LOAD)) {
            Ofile << endl;
        }
    }
    if ((wa->write_mode == WRITE_ONLY) || (wa->write_mode == WRITE_AND_LOAD)) {
        Ofile.close();
        wa->write_lock.unlock();
    }
}

/*findBest: get best n entries*/
void findBest(int* dist, nnMultiEntry* me_prim, workerArgs *wa) {
    limitedQueue lq(wa->mode);
    int src_imp, dst_imp, calc_imp, fin_imp;
    string src_id;
    string dst_id;
    for (int i = 0; i < me_prim->n_entries; i++) {
        src_imp = me_prim->entries[i].dist / wa->impedence;
        src_id = me_prim->entries[i].id;
        for (int j = 0; j < wa->secondaryNN.me->n_entries; j++) {
            dst_imp = wa->secondaryNN.me->entries[j].dist * wa->impedence;
            dst_id = wa->secondaryNN.me->entries[j].id;
            calc_imp = dist[wa->secondaryNN.me->entries[j].pos];
            if (calc_imp == INT_MAX) {
                continue;
            } else if (me_prim->entries[i].pos == wa->secondaryNN.me->entries[j].pos) {
                continue;
            }
            else {
                fin_imp = dst_imp + calc_imp + src_imp;
                lq.put(dst_id, fin_imp);
            }


        }
        //wa->insert_data.lock();
        //wa->data->emplace(me_prim->entries[i].id, lq.get());
        //wa->insert_data.unlock();
        wa->write_lock.lock();
        wa->json.insert(src_id, lq.get());
        wa->write_lock.unlock();
    }

}

/* The main function that calulates distances of shortest paths from src to all*/
/* vertices. It is a O(ELogV) function*/
void dijkstra(int src, workerArgs *wa) {

    nnMultiEntry* me_prim = wa->primaryNN.findMatchingEntries(src);
    if (!me_prim) {
        return;
    }


    int V = wa->graph->V;// Get the number of vertices in graph
    int *dist = new int [V];// dist values used to pick minimum weight edge in cut
 
    // minHeap represents set E
    struct MinHeap* minHeap = createMinHeap(V);
 
    // Initialize min heap with all vertices. dist value of all vertices 
    struct MinHeapNode newNode;
    for (int v = 0; v < V; ++v)
    {
        dist[v] = INT_MAX;
        newMinHeapNode(v, dist[v], &newNode);
        minHeap->array[v] = newNode;
        minHeap->pos[v] = v;
    }
 
    // Make dist value of src vertex as 0 so that it is extracted first
    struct MinHeapNode newSourceNode;
    newMinHeapNode(src, dist[src], &newSourceNode);
    minHeap->array[src] = newSourceNode;
    minHeap->pos[src] = src;
    dist[src] = 0;
    decreaseKey(minHeap, src, dist[src]);
 
    // Initially size of min heap is equal to V
    minHeap->size = V;
 
    // In the followin loop, min heap contains all nodes
    // whose shortest distance is not yet finalized.
    while (!isEmpty(minHeap))
    {
        // Extract the vertex with minimum distance value
        struct MinHeapNode minHeapNode;
        extractMin(minHeap, &minHeapNode);
        int u = minHeapNode.v; // Store the extracted vertex number
 
        // Traverse through all adjacent vertices of u (the extracted
        // vertex) and update their distance values
        struct AdjListNode* pCrawl = wa->graph->array[u].head;
        while (pCrawl != NULL)
        {
            int v = pCrawl->dest;
 
            // If shortest distance to v is not finalized yet, and distance to v
            // through u is less than its previously calculated distance
            if (isInMinHeap(minHeap, v) && dist[u] != INT_MAX && 
                                          pCrawl->weight + dist[u] < dist[v])
            {
                dist[v] = dist[u] + pCrawl->weight;
 
                // update distance value in min heap also
                decreaseKey(minHeap, v, dist[v]);
            }
            pCrawl = pCrawl->next;
        }
    }

    //write row to file or find best
    if (!wa->mode) {
        writeRow(dist, me_prim, wa);
    } else {
        findBest(dist, me_prim, wa);
    }

    //free allocated memory
    freeMinheap(minHeap);
    delete []dist;
    
}

vector<string> readIDs(string infile) {

    ifstream fileIN;

    int a, b;
    string id;

    fileIN.open(infile);
    if (fileIN.fail()) {
        throw runtime_error("Could not load input file");
    }

    string line;
    vector<string> data;
    while (getline(fileIN, line)) {
        istringstream stream(line);
        string input;
        getline(stream, input,',');
        a = (int) stoi(input);
        getline(stream, input,',');
        id = input;
        data.push_back(id);
        getline(stream, input,',');
        b = (int) stoi(input);
    }

    return data;
}


void workerHandler(workerArgs* wa) {
    int src;
    while (!wa->jq.empty()) {
        src = wa->jq.pop();
        //exit loop if job queue was empty
        if (src < 0) {
            break;
        }
        dijkstra(src, wa);
    }
}

class tMatrix {
public:
    dataFrame df;
    //unique_ptr<dataFrame> df_ptr; //causes setup.py to fail
    int write_mode;
    tMatrix(string infile, string nn_pinfile, string nn_sinfile, string outfile,
        int N, float impedence, int num_threads, int outer_node_rows, 
        int outer_node_cols, int mode, int write_mode);
    tMatrix(void);
    ~tMatrix(void);
    int get(string source, string dest);
    void loadFromDisk(void);
};


tMatrix::tMatrix(void) {

}

void tMatrix::loadFromDisk(void) {

}

tMatrix::tMatrix(string infile, string nn_pinfile, string nn_sinfile, string outfile,
        int N, float impedence, int num_threads, int outer_node_rows, int outer_node_cols, 
        int mode, int write_mode_in) {


    write_mode = write_mode_in;

    if (write_mode == READ_ONLY) {
        if (!df.loadFromDisk(infile)) {
            throw runtime_error("failed to load df from file");
        }

    } else {
        //initialize worker arguments
        vector<string> primary_ids = readIDs(nn_pinfile);

        vector<string> secondary_ids = readIDs(nn_sinfile);

        if ((write_mode == LOAD_ONLY) || (write_mode == WRITE_AND_LOAD)) {
            df.reserve(primary_ids, secondary_ids);
        }
        workerArgs wa(infile, outfile, impedence, mode, N, outer_node_cols, nn_pinfile, nn_sinfile, &df, write_mode);

        //initialize worker queue
        workerQueue wq(num_threads);

        //start queue
        wq.start(workerHandler, &wa);


    }

}

int tMatrix::get(string source, string dest) {
    if (write_mode != WRITE_ONLY) {
        return df.retrieveSafe(source, dest);
    } else {
        return 0;
    }
}

tMatrix::~tMatrix(void) {
    //free

}