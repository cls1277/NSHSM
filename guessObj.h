#ifndef _GUESSOBJ_H
#define _GUESSOBJ_H

#include <vector>
#include <algorithm>
#include <string>
#include "Graph.h"
#include <tuple>
#include "solveSchedule.h"
#include "tools.h"

Ret_Pop guess(const Individual & ind, const Dset_info & dset_data, const std::vector<cand_info> & cand_data) {
    int sum_operations = dset_data.JOBS * 5;
    int N = sum_operations + 1;
    int factory = std::get<2>(ind.objectives);
    Ret_Pop output(sum_operations);


    Graph graph = init_graph(ind, std::get<2>(ind.objectives), dset_data, cand_data);
    std::pair<int, std::vector<int>> cp = get_distance(graph.graph, 0, N, dset_data.JOBS, true);
    output.psjm.nodes_to_indexes = get_nodes_to_indexes(ind.schedules, dset_data.JOBS);
    
    output.psjm.indexes_to_nodes = get_indexes_to_nodes(ind.schedules, dset_data.JOBS);

    std::vector<int> operation(dset_data.JOBS, -1);
    for(int index=0; index<ind.schedules.size(); index++) {
        int job = ind.schedules[index];
        operation[job] ++;
        if(graph.PM[output.psjm.indexes_to_nodes[index]]>0 && graph.PM[output.psjm.indexes_to_nodes[index]]<N) {
            output.psjm.PM_index[index] = output.psjm.nodes_to_indexes[graph.PM[output.psjm.indexes_to_nodes[index]]];
        } else {
            output.psjm.PM_index[index] = -1;
        }
        if(graph.PJ[output.psjm.indexes_to_nodes[index]]>0 && graph.PJ[output.psjm.indexes_to_nodes[index]]<N) {
            output.psjm.PJ_index[index] = output.psjm.nodes_to_indexes[graph.PJ[output.psjm.indexes_to_nodes[index]]];
        } else {
            output.psjm.PJ_index[index] = -1;
        }
        if(graph.SM[output.psjm.indexes_to_nodes[index]]>0 && graph.SM[output.psjm.indexes_to_nodes[index]]<N) {
            output.psjm.SM_index[index] = output.psjm.nodes_to_indexes[graph.SM[output.psjm.indexes_to_nodes[index]]];
        } else {
            output.psjm.SM_index[index] = -1;
        }
        if(graph.SJ[output.psjm.indexes_to_nodes[index]]>0 && graph.SJ[output.psjm.indexes_to_nodes[index]]<N) {
            output.psjm.SJ_index[index] = output.psjm.nodes_to_indexes[graph.SJ[output.psjm.indexes_to_nodes[index]]];
        } else {
            output.psjm.SJ_index[index] = -1;
        }
    }

    std::vector<int> start_time_index(ind.schedules.size(), 0), end_time_index(ind.schedules.size(), 0);
    for(int node=0; node<graph.start_time_nodes.size(); node++) {
    	if(node<=0||node>=N) continue; 
        start_time_index[output.psjm.nodes_to_indexes[node]] = graph.start_time_nodes[node];
        end_time_index[output.psjm.nodes_to_indexes[node]] = graph.end_time_nodes[node];
    }

    std::vector<int> critical_path_machines(dset_data.MACHINES, -1);
    for(int node_index=1; node_index<cp.second.size()-1; node_index++) {
    	int node = cp.second[node_index];
        int machine = ind.machines[node-1];
        if(critical_path_machines[machine]==-1) {
            critical_path_machines[machine] = output.psjm.nodes_to_indexes[node];
        }
    }

    std::vector<Pop> bestPops, bestPops2;
    for(int v_i=1; v_i<cp.second.size()-1; v_i++) {
    	int v = cp.second[v_i];
        auto graph2 = graph.graph;

        Pop bestPop({2147483647, -1, -1, -1, "backward"});
        Pop bestPop2({2147483647, -1, -1, -1, "backward"});

        int index_v = output.psjm.nodes_to_indexes[v];
        std::pair<int, int> j_o_v = get_job_operation(v);

        if(graph.PM[v] != -1) {
            remove_edge(graph2, graph.PM[v], v);
        }
        if(graph.SM[v] != -1 && graph.SM[v] != graph.SJ[v]) {
            remove_edge(graph2, v, graph.SM[v]);
        }
        if(graph.PM[v] != -1 && graph.SM[v] != -1) {
            std::pair<int, int> j_o_sm = get_job_operation(graph.SM[v]);
            int node_sm = get_node(j_o_sm.first, j_o_sm.second);
            add_edge(graph2, graph.PM[v], graph.SM[v], get_time(node_sm, factory, ind.machines[node_sm-1], cand_data));
        }

        int new_sv = -1;
        if(graph.PJ[v] == -1) {
            new_sv = 0;
        } else {
            new_sv = get_distance(graph2, 0, graph.PJ[v], dset_data.JOBS).first;
        }
        int new_tv = get_distance(graph2, v, N, dset_data.JOBS).first;

        for(int machine : cand_data[v].machines) {
            Pop nowPop({2147483647, -1, -1, -1, "backward"});
            Pop nowPop2(nowPop);

            int time_v = get_time(v, factory, machine, cand_data);
            if(!graph.all_operations_of_machine[machine].size()) {
                nowPop = Pop({time_v + new_sv + new_tv, machine, -1, index_v, "all"});
                nowPop2 = Pop({std::get<1>(ind.objectives), machine, -1, index_v, "all"});
            } else if(graph.all_operations_of_machine[machine].size() == 1) {
                int index_u = graph.all_operations_of_machine[machine][0];
                int node_u = output.psjm.indexes_to_nodes[index_u];
                std::pair<int, int> j_o_u = get_job_operation(node_u);
                int time_u = get_time(node_u, factory, machine, cand_data);
                if(j_o_u.first == j_o_v.first) {
                    if(j_o_u.second > j_o_v.second) {
                        nowPop = Pop({time_v + new_sv + time_u + std::get<0>(ind.objectives) - end_time_index[index_u], machine, index_u, index_v, "backward"});
                        nowPop2 = Pop({std::get<1>(ind.objectives), machine, index_u, index_v, "backward"});
                    } else {
                        nowPop = Pop({time_v + new_tv + time_u + std::get<0>(ind.objectives) - end_time_index[index_u], machine, index_u, index_v, "forward"});
                        nowPop2 = Pop({std::get<1>(ind.objectives), machine, index_u, index_v, "forward"});                        
                    }
                } else {
                    int rd = rand() % 2;
                    if(rd) {
                        nowPop = Pop({time_v + new_sv + time_u + std::get<0>(ind.objectives) - end_time_index[index_u], machine, index_u, index_v, "backward"});
                        nowPop2 = Pop({std::get<1>(ind.objectives), machine, index_u, index_v, "backward"});
                    } else {
                        nowPop = Pop({time_v + new_tv + time_u + std::get<0>(ind.objectives) - end_time_index[index_u], machine, index_u, index_v, "forward"});
                        nowPop2 = Pop({std::get<1>(ind.objectives), machine, index_u, index_v, "forward"});           
                    }
                }
            } else {
                int low = 0, high = graph.all_operations_of_machine[machine].size()-1;
                int mid = -1;
                int index_mid, node_mid, time_mid;
                while(low <= high) {
                    mid = (low + high)>>1;
                    index_mid = graph.all_operations_of_machine[machine][mid];
                    node_mid = output.psjm.indexes_to_nodes[index_mid];
                    time_mid = get_time(node_mid, factory, machine, cand_data);
                    if(new_tv > std::get<0>(ind.objectives) - end_time_index[index_mid] + time_mid) {
                        high = mid - 1;
                    } else if(new_tv < std::get<0>(ind.objectives) - end_time_index[index_mid] + time_mid) {
                        low = mid + 1;
                    } else {
                        break;
                    }
                }
                int L=-1, R=-1;
                if(new_tv == std::get<0>(ind.objectives) - end_time_index[index_mid] + time_mid) {
                    L = mid - 1;
                } else {
                    L = mid;
                }

                low = 0; high = graph.all_operations_of_machine[machine].size()-1;
                mid = -1;
                while(low <= high) {
                    mid = (low + high) >> 1;
                    index_mid = graph.all_operations_of_machine[machine][mid];
                    node_mid = output.psjm.indexes_to_nodes[index_mid];
                    time_mid = get_time(node_mid, factory, machine, cand_data);
                    if(new_sv < start_time_index[index_mid] + time_mid) {
                        high = mid - 1;
                    } else if (new_sv > start_time_index[index_mid] + time_mid) {
                        low = mid + 1;
                    } else {
                        break;
                    }
                }
                if(new_sv == start_time_index[index_mid] + time_mid) {
                    R = mid + 1;
                } else {
                    R = mid;
                }

                if(L == R || L<0 || R<0) {
                    continue;
                }

                bool flag = false;
                int idx = -1, obj = 2147483647;
                if(L < R) {
                    idx = L;
                    obj = std::get<0>(ind.objectives);
                } else {
                    idx = R;
                    int index_r = graph.all_operations_of_machine[machine][idx];
                    int et = 0;
                    if(output.psjm.PJ_index[index_r] == -1) {
                        et = 0;
                    } else {
                        et = std::max(new_sv+time_v, end_time_index[output.psjm.PJ_index[index_r]]) - (new_sv + time_v);
                    }
                    obj = new_sv + time_v + et + std::get<0>(ind.objectives) - start_time_index[index_r];
                    flag = false;

                    for(int pos=R; pos<L; pos++) {
                        int index_pre = graph.all_operations_of_machine[machine][pos+1];
                        int index_pos = graph.all_operations_of_machine[machine][pos];
                        
                        int st = 0;
                        if(output.psjm.PJ_index[index_v] == -1) {
                            st = 0;
                        } else {
                            st = std::max(end_time_index[output.psjm.PJ_index[index_v]], end_time_index[index_pos]) - end_time_index[index_pos];
                        }

                        if(output.psjm.PJ_index[index_pre] == -1) {
                            et = 0;
                        } else {
                            et = std::max(end_time_index[index_pos] + st + time_v, end_time_index[output.psjm.PJ_index[index_pre]]) - (end_time_index[index_pos] + st + time_v);
                        }

                        int now_obj = end_time_index[index_pos] + st + time_v + et + std::get<0>(ind.objectives) - start_time_index[index_pre];
                        if(now_obj < obj) {
                            idx = pos;
                            obj = now_obj;
                            if(idx == R) {
                                flag = true;
                            }
                        }
                    }

                    int index_l = graph.all_operations_of_machine[machine][L];
                    int time_l = get_time(output.psjm.indexes_to_nodes[index_l], factory, machine, cand_data);
                    int st = 0;
                    if(output.psjm.PJ_index[index_v] == -1) {
                        st = 0;
                    } else {
                        st = std::max(end_time_index[output.psjm.PJ_index[index_v]], end_time_index[index_l]) - end_time_index[index_l];
                    }
                    int now_obj = start_time_index[index_l] + time_l + st + time_v + new_tv;
                    if(now_obj < obj) {
                        idx = L;
                        obj = now_obj;
                    }
                }

                if(idx==R && flag==false) {
                    nowPop = Pop({obj, machine, graph.all_operations_of_machine[machine][idx], index_v, "backward"});
                } else {
                    nowPop = Pop({obj, machine, graph.all_operations_of_machine[machine][idx], index_v, "forward"});
                }

                if(L<R) {
                    std::swap(L, R);
                }
                
                int last_critical_index = -1;
               if(critical_path_machines[machine] != -1) {
                   last_critical_index = std::find(graph.all_operations_of_machine[machine].begin(), graph.all_operations_of_machine[machine].end(), critical_path_machines[machine])-graph.all_operations_of_machine[machine].begin();
               }

                std::vector<bool> vis(sum_operations, false);
                std::vector<int> st_index_copy(start_time_index);
                std::vector<int> et_index_copy(end_time_index);

                if(last_critical_index + 1 < graph.all_operations_of_machine[machine].size() && last_critical_index < L) {
                    R = std::max(last_critical_index+1, R);
                    int w = graph.all_operations_of_machine[machine][R];
                    if(vis[w] == false) {
                        vis[w] = true;
                        delay_schedule(ind, w, output.psjm.SJ_index, output.psjm.SM_index, st_index_copy, et_index_copy, vis, cp.second, output.psjm.indexes_to_nodes, cand_data);
                    }
                }

                int time_v_origin = get_time(v, factory, ind.machines[v-1], cand_data);
                int time_v_k = get_time(v, factory, machine, cand_data);
                idx = -1, obj = 2147483647;
                if(L == graph.all_operations_of_machine[machine].size()) {
                    L --;
                }
                if(L+1 == graph.all_operations_of_machine[machine].size()) {
                    L --;
                }
                for(int pos=R; pos<L+2; pos++) {
                    int u = graph.all_operations_of_machine[machine][pos];
                    int dettime, dettime1;
                    int tmp1 = 0, tmp2 = 0;
                    if(output.psjm.PM_index[u] == -1) {
                        dettime = st_index_copy[u];
                        dettime1 = start_time_index[u];
                    } else {
                        dettime = st_index_copy[u] - end_time_index[output.psjm.PM_index[u]];
                        dettime1 = start_time_index[u] - end_time_index[output.psjm.PM_index[u]];
                        tmp1 = end_time_index[output.psjm.PM_index[u]];
                    }
                    if(output.psjm.PJ_index[index_v] != -1) {
                        tmp2 = end_time_index[output.psjm.PJ_index[index_v]];
                    }                    
                    if(dettime >= time_v_k && ( (time_v_origin  -  time_v_k >= 0 && time_v_k <= dettime1) || (3 * time_v_origin - 3 * time_v_k - dset_data.MACHINES * (time_v_k - dettime1) >= 0 && time_v_k >dettime1))) {
                    // if(dettime >= time_v_k || (4 * (time_v_origin - time_v_k) + dettime >= dset_data.MACHINES * (time_v_k - dettime))) {
                        if(output.psjm.SJ_index[index_v] == -1 || (std::max(tmp1, tmp2) + time_v_k <= st_index_copy[output.psjm.SJ_index[index_v]])) {
                        // if(output.psjm.SJ_index[index_v] == -1 || (end_time_index[index_v] + time_v_k <= st_index_copy[output.psjm.SJ_index[index_v]])) {
                            // int now_obj = std::get<1>(ind.objectives) - (4 * (time_v_origin - time_v_k) + dettime) + dset_data.MACHINES * (time_v_k - dettime);
                            int now_obj;
                            if(time_v_origin - time_v_k >= 0 && time_v_k <= dettime1) {
                                now_obj = std::get<1>(ind.objectives) - (3 * time_v_origin - 3 * time_v_k);
                            } else if(3 * time_v_origin - 3 * time_v_k - dset_data.MACHINES * (time_v_k - dettime1) >= 0 && time_v_k >dettime1) {
                                now_obj = std::get<1>(ind.objectives) - (3 * time_v_origin - 3 * time_v_k - dset_data.MACHINES * (time_v_k - dettime1));
                            }
                            if(now_obj < obj) {
                                obj = now_obj;
                                idx = pos;
                            }
                        }
                    }
                    nowPop2 = Pop({obj, machine, graph.all_operations_of_machine[machine][idx], index_v, "backward"});
                }

        }
    
            if(nowPop.idx != index_v && nowPop.idx != -1) {
                if(nowPop.obj < bestPop.obj) {
                    bestPop = nowPop;
                }
            }
            if(nowPop2.idx != index_v && nowPop2.idx != -1 && nowPop2.obj != 2147483647) {
                if(nowPop2.obj < bestPop2.obj) {
                    bestPop2 = nowPop2;
                }
            }
        }
        if(bestPop.idx != index_v && bestPop.idx != -1) {
            bestPops.push_back(bestPop);
        }
        if(bestPop2.idx != index_v && bestPop2.idx != -1) {
            bestPops2.push_back(bestPop2);
        }
    }
    output.mksp = bestPops;
    output.tec = bestPops2;
    
    return output;
}

#endif
