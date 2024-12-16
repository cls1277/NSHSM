#ifndef _SOLVESCHEDULE_H
#define _SOLVESCHEDULE_H

#include <tuple>
#include <algorithm>
#include <vector>
#include "tools.h"
#include "evalPop.h"

void delay_schedule(const Individual & ind, int u, const std::vector<int> & SJ_index, const std::vector<int> & SM_index, std::vector<int> & st_index, std::vector<int> & et_index, std::vector<bool> & vis, const std::vector<int> & critical_path, const std::vector<int> & indexes_to_nodes, const std::vector<cand_info> & cand_data) {
    if(SJ_index[u] != -1 && vis[SJ_index[u]] == false && (std::find(critical_path.begin(), critical_path.end(), SJ_index[u]) == critical_path.end())) {
        vis[SJ_index[u]] = true;
        delay_schedule(ind, SJ_index[u], SJ_index, SM_index, st_index, et_index, vis, critical_path, indexes_to_nodes, cand_data);
    }
    if(SM_index[u] != -1 && vis[SM_index[u]] == false && (std::find(critical_path.begin(), critical_path.end(), SM_index[u]) == critical_path.end())) {
        vis[SM_index[u]] = true;
        delay_schedule(ind, SM_index[u], SJ_index, SM_index, st_index, et_index, vis, critical_path, indexes_to_nodes, cand_data);
    }
    int et = 2147483647;
    if(SJ_index[u] != -1) {
        et = std::min(et, st_index[SJ_index[u]]);
    }
    if(SM_index[u] != -1) {
        et = std::min(et, st_index[SM_index[u]]);
    }
    if(et == 2147483647) {
        et = et_index[u];
    } else {
        et = std::max(et, et_index[u]);
    }
    int node_u = indexes_to_nodes[u];
    std::pair<int, int> j_o_u = get_job_operation(node_u);
    et_index[u] = et;
    st_index[u] = et_index[u] - get_time(node_u, ind.factories[j_o_u.first], ind.machines[node_u-1], cand_data);
}

void mb_dfs(int x, const std::vector<int> & SM_index, const std::vector<int> & SJ_index, int u, int v, std::vector<bool> & vis, std::vector<bool> & is_move) {
    is_move[x] = true;
    if(x!=u && u<SM_index[x] && SM_index[x]<v && vis[SM_index[x]]==false) {
        vis[SM_index[x]] = true;
        mb_dfs(SM_index[x], SM_index, SJ_index, u, v, vis, is_move);
    }
    if(u<SJ_index[x] && SJ_index[x]<v && vis[SJ_index[x]]==false) {
        vis[SJ_index[x]] = true;
        mb_dfs(SJ_index[x], SM_index, SJ_index, u, v, vis, is_move);
    }
}

std::vector<bool> move_back(const std::vector<int> & SM_index, const std::vector<int> & SJ_index, int u, int v, int JOBS) {
    int sum_operations = JOBS * 5;
    std::vector<bool> vis(sum_operations, false), is_move(sum_operations, false);
    vis[u] = true;
    mb_dfs(u, SM_index, SJ_index, u, v, vis, is_move);
    return is_move;
}

void mf_dfs(int x, const std::vector<int> &  PM_index, const std::vector<int> &  PJ_index, int u, int v, std::vector<bool> & vis, std::vector<bool> & is_move) {
    is_move[x] = true;
    if(x!=v && u<PM_index[x] && PM_index[x]<v && vis[PM_index[x]]==false) {
        vis[PM_index[x]] = true;
        mf_dfs(PM_index[x], PM_index, PJ_index, u, v, vis, is_move);
    }
    if(u<PJ_index[x] && PJ_index[x]<v && vis[PJ_index[x]]==false) {
        vis[PJ_index[x]] = true;
        mf_dfs(PJ_index[x], PM_index, PJ_index, u, v, vis, is_move);
    }
}

std::vector<bool> move_for(const std::vector<int> & PM_index, const std::vector<int> & PJ_index, int u, int v, int JOBS) {
    int sum_operations = JOBS * 5;
    std::vector<bool> vis(sum_operations, false), is_move(sum_operations, false);
    vis[v] = true;
    mf_dfs(v, PM_index, PJ_index, u, v, vis, is_move);
    return is_move;
}

