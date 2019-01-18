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
    void print() const;
    const std::vector<userDataPoint>& retrieveDataPoints() const;
};

const std::vector<userDataPoint>& userDataTract::retrieveDataPoints() const
{
    return data;
}

void userDataTract::print() const
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
    bool isSymmetric;
    std::unordered_map<int, userDataTract> data;
    std::vector<int> allNetworkNodeIds;
    std::vector<unsigned long int> ids;
    std::vector<int> uniqueNetworkNodeIds;
    userDataContainer();
    void addPoint(int networkNodeId, unsigned long int id, int lastMileDistance);
    bool containsTract(int networkNodeId) const;
    const userDataTract& retrieveTract(int networkNodeId) const;
    const std::vector<unsigned long int>& retrieveAllUserDataIds() const;
    const std::vector<int>& retrieveAllNetworkNodeIds() const;
    const std::vector<int>& retrieveUniqueNetworkNodeIds() const;
    void print() const;
};

const std::vector<unsigned long int>& userDataContainer::retrieveAllUserDataIds() const
{
    return this->ids;
}


void userDataContainer::print() const
{
    for (auto entry : data)
    {
        entry.second.print();
    }
}

userDataContainer::userDataContainer()
{
    this->isSymmetric = false;
}

bool userDataContainer::containsTract(int networkNodeId) const
{
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

const userDataTract& userDataContainer::retrieveTract(int networkNodeId) const
{
    return data.at(networkNodeId);
}

const std::vector<int>& userDataContainer::retrieveAllNetworkNodeIds() const
{
    return allNetworkNodeIds;
}


const std::vector<int>& userDataContainer::retrieveUniqueNetworkNodeIds() const
{
    return uniqueNetworkNodeIds;
}