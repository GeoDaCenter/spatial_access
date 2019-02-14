#pragma once

#include <unordered_map>

class userDataPoint
{
public:
    int networkNodeId;
    unsigned int loc;
    unsigned short int lastMileDistance;
    userDataPoint(unsigned int networkNodeId, unsigned int loc, unsigned short int lastMileDistance);
};

class userDataTract
{
public:
    int networkNodeId;
    std::vector<userDataPoint> data;
    userDataTract(unsigned int networkNodeId);
    void addPoint(userDataPoint userData);
    const std::vector<userDataPoint>& retrieveDataPoints() const;
};


class userDataContainer
{
private:
    std::unordered_map<unsigned int, userDataTract> data;
    std::vector<unsigned int> allNetworkNodeIds;
    std::vector<unsigned int> ids;
    std::vector<unsigned int> uniqueNetworkNodeIds;
public:
    userDataContainer()= default;
    void addPoint(unsigned int networkNodeId, unsigned int loc, unsigned short int lastMileDistance);
    bool containsTract(unsigned int networkNodeId) const;
    const userDataTract& retrieveTract(unsigned int networkNodeId) const;
    const std::vector<unsigned int>& retrieveAllUserDataIds() const;
    const std::vector<unsigned int>& retrieveAllNetworkNodeIds() const;
    const std::vector<unsigned int>& retrieveUniqueNetworkNodeIds() const;
};
