#pragma once

#include <stdexcept>

class MinHeapNode
{
public:
    int v;
    int dist;
    MinHeapNode(int v, int dist);
    MinHeapNode();
};

MinHeapNode::MinHeapNode(int v, int dist)
{
    this->v = v;
    this->dist = dist;
}

MinHeapNode::MinHeapNode()
{
    
}

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
    void decreaseKey(int v, int dist);
    bool isInMinHeap(int v);
};

/* A utility function to create a Min Heap*/
MinHeap::MinHeap(int capacity)
{
    this->pos = new int[capacity];
    this->size = 0;
    this->capacity = capacity;
    this->array = new MinHeapNode[capacity];
}


/* free a minHeap struct*/
MinHeap::~MinHeap() {
    // delete [] this->array;
    // delete this->pos;
}


/* A utility function to swap two nodes of min heap. Needed for min heapify*/
void swapMinHeapNode(MinHeapNode* a, MinHeapNode* b)
{
    auto tempV = a->v;
    auto tempDist = a->dist;

    a->v = b->v;
    a->dist = b->dist;

    b->v = tempV;
    b->dist = tempDist;

}
 

/* A standard function to heapify at given idx */
/* This function also updates position of nodes when they are swapped.*/
/* Position is needed for decreaseKey()*/
void MinHeap::minHeapify(int idx)
{
    int smallest, left, right;
    smallest = idx;
    left = 2 * idx + 1;
    right = 2 * idx + 2;
 
    if (left < this->size &&
        this->array[left].dist < this->array[smallest].dist )
      smallest = left;
 
    if (right < this->size &&
        this->array[right].dist < this->array[smallest].dist )
      smallest = right;
 
    if (smallest != idx)
    {
        // The nodes to be swapped in min heap
        MinHeapNode smallestNode = this->array[smallest];
        MinHeapNode idxNode = this->array[idx];
 
        // Swap positions
        this->pos[smallestNode.v] = idx;
        this->pos[idxNode.v] = smallest;
 
        // Swap nodes
        swapMinHeapNode(&this->array[smallest], &this->array[idx]);
        minHeapify(smallest);
    }
}
 

/* A utility function to check if the given minHeap is ampty or not*/
bool MinHeap::isEmpty()
{
    return this->size == 0;
}

 
/* Standard function to extract minimum node from heap*/
MinHeapNode MinHeap::extractMin()
{
    if (isEmpty())
    {
        throw std::runtime_error("minheap is empty");
    }
 
    // Store the root node
    MinHeapNode root = this->array[0];
 
    // Replace root node with last node
    MinHeapNode lastNode = this->array[this->size - 1];
    this->array[0] = lastNode;
 
    // Update position of last node
    this->pos[root.v] = this->size-1;
    this->pos[lastNode.v] = 0;
 
    // Reduce heap size and heapify root
    --this->size;
    minHeapify(0);
 
    return root;
}

 
/* Function to decreasy dist value of a given vertex v. This function*/
/* uses pos[] of min heap to get the current index of node in min heap*/
void MinHeap::decreaseKey(int v, int dist)
{
    // Get the index of v in  heap array
    int i = this->pos[v];
 
    // Get the node and update its dist value
    this->array[i].dist = dist;
 
    // Travel up while the complete tree is not heapified.
    // This is a O(Logn) loop
    while (i && this->array[i].dist < this->array[(i - 1) / 2].dist)
    {
        // Swap this node with its parent
        this->pos[this->array[i].v] = (i-1)/2;
        this->pos[this->array[(i-1)/2].v] = i;
        swapMinHeapNode(&this->array[i],  &this->array[(i - 1) / 2]);
 
        // move to parent index
        i = (i - 1) / 2;
    }
}

 
/* A utility function to check if a given vertex*/
/* 'v' is in min heap or not*/
bool MinHeap::isInMinHeap(int v)
{
   return (this->pos[v] < this->size);
}