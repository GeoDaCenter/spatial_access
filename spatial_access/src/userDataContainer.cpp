#include <vector>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <iostream>

#include "userDataContainer.h"

userDataPoint::userDataPoint(int networkNodeId, unsigned int loc, int lastMileDistance)
{
    this->networkNodeId = networkNodeId;
    this->loc = loc;
    this->lastMileDistance = lastMileDistance;
}

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

const std::vector<unsigned int>& userDataContainer::retrieveAllUserDataIds() const
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

void userDataContainer::addPoint(int networkNodeId, unsigned int loc, int lastMileDistance)
{
    ids.push_back(loc);
    allNetworkNodeIds.push_back(networkNodeId);
    userDataPoint newDataPoint(networkNodeId, loc, lastMileDistance);
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