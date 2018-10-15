#pragma once

#include <vector>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <iostream>

class userDataPoint
{
public:
    int networkNodeId;
    unsigned long int id;
    int lastMileDistance;
    userDataPoint(int networkNodeId, unsigned long int id, int lastMileDistance);
};

userDataPoint::userDataPoint(int networkNodeId, unsigned long int id, int lastMileDistance)
{
    this->networkNodeId = networkNodeId;
    this->id = id;
    this->lastMileDistance = lastMileDistance;
}


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

const std::vector<userDataPoint>& userDataTract::retrieveDataPoints()
{
    return data;
}

void userDataTract::print()
{
    std::cout << networkNodeId << std::endl;
    for (auto dataPoint : data)
    {
        std::cout << "(" << dataPoint.id << "," << dataPoint.lastMileDistance << ")" << std::endl;
    }
}

userDataTract::userDataTract(int networkNodeId)
{
    this->networkNodeId = networkNodeId;
}

void userDataTract::addPoint(userDataPoint userData)
{
    data.push_back(userData);
}



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

const std::vector<unsigned long int>& userDataContainer::retrieveAllUserDataIds()
{
    return this->ids;
}


void userDataContainer::print()
{
    for (auto entry : data)
    {
        entry.second.print();
    }
}

userDataContainer::userDataContainer()
{

}
bool userDataContainer::containsTract(int networkNodeId)
{
    // improve search time using set
    return data.find(networkNodeId) != data.end();
}
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

const userDataTract& userDataContainer::retrieveTract(int networkNodeId)
{
    return data.at(networkNodeId);
}

const std::vector<int>& userDataContainer::retrieveAllNetworkNodeIds()
{
    return allNetworkNodeIds;
}


const std::vector<int>& userDataContainer::retrieveUniqueNetworkNodeIds()
{
    return uniqueNetworkNodeIds;
}