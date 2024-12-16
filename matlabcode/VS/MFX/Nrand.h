#ifndef _NRAND_H
#define _NRAND_H

#include <algorithm>
#include <vector>
#include "tools.h"
#include "Graph.h"

void swap_all(Individual & ind, int FACTORIES, int JOBS) {
    int key = std::rand()%FACTORIES;
    std::vector<int> indices;
    for(int i=0; i<JOBS; i++) {
        if(ind.factories[i] == key) {
            indices.push_back(i);
        }
    }
    if(indices.size() < 2) return ;
    int job1, job2;
    do {
        job1 = indices[rand()%(indices.size())];
        job2 = indices[rand()%(indices.size())];
    }while(job1==job2);
    int op1 = rand() % 5, op2 = rand() % 5;
    int node1 = get_node(job1, op1), node2 = get_node(job2, op2);
    int index1 = get_node_to_index(ind.schedules, node1, JOBS);
    int index2 = get_node_to_index(ind.schedules, node2, JOBS);
    std::swap(ind.schedules[index1], ind.schedules[index2]);
}

void swap_key(Individual & ind, int JOBS) {
    int key = std::get<2>(ind.objectives);
    std::vector<int> indices;
    for(int i=0; i<JOBS; i++) {
        if(ind.factories[i] == key) {
            indices.push_back(i);
        }
    }
    if(indices.size() < 2) return ;
    int job1, job2;
    do {
        job1 = indices[rand()%(indices.size())];
        job2 = indices[rand()%(indices.size())];
    }while(job1==job2);
    int op1 = rand() % 5, op2 = rand() % 5;
    int node1 = get_node(job1, op1), node2 = get_node(job2, op2);
    int index1 = get_node_to_index(ind.schedules, node1, JOBS);
    int index2 = get_node_to_index(ind.schedules, node2, JOBS);
    std::swap(ind.schedules[index1], ind.schedules[index2]);
}

void insert_all(Individual & ind, int FACTORIES, int JOBS) {
    int key = std::rand()%FACTORIES;
    std::vector<int> indices;
    for(int i=0; i<JOBS; i++) {
        if(ind.factories[i] == key) {
            indices.push_back(i);
        }
    }
    if(indices.size() < 2) return ;
    int job1 = indices[rand()%(indices.size())];
    int job2 = indices[rand()%(indices.size())];
    int op1, op2;
    if(job1 == job2) {
        op1 = rand() % 5;
        do {
            op2 = rand() % 5;
        }while(op1 == op2);
    } else {
        op1 = rand() % 5;
        op2 = rand() % 5;
    }
    int node1 = get_node(job1, op1), node2 = get_node(job2, op2);
    int index1 = get_node_to_index(ind.schedules, node1, JOBS);
    int index2 = get_node_to_index(ind.schedules, node2, JOBS);
    if(index1 > index2) std::swap(index1, index2);
    int temp = ind.schedules[index2];
    for(int i=index2; i>index1; i--) {
        ind.schedules[i] = ind.schedules[i-1];
    }
    ind.schedules[index1] = temp;
}

void insert_key(Individual & ind, int JOBS) {
    int key = std::get<2>(ind.objectives);
    std::vector<int> indices;
    for(int i=0; i<JOBS; i++) {
        if(ind.factories[i] == key) {
            indices.push_back(i);
        }
    }
    if(indices.size() < 2) return ;
    int job1 = indices[rand()%(indices.size())];
    int job2 = indices[rand()%(indices.size())];
    int op1, op2;
    if(job1 == job2) {
        op1 = rand() % 5;
        do {
            op2 = rand() % 5;
        }while(op1 == op2);
    } else {
        op1 = rand() % 5;
        op2 = rand() % 5;
    }
    int node1 = get_node(job1, op1), node2 = get_node(job2, op2);
    int index1 = get_node_to_index(ind.schedules, node1, JOBS);
    int index2 = get_node_to_index(ind.schedules, node2, JOBS);
    if(index1 > index2) std::swap(index1, index2);
    int temp = ind.schedules[index2];
    for(int i=index2; i>index1; i--) {
        ind.schedules[i] = ind.schedules[i-1];
    }
    ind.schedules[index1] = temp;
}

void machine_all(Individual & ind, const Dset_info & dset_data, const std::vector<cand_info> & cand_data) {
	int key = std::get<2>(ind.objectives);
    int N = dset_data.JOBS * 5 + 1;
    std::unordered_map<int, std::vector<std::pair<int, int>>> graph = init_graph(ind, key, dset_data, cand_data).graph;
    std::pair<int, std::vector<int>> cp = get_distance(graph, 0, N, dset_data.JOBS, true);
    int node = cp.second[rand() % (cp.second.size() - 2) + 1];
    int new_machine = cand_data[node].machines[rand() % cand_data[node].machines.size()];
    ind.machines[node-1] = new_machine;
}

void machine_roule(Individual & ind, const Dset_info & dset_data, const std::vector<cand_info> & cand_data) {
    int key = std::get<2>(ind.objectives);
    int N = dset_data.JOBS * 5 + 1;
    std::unordered_map<int, std::vector<std::pair<int, int>>> graph = init_graph(ind, key, dset_data, cand_data).graph;
    std::pair<int, std::vector<int>> cp = get_distance(graph, 0, N, dset_data.JOBS, true);
	int node = cp.second[rand() % (cp.second.size() - 2) + 1];
    
    std::vector<int> sum_time;
    for(auto it : cand_data[node].times[key]) {
        if(!sum_time.size()) {
            sum_time.push_back(it);
        } else {
            sum_time.push_back(sum_time[sum_time.size()-1] + it);
        }
    }
    int new_machine_index = std::upper_bound(sum_time.begin(), sum_time.end(), rand() % sum_time[sum_time.size()-1])-sum_time.begin();
    int new_machine = cand_data[node].machines[new_machine_index];
    ind.machines[node-1] = new_machine;
}

void factory_mu(Individual & ind, int JOBS, int FACTORIES) {
    int job = rand() % JOBS;
    int new_factory = -1;
    do {
        new_factory = rand() % FACTORIES;
    }while(new_factory == ind.factories[job]);
    ind.factories[job] = new_factory;
}

#endif
