#pragma once

class MinHeapNode
{
public:
    int v;
    unsigned short int dist;
    MinHeapNode(int v, unsigned short int dist);
    MinHeapNode();
};

class MinHeap
{
public:
    int size;
    int capacity;
    int *pos;
    MinHeapNode *array;
    MinHeap(int capacity);
    ~MinHeap();
    void minHeapify(int idx);
    bool isEmpty();
    MinHeapNode extractMin();
    void decreaseKey(int v, unsigned short int dist);
    bool isInMinHeap(int v);
};


/* A utility function to swap two nodes of min heap. Needed for min heapify*/
void swapMinHeapNode(MinHeapNode* a, MinHeapNode* b);

 