void forward_schedule(Individual & ind, const std::vector<int> & PM_index, const std::vector<int> & PJ_index, const std::vector<int> & SM_index, const std::vector<int> & SJ_index, int u, int v, const Dset_info & dset_data, const std::vector<cand_info> & cand_data, int & iter) {
   int FACTORIES = dset_data.FACTORIES;
   int JOBS = dset_data.JOBS;
   int MACHINES = dset_data.MACHINES;
    if(u < v) {
        std::vector<bool> move_back_out = move_back(SM_index, SJ_index, u, v, JOBS);
        std::vector<bool> is_move(move_back_out.begin() + u, move_back_out.begin() + v);
//        for(auto it : is_move) {
//        	std::cout<<it<<' ';
//		}        
//		printf("\n");
        std::vector<int> move, not_move;
        for(int i=u; i<v; i++) {
            if(is_move[i-u] == true) {
                move.push_back(ind.schedules[i]);
            } else {
                not_move.push_back(ind.schedules[i]);
            }
        }
//        for(auto it : move) {
//        	printf("%d ", it);
//		}
//		printf("\n");
//		for(auto it : not_move) {
//			printf("%d ", it);
//		}
        int temp = ind.schedules[v];
        ind.schedules.erase(ind.schedules.begin() + u, ind.schedules.begin() + v + 1);
        ind.schedules.insert(ind.schedules.begin() + u, not_move.begin(), not_move.end());
        ind.schedules.insert(ind.schedules.begin() + u + not_move.size(), temp);
        ind.schedules.insert(ind.schedules.begin() + u + not_move.size() + 1, move.begin(), move.end());
    } else {
        std::vector<bool> move_for_out = move_for(PM_index, PJ_index, v, u, JOBS);
        std::vector<bool> is_move(move_for_out.begin() + v + 1, move_for_out.begin() + u + 1);
        std::vector<int> move, not_move;
        for(int i=v+1; i<u+1; i++) {
            if(is_move[i-v-1] == true) {
                move.push_back(ind.schedules[i]);
            } else {
                not_move.push_back(ind.schedules[i]);
            }
        }
        int temp = ind.schedules[v];
        ind.schedules.erase(ind.schedules.begin() + v, ind.schedules.begin() + u + 1);
        ind.schedules.insert(ind.schedules.begin() + v, temp);
        ind.schedules.insert(ind.schedules.begin() + v + 1, move.begin(), move.end());
        ind.schedules.insert(ind.schedules.begin() + v + 1 + move.size(), not_move.begin(), not_move.end());
    }
    ind.objectives = evaluate(ind.factories, ind.machines, ind.schedules, dset_data, cand_data, iter);
}

void backward_schedule(Individual & ind, const std::vector<int> & PM_index, const std::vector<int> &  PJ_index, const std::vector<int> &  SM_index, const std::vector<int> &  SJ_index, int u, int v, const Dset_info & dset_data, const std::vector<cand_info> & cand_data, int & iter) {
    int FACTORIES = dset_data.FACTORIES;
   int JOBS = dset_data.JOBS;
   int MACHINES = dset_data.MACHINES;
    if(u >= v) {
        std::vector<bool> move_back_out = move_back(SM_index, SJ_index, v, u, JOBS);
        std::vector<bool> is_move(move_back_out.begin() + v, move_back_out.begin() + u);
        std::vector<int> move, not_move;
        for(int i=v; i<u; i++) {
            if(is_move[i-v] == true) {
                move.push_back(ind.schedules[i]);
            } else {
                not_move.push_back(ind.schedules[i]);
            }
        }
        int temp = ind.schedules[u];
        ind.schedules.erase(ind.schedules.begin() + v, ind.schedules.begin() + u + 1);
        ind.schedules.insert(ind.schedules.begin() + v, not_move.begin(), not_move.end());
        ind.schedules.insert(ind.schedules.begin() + v + not_move.size(), move.begin(), move.end());
        ind.schedules.insert(ind.schedules.begin() + v + not_move.size() + move.size(), temp);
    } else {
        std::vector<bool> move_for_out = move_for(PM_index, PJ_index, u, v, JOBS);
        std::vector<bool> is_move(move_for_out.begin() + u + 1, move_for_out.begin() + v + 1);
        std::vector<int> move, not_move;
        for(int i=u+1; i<v+1; i++) {
            if(is_move[i-u-1] == true) {
                move.push_back(ind.schedules[i]);
            } else {
                not_move.push_back(ind.schedules[i]);
            }
        }
        int temp = ind.schedules[u];
        ind.schedules.erase(ind.schedules.begin() + u, ind.schedules.begin() + v + 1);
        ind.schedules.insert(ind.schedules.begin() + u, move.begin(), move.end());
        ind.schedules.insert(ind.schedules.begin() + u + move.size(), temp);
        ind.schedules.insert(ind.schedules.begin() + u + move.size() + 1, not_move.begin(), not_move.end());
    }
    ind.objectives = evaluate(ind.factories, ind.machines, ind.schedules, dset_data, cand_data, iter);
}

#endif
