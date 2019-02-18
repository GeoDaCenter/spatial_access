// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#include <vector>
#include <string>
#include <unordered_map>
#include <unordered_set>
#include <iostream>

#include "userDataContainer.h"

userDataPoint::userDataPoint(unsigned long int networkNodeId, unsigned long int loc, unsigned short int lastMileDistance)
{
    this->networkNodeId = networkNodeId;
    this->loc = loc;
    this->lastMileDistance = lastMileDistance;
}

const std::vector<userDataPoint>& userDataTract::retrieveDataPoints() const
{
    return data;
}


userDataTract::userDataTract(unsigned long int networkNodeId)
{
    this->networkNodeId = networkNodeId;
}

void userDataTract::addPoint(userDataPoint userData)
{
    data.push_back(userData);
}

const std::vector<unsigned long int>& userDataContainer::retrieveAllUserDataIds() const
{
    return this->ids;
}


bool userDataContainer::containsTract(unsigned long int networkNodeId) const
{
    return data.find(networkNodeId) != data.end();
}

void userDataContainer::addPoint(unsigned long int networkNodeId, unsigned long int loc, unsigned short int lastMileDistance)
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

const userDataTract& userDataContainer::retrieveTract(unsigned long int networkNodeId) const
{
    return data.at(networkNodeId);
}

const std::vector<unsigned long int>& userDataContainer::retrieveAllNetworkNodeIds() const
{
    return allNetworkNodeIds;
}


const std::vector<unsigned long int>& userDataContainer::retrieveUniqueNetworkNodeIds() const
{
    return uniqueNetworkNodeIds;
}