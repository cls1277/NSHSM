#ifndef _GRAPH_H
#define _GRAPH_H

#include <iostream>
#include <vector>
#include <unordered_map>
#include <queue>
#include <algorithm>
#include "tools.h"

// 添加一条从 u 到 v 的边，长度为 w
void add_edge(std::unordered_map<int, std::vector<std::pair<int, int>>>& graph, int u, int v, int w) {
    graph[u].push_back(std::make_pair(v, w));
}

// 从 u 到 v 移除一条边
void remove_edge(std::unordered_map<int, std::vector<std::pair<int, int>>>& graph, int u, int v) {
    if (graph.find(u) != graph.end()) {
        graph[u].erase(std::remove_if(graph[u].begin(), graph[u].end(), [v](const std::pair<int, int>& p) {
            return p.first == v;
        }), graph[u].end());
    }
}

// 查找路径
std::vector<int> find_path(const std::vector<int> & pre, int u, int v) {
    std::vector<int> path;
    int current = v;
    while (current != -1) {
        path.push_back(current);
        current = pre[current];
    }
    std::reverse(path.begin(), path.end());
    return path;
}

// 获取距离
std::pair<int, std::vector<int>> get_distance(std::unordered_map<int, std::vector<std::pair<int, int>>>& graph, int s, int t, int JOBS, bool get_path = false) {
    int N = JOBS * 5 + 1;
    std::vector<int> ind(N+1, 0);
    std::queue<int> q;

    for (const auto& pair : graph) {
        for (const auto& edge : pair.second) {
            ind[edge.first]++;
        }
    }
    for (const auto& pair : graph) {
        if (ind[pair.first] == 0) {
            q.push(pair.first);
        }
    }

    std::vector<int> dp;
    std::vector<int> pre;
    for (int node = 0; node <= N; ++node) {
        dp.push_back(INT_MIN);
        pre.push_back(-1);
    }
    dp[s] = 0;

    while (!q.empty()) {
        int x = q.front();
        q.pop();
        for (const auto & edge : graph[x]) {
            int v = edge.first;
            int w = edge.second;
            ind[v]--;
            if (ind[v] == 0) {
                q.push(v);
            }
            if (dp[x] + w > dp[v]) {
                pre[v] = x;
                dp[v] = dp[x] + w;
            }
        }
    }
    std::vector<int> path;
    if(get_path) {
        path = find_path(pre, s, t);
    }
    return std::make_pair(dp[t], path);
}

// 初始化图
Graph init_graph(const Individual & ind, int factory, const Dset_info & dset_data, const std::vector<cand_info> & cand_data) {
    int MACHINES = dset_data.MACHINES;
    int JOBS = dset_data.JOBS;
    int N = JOBS * 5 + 1;
    Graph graph(N, MACHINES);
    for (int job = 0; job < JOBS; ++job) {
        if (ind.factories[job] != factory) {
            continue;
        }
        int first_node = get_node(job, 0);
        int machine = ind.machines[first_node-1];
        int first_time = get_time(first_node, factory, machine, cand_data);
        add_edge(graph.graph, 0, first_node, first_time);
        int last_node = get_node(job, 4);
        add_edge(graph.graph, last_node, N, 0);
        for (int operation = 0; operation < 5; ++operation) {
            int node = get_node(job, operation);
            int machine = ind.machines[node-1];
            int time = get_time(node, factory, machine, cand_data);
            if (operation == 0) {
                graph.PJ[node] = 0;
                graph.SJ[node] = node + 1;
            } else if (operation == 4) {
                graph.PJ[node] = node - 1;
                graph.SJ[node] = N;
                add_edge(graph.graph, node-1, node, time);
            } else {
                graph.PJ[node] = node - 1;
                graph.SJ[node] = node + 1;
                add_edge(graph.graph, node-1, node, time);
            }
        }
    }

    std::vector<int> endtime_job(JOBS, 0);
    std::vector<int> endtime_machine(MACHINES, 0);
    std::vector<int> last_node_machine(MACHINES, -1);
    std::vector<int> operation(JOBS, -1);
    for (int index = 0; index < ind.schedules.size(); index++) {
        int job = ind.schedules[index];
        if (ind.factories[job] != factory) {
            continue;
        }
        operation[job]++;
        int node = get_node(job, operation[job]);
        int machine = ind.machines[node-1];
        graph.all_operations_of_machine[machine].push_back(index);
        int time = get_time(node, factory, machine, cand_data);
        graph.PM[node] = last_node_machine[machine];
        if(last_node_machine[machine] != -1) {
            graph.SM[last_node_machine[machine]] = node;
        }
        last_node_machine[machine] = node;
        int start_time = std::max(endtime_job[job], endtime_machine[machine]);
        endtime_machine[machine] = endtime_job[job] = start_time + time;

        graph.start_time_nodes[node] = start_time;
        graph.end_time_nodes[node] = endtime_job[job];
    }

    for(int node=0; node<N; node++) {
        if(graph.PM[node] == -1) continue;
        int machine = ind.machines[node-1];
        int time = get_time(node, factory, machine, cand_data);
        add_edge(graph.graph, graph.PM[node], node, time);
    }

    // 添加N，结束点到图中，解决一些问题
    graph.graph[N] = {};
    return graph;
}

#endif
