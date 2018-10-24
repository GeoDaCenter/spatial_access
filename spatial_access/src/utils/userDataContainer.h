#pragma once

#include <vector>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <iostream>


/* This class encapsulates a single point of the user's data
 * and its relation to the graph.
 */
class userDataPoint
{
public:
    int networkNodeId;
    unsigned long int id;
    int lastMileDistance;
    userDataPoint(int networkNodeId, unsigned long int id, int lastMileDistance);
};


/* Constructor */
userDataPoint::userDataPoint(int networkNodeId, unsigned long int id, int lastMileDistance)
{
    this->networkNodeId = networkNodeId;
    this->id = id;
    this->lastMileDistance = lastMileDistance;
}


/* This class encapsulates all of the userDataPoints that have
 * a given networkNodeId as the closest entry point to the graph.
 */
class userDataTract
{
public:
    int networkNodeId;
    std::vector<userDataPoint> data;
    userDataTract(int networkNodeId);
    void addPoint(userDataPoint userData);
    void print();
    const std::vector<userDataPoint>& retrieveDataPoints();
};


/* Return all the user data points associated with a single tract */
const std::vector<userDataPoint>& userDataTract::retrieveDataPoints()
{
    return data;
}


/* Print the tract */
void userDataTract::print()
{
    std::cout << networkNodeId << std::endl;
    for (auto dataPoint : data)
    {
        std::cout << "(" << dataPoint.id << "," << dataPoint.lastMileDistance << ")" << std::endl;
    }
}


/* Constructor */
userDataTract::userDataTract(int networkNodeId)
{
    this->networkNodeId = networkNodeId;
}


/* Add a user data point to this node of the network graph */
void userDataTract::addPoint(userDataPoint userData)
{
    data.push_back(userData);
}


/* This class encapsulates all of the source and/or destination points
 * that a user provides
 */
class userDataContainer
{
public:
    std::unordered_map<int, userDataTract> data;
    std::vector<int> allNetworkNodeIds;
    std::vector<unsigned long int> ids;
    std::vector<int> uniqueNetworkNodeIds;
    userDataContainer();
    void addPoint(int networkNodeId, unsigned long int id, int lastMileDistance);
    bool containsTract(int networkNodeId);
    const userDataTract& retrieveTract(int networkNodeId);
    const std::vector<unsigned long int>& retrieveAllUserDataIds();
    const std::vector<int>& retrieveAllNetworkNodeIds();
    const std::vector<int>& retrieveUniqueNetworkNodeIds();
    void print();
};


/* Return all of the ids to the user data */
const std::vector<unsigned long int>& userDataContainer::retrieveAllUserDataIds()
{
    return this->ids;
}


/* Print the user's data points */
void userDataContainer::print()
{
    for (auto entry : data)
    {
        entry.second.print();
    }
}


/* Void Constructor (unused) */
userDataContainer::userDataContainer()
{

}


/* Determine if the tract is already contained in the instance */
bool userDataContainer::containsTract(int networkNodeId)
{
    return data.find(networkNodeId) != data.end();
}


/* Add a single user data point */
void userDataContainer::addPoint(int networkNodeId, unsigned long int id, int lastMileDistance)
{
    ids.push_back(id);
    allNetworkNodeIds.push_back(networkNodeId);
    userDataPoint newDataPoint(networkNodeId, id, lastMileDistance);
    if (containsTract(networkNodeId))
    {
        data.at(networkNodeId).addPoint(newDataPoint);
    }
    else
    {
        userDataTract newUserDataTract(networkNodeId);
        newUserDataTract.addPoint(newDataPoint);
        data.insert(std::make_pair(networkNodeId, newUserDataTract));
        uniqueNetworkNodeIds.push_back(networkNodeId);
    }


}


/* Retrieve a tract by id */
const userDataTract& userDataContainer::retrieveTract(int networkNodeId)
{
    return data.at(networkNodeId);
}


/* Retrieve a vector of all network node ids */
const std::vector<int>& userDataContainer::retrieveAllNetworkNodeIds()
{
    return allNetworkNodeIds;
}


/* Retrieve a vector of only unique network node ids */
const std::vector<int>& userDataContainer::retrieveUniqueNetworkNodeIds()
{
    return uniqueNetworkNodeIds;
}