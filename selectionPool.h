#ifndef _SELECTIONPOOL_H
#define _SELECTIONPOOL_H

#include <algorithm>
#include <vector>
#include "tools.h"
#include <tuple>


// 返回在pop中的下标
std::vector<int> tournament_selection(const std::vector<Individual> & pop) {

    std::vector<int> output;
    int POPSIZE = pop.size();

    for(int i=0; i<POPSIZE; i++) {
        int f1 = std::rand()%POPSIZE, f2 = std::rand()%POPSIZE;
        int op = nds(pop[f1].objectives, pop[f2].objectives);
        if(op == 1) {
            output.push_back(f1);
        } else if(op == 2) {
            output.push_back(f2);
        } else {
            if(rand()%2) {
                output.push_back(f1);
            } else {
                output.push_back(f2);
            }
        }
    }
    return output;
}

#endif