#ifndef _LOCALSEARCH2_H
#define _LOCALSEARCH2_H

#include <vector>
#include <tuple>
#include <algorithm>
#include <string>
#include "guessObj.h"
#include <cmath>
#include <set>
#include "evalPop.h"
#include "tools.h"
#include "popSort2.h"


std::vector<Individual> local_search(std::vector<Individual> & pop_old, const Dset_info & dset_data, const std::vector<cand_info> & cand_data, int & iter, double& det, int& detc, double Pk = 0.5) {
    std::vector<std::tuple<int, int, int>> objectives;
    std::sort(pop_old.begin(), pop_old.end());
    for(const Individual & ind : pop_old) {
    	objectives.push_back(ind.objectives); 
	}
    
//    for(auto it : objectives) {
//		printf("%d %d\n", std::get<0>(it), std::get<1>(it));
//	 } 
	
    std::vector<int> pop_index = fast_non_dominated_sort(objectives)[0];
    std::vector<Individual> pop;
    for(int pop_i : pop_index) {
    	pop.push_back(pop_old[pop_i]);
	}
	// printf("%d\n",pop.size());
	
	std::vector<Individual> new_pop;
    
    int POPSIZE = pop.size();
    // std::vector<std::pair<int, int>> min_objs[2];
    std::vector<Min_Objs> min_objs[2];
    std::vector<PSJM> psjms;
    for(int i=0; i<POPSIZE; i++) {
        Ret_Pop output = guess(pop[i], dset_data, cand_data);
        psjms.push_back(output.psjm);
        int res1 = 2147483647, res2 = 2147483647;
        for(const Pop & it : output.mksp) {
            res1 = std::min(res1, it.obj);
        }
        min_objs[0].push_back({res1, i, output.mksp});
        for(const Pop & it : output.tec) {
            res2 = std::min(res2, it.obj);
        }
        min_objs[1].push_back({res2, i, output.tec});
        // printf("%d\n",output.tec.size());
    }
    std::sort(min_objs[0].begin(), min_objs[0].end());
    std::sort(min_objs[1].begin(), min_objs[1].end());
    int K = std::ceil(POPSIZE * Pk);
    // makespan
    for(int i=0; i<K; i++) {
        Min_Objs bestPop = min_objs[0][i];
        PSJM p = psjms[bestPop.idx];
        for(const Pop & it : bestPop.pop) {
            int index_v = it.v;
            if(it.idx == index_v || it.idx == -1) {
                continue;
            }
            // std::cout<<it.direction<<' ';
            // printf("%d %d %d %d\n",it.obj, it.machine, it.idx, it.v); 
            int v = p.indexes_to_nodes[index_v];
            Individual new_ind = pop[bestPop.idx];
            new_ind.machines[v-1] = it.machine;
//            for(auto it : p.indexes_to_nodes) {
//            	printf("%d ", it);
//			}
//			printf("\n");
            int node_best = p.indexes_to_nodes[it.idx];
            if(it.direction == "all") {
                new_ind.objectives = evaluate(new_ind.factories, new_ind.machines, new_ind.schedules, dset_data, cand_data, iter);
            } else if(it.direction == "forward") {
                forward_schedule(new_ind, p.PM_index, p.PJ_index, p.SM_index, p.SJ_index, index_v, it.idx, dset_data, cand_data, iter);
            } else {
                backward_schedule(new_ind, p.PM_index, p.PJ_index, p.SM_index, p.SJ_index, it.idx, index_v, dset_data, cand_data, iter);
            }
            // printf("%d %d\n",std::get<0>(new_ind.objectives), std::get<1>(new_ind.objectives));
            new_pop.push_back(new_ind);
        }
    }
    // tec
//    double det = 0; int detc = 0;
    for(int i=0; i<K; i++) {
        Min_Objs bestPop = min_objs[1][i];
        PSJM p = psjms[bestPop.idx];
        for(const Pop & it : bestPop.pop) {
            int index_v = it.v;
            if(it.idx == index_v || it.idx == -1) {
                continue;
            }
            int v = p.indexes_to_nodes[index_v];
            Individual new_ind = pop[bestPop.idx];
            new_ind.machines[v-1] = it.machine;
            int node_best = p.indexes_to_nodes[it.idx];
            if(it.direction == "all") {
                new_ind.objectives = evaluate(new_ind.factories, new_ind.machines, new_ind.schedules, dset_data, cand_data, iter);
            } else if(it.direction == "forward") {
                forward_schedule(new_ind, p.PM_index, p.PJ_index, p.SM_index, p.SJ_index, index_v, it.idx, dset_data, cand_data, iter);
            } else {
                backward_schedule(new_ind, p.PM_index, p.PJ_index, p.SM_index, p.SJ_index, it.idx, index_v, dset_data, cand_data, iter);
            }
            new_pop.push_back(new_ind);
            det += std::fabs(std::get<1>(new_ind.objectives)-it.obj) / it.obj;
            detc ++;
        }
    }
   /* if(detc) {
        printf("delta: %.4lf\n", det / detc);
    }*/

    return new_pop;
}

#endif
