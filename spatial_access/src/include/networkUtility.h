// Logan Noel (github.com/lmnoel)
//
// ©2017-2019, Center for Spatial Data Science

#pragma once

#include <vector>
#include <tuple>
#include <stack>
#include <unordered_set>
#include <unordered_map>
#include <algorithm>

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

    NetworkUtility(edge_array &edges, node_array &nodes)
            : edges(edges), nodes(nodes) {
        auto traversal_order = getTraversalOrder();
        auto transpose_graph = getTransposeGraph();
        std::unordered_set<node_id> is_visited;
        std::vector<std::vector<node_id>> connected_components;
        while (!traversal_order.empty()) {
            node_id v = traversal_order.top();
            traversal_order.pop();
            if (is_visited.find(v) == is_visited.end()) {
                continue;
            }
            std::vector<node_id> new_connected_component;
            connected_components.push_back(new_connected_component);
            std::stack<node_id> secondary_stack;
            secondary_stack.push(v);
            while (!secondary_stack.empty()) {
                node_id u = secondary_stack.top();
                secondary_stack.pop();
                connected_components.at(connected_components.size()).push_back(u);
                for (node_id t : transpose_graph.at(u)) {
                    if (is_visited.find(t) != is_visited.end()) {
                        secondary_stack.push(t);
                    }
                }

            }
        }
        if (connected_components.empty()) {
            throw std::runtime_error("Found no connected components");
        }
        std::sort(connected_components.begin(), connected_components.end(),
                  [](const node_array &a, const node_array &b) { return a.size() > b.size(); });
        this->main_connected_component = connected_components.at(0);
        this->edges_of_main_connected_component = getEdgesOfMainConnectedComponent();
    }

    edge_array
    getConnectedNetworkEdges()  {
        return edges_of_main_connected_component;
    }

    node_array
    getConnectedNetworkNodes()  {
        return main_connected_component;
    }

private:

    const std::unordered_map<node_id, node_array>
    getGraph() const {
        std::unordered_map<node_id, node_array> graph;
        for (auto node : nodes) {
            node_array values;
            graph.emplace(node, values);
        }
        for (auto edge : edges) {
            node_id from_edge = std::get<0>(edge);
            node_id to_edge = std::get<1>(edge);
            graph.at(from_edge).push_back(to_edge);
        }
        return graph;
    }

    const std::unordered_map<node_id, node_array>
    getTransposeGraph() const {
        std::unordered_map<node_id, node_array> graph;
        for (auto node : nodes) {
            node_array values;
            graph.emplace(node, values);
        }
        for (auto edge : edges) {
            node_id from_edge = std::get<1>(edge);
            node_id to_edge = std::get<0>(edge);
            graph.at(from_edge).push_back(to_edge);
        }
        return graph;
    }

    std::stack<node_id>
    getTraversalOrder() {
        std::stack<std::pair<node_id, bool>> temp_stack;
        std::stack<node_id> return_stack;
        node_array nodes_copy(this->nodes);
        std::unordered_set<node_id> visited;
        auto num_nodes = this->nodes.size();

        while (return_stack.size() < num_nodes) {
            auto v = nodes_copy.back();
            nodes_copy.pop_back();
            if (visited.find(v) != visited.end()) {
                continue;
            }
            temp_stack.push(std::make_pair(v, false));
            auto graph = this->getGraph();
            while (!temp_stack.empty()) {
                auto res = temp_stack.top();
                temp_stack.pop();
                node_id u = std::get<0>(res);
                bool flag = std::get<1>(res);
                if (flag) {
                    return_stack.push(u);
                } else if (visited.find(u) != visited.end()) {
                    visited.insert(u);
                    temp_stack.push(std::make_pair(u, true));
                    for (auto t : graph.at(u)) {
                        temp_stack.push(std::make_pair(t, false));
                    }
                }
            }
        }
        return return_stack;
    }

    const edge_array
    getEdgesOfMainConnectedComponent() const {
        std::unordered_set<node_id> nodes_in_main_component(main_connected_component.begin(),
                                                            main_connected_component.end());
        edge_array return_edges;
        for (edge_id edge : edges) {
            node_id from_edge = std::get<0>(edge);
            node_id to_edge = std::get<1>(edge);
            if (nodes_in_main_component.find(from_edge) == nodes_in_main_component.end()) {
                continue;
            }
            if (nodes_in_main_component.find(to_edge) == nodes_in_main_component.end()) {
                continue;
            }
            return_edges.push_back(edge);
        }
        return return_edges;
    }



    };
