// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#pragma once

#include <unordered_map>

class userDataPoint
{
public:
    unsigned long int networkNodeId;
    unsigned long int loc;
    unsigned short int lastMileDistance;
    userDataPoint(unsigned long int networkNodeId, unsigned long int loc, unsigned short int lastMileDistance);
};

class userDataTract
{
public:
    int networkNodeId;
    std::vector<userDataPoint> data;
    userDataTract(unsigned long int networkNodeId);
    void addPoint(userDataPoint userData);
    const std::vector<userDataPoint>& retrieveDataPoints() const;
};


class userDataContainer
{
private:
    std::unordered_map<unsigned long int, userDataTract> data;
    std::vector<unsigned long int> allNetworkNodeIds;
    std::vector<unsigned long int> ids;
    std::vector<unsigned long int> uniqueNetworkNodeIds;
public:
    userDataContainer()= default;
    void addPoint(unsigned long int networkNodeId, unsigned long int loc, unsigned short int lastMileDistance);
    bool containsTract(unsigned long int networkNodeId) const;
    const userDataTract& retrieveTract(unsigned long int networkNodeId) const;
    const std::vector<unsigned long int>& retrieveAllUserDataIds() const;
    const std::vector<unsigned long int>& retrieveAllNetworkNodeIds() const;
    const std::vector<unsigned long int>& retrieveUniqueNetworkNodeIds() const;
};
