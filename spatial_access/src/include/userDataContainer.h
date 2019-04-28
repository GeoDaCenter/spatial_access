// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#pragma once

#include <vector>
#include <string>
#include <unordered_map>
#include <unordered_set>

template <class value_type>
class userDataPoint
{
public:
    unsigned long int networkNodeId;
    unsigned long int loc;
    value_type lastMileDistance;
    userDataPoint(unsigned long int networkNodeId, unsigned long int loc, unsigned short int lastMileDistance)
    : networkNodeId(networkNodeId), loc(loc), lastMileDistance(lastMileDistance) {}
};

template <class value_type>
class userDataTract
{
public:
    unsigned long int networkNodeId;
    std::vector<userDataPoint<value_type>> data;
    userDataTract(unsigned long int networkNodeId) : networkNodeId(networkNodeId) {}
    void addPoint(userDataPoint<value_type> userData)
    {
        data.push_back(userData);
    }
    const std::vector<userDataPoint<value_type>>& retrieveDataPoints() const
    {
        return data;
    }
};


template <class value_type>
class userDataContainer
{
private:
    std::unordered_map<unsigned long int, userDataTract<value_type>> data;
    std::vector<unsigned long int> allNetworkNodeIds;
    std::vector<unsigned long int> ids;
    std::vector<unsigned long int> uniqueNetworkNodeIds;
public:
    userDataContainer()= default;

    void addPoint(unsigned long int networkNodeId, unsigned long int loc, value_type lastMileDistance)
    {
        ids.push_back(loc);
        allNetworkNodeIds.push_back(networkNodeId);
        userDataPoint<value_type> newDataPoint(networkNodeId, loc, lastMileDistance);
        if (containsTract(networkNodeId))
        {
            data.at(networkNodeId).addPoint(newDataPoint);
        }
        else
        {
            userDataTract<value_type> newUserDataTract(networkNodeId);
            newUserDataTract.addPoint(newDataPoint);
            data.insert(std::make_pair(networkNodeId, newUserDataTract));
            uniqueNetworkNodeIds.push_back(networkNodeId);
        }


    }
    bool containsTract(unsigned long int networkNodeId) const
    {
        return data.find(networkNodeId) != data.end();
    }
    const userDataTract<value_type>& retrieveTract(unsigned long int networkNodeId) const
    {
        return data.at(networkNodeId);
    }

    const std::vector<unsigned long int>& retrieveUniqueNetworkNodeIds() const
    {
        return uniqueNetworkNodeIds;
    }
};
