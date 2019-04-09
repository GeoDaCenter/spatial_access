// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#pragma once

#include <vector>
#include <tuple>
#include <stack>
#include <unordered_set>
#include <unordered_map>

typedef unsigned long int node_id;
typedef std::pair<node_id, node_id> edge_id;
typedef std::vector<edge_id> edge_array;
typedef std::vector<node_id> node_array;


class NetworkUtility {
    private:
        const edge_array edges;
        const node_array nodes;
        node_array main_connected_component;
        edge_array edges_of_main_connected_component;
    public:
        NetworkUtility(edge_array &edges, node_array &nodes);
        NetworkUtility()= default;

        edge_array getConnectedNetworkEdges();

        std::vector<unsigned long int> getConnectedNetworkNodes();

    private:
        std::stack<node_id> getTraversalOrder();

        const std::unordered_map<node_id, node_array> getGraph() const;

        const std::unordered_map<node_id, node_array> getTransposeGraph() const;

        const edge_array getEdgesOfMainConnectedComponent() const;

    };
