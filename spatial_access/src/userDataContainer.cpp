#include <vector>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <iostream>

#include "userDataContainer.h"

userDataPoint::userDataPoint(unsigned int networkNodeId, unsigned int loc, unsigned short int lastMileDistance)
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
        std::cout << "(" << dataPoint.loc << "," << dataPoint.lastMileDistance << ")" << std::endl;
    }
}

userDataTract::userDataTract(unsigned int networkNodeId)
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
    for (const auto entry : data)
    {
        entry.second.print();
    }
}

userDataContainer::userDataContainer()
{
    this->isSymmetric = false;
}

bool userDataContainer::containsTract(unsigned int networkNodeId) const
{
    return data.find(networkNodeId) != data.end();
}

void userDataContainer::addPoint(unsigned int networkNodeId, unsigned int loc, unsigned short int lastMileDistance)
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

const userDataTract& userDataContainer::retrieveTract(unsigned int networkNodeId) const
{
    return data.at(networkNodeId);
}

const std::vector<unsigned int>& userDataContainer::retrieveAllNetworkNodeIds() const
{
    return allNetworkNodeIds;
}


const std::vector<unsigned int>& userDataContainer::retrieveUniqueNetworkNodeIds() const
{
    return uniqueNetworkNodeIds;
}