#ifndef _TOOLS_H
#define _TOOLS_H

#include <algorithm>
#include <tuple>
#include <vector>
#include <unordered_map>

struct Dset_info {
    int FACTORIES, MACHINES, JOBS;
};

struct Individual {
    std::vector<int> factories;
    std::vector<int> machines;
    std::vector<int> schedules;
    std::tuple<int, int, int> objectives; // <2>是关键工厂
};

bool operator < (const Individual & x, const Individual & y) {
    return x.objectives < y.objectives;
}

struct cand_info {
    std::vector<int> machines;
    std::vector<std::vector<int>> times;
};

struct Pop {
    int obj, machine, idx, v;
    std::string direction;
};

struct Graph {
    std::vector<int> PM, PJ, SM, SJ;
    std::vector<int> start_time_nodes, end_time_nodes;
    std::unordered_map<int, std::vector<std::pair<int, int>>> graph;
    std::vector<std::vector<int>> all_operations_of_machine;
    // std::unordered_map<int, std::vector<int>> all_operations_of_machine;
    Graph() {}
    Graph(int N, int MACHINES) : all_operations_of_machine(MACHINES, std::vector<int>()), PM(N+1, -1), PJ(N+1, -1), SM(N+1, -1), SJ(N+1, -1), start_time_nodes(N+1, 0), end_time_nodes(N+1, 0) {}
};

struct PSJM {
    std::vector<int> PM_index, PJ_index, SM_index, SJ_index;
    std::vector<int> nodes_to_indexes, indexes_to_nodes;
    PSJM() {};
    PSJM(int sum_operations) : PM_index(sum_operations, 0), PJ_index(sum_operations, 0), SM_index(sum_operations, 0), SJ_index(sum_operations, 0) {};
};

struct Ret_Pop {
    std::vector<Pop> mksp, tec;
    PSJM psjm;
    Ret_Pop() {};
    Ret_Pop(int sum_operations) : psjm(sum_operations) {};
};

struct Min_Objs {
    int obj, idx;
    std::vector<Pop> pop;
};

bool operator < (const Min_Objs & x, const Min_Objs & y) {
    return x.obj < y.obj;
}

// ------

std::pair<int, int> get_job_operation(int node) {
//    int operation = node % 5 - 1;
	int operation = (node % 5 + 4) % 5; 
    int job = (node - operation - 1) / 5;
    return std::make_pair(job, operation);
}

int get_time(int node, int factory, int machine, const std::vector<cand_info> & cand_data) {
    int time = -1;
    for ( int m_index=0; m_index<cand_data[node].machines.size(); m_index++) {
        if(cand_data[node].machines[m_index] == machine) {
            time = cand_data[node].times[factory][m_index];
            break;
        }
    }
    return time;
}

int get_node(int job, int operation) {
    return job * 5 + operation + 1;
}

int nds(const std::tuple<int, int, int> & f1, const std::tuple<int, int, int> & f2) {
    std::vector<int> op(3, 0);
    int mksp1, tec1, key1;
    std::tie(mksp1, tec1, key1) = f1;    
    int mksp2, tec2, key2;
    std::tie(mksp2, tec2, key2) = f2; 
    if(mksp1 > mksp2) {
        op[0] ++;
    } else if(mksp1 == mksp2) {
        op[1] ++;
    } else {
        op[2] ++;
    }
    if(tec1 > tec2) {
        op[0] ++;
    } else if(tec1 == tec2) {
        op[1] ++;
    } else {
        op[2] ++;
    }
    if(op[0]==0 && op[1]!=2) return 1;
    if(op[2]==0 && op[1]!=2) return 2;
    return 0;
}

std::vector<int> get_nodes_to_indexes(const std::vector<int> & schedules, int JOBS) {
    int sum_operations = JOBS * 5;
    std::vector<int> nodes_to_indexes(sum_operations+1, 0);
    std::vector<int> operation(JOBS, -1);
    for(int index = 0; index<schedules.size(); index++) {
        int job = schedules[index];
        operation[job] ++;
//        int temp = get_node(job, operation[job]); 
        nodes_to_indexes[get_node(job, operation[job])] = index;
    }
    return nodes_to_indexes;
}

std::vector<int> get_indexes_to_nodes(const std::vector<int> & schedules, int JOBS) {
    std::vector<int> indexes_to_nodes(schedules.size());
    std::vector<int> operation(JOBS, -1);
    for(int index = 0; index<schedules.size(); index++) {
        int job = schedules[index];
        operation[job] ++;
        indexes_to_nodes[index] = get_node(job, operation[job]);
    }
    return indexes_to_nodes; 
}

int get_node_to_index(const std::vector<int> & schedules, int node, int JOBS) {
	std::pair<int, int> j_o_node = get_job_operation(node);
    std::vector<int> operation(JOBS, -1);
    for(int i=0; i<schedules.size(); i++) {
        int job = schedules[i];
        operation[job] ++;
        if(job==j_o_node.first && operation[job]==j_o_node.second) {
            return i;
        }
    }
    return 0;
} 

#endif
