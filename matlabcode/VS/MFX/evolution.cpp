#ifndef _EVOLUTION_CPP
#define _EVOLUTION_CPP

#include "mex.h"
#include <algorithm>
#include <vector>
#include <tuple>
#include <random>
#include <iostream>
#include <ctime>
#include <set>
#include "Nrand.h"
#include "tools.h"
#include <fstream>

std::pair<std::vector<int>, std::vector<int>> POX(const std::vector<int> & schedule1, const std::vector<int> & schedule2, int JOBS) {
    int sum_operations = JOBS * 5;
   std::vector<int> new_s1(sum_operations, -1);
   std::vector<int> new_s2(sum_operations, -1);
   std::vector<int> jobs;

    for(int i=0; i<JOBS; i++) {
        jobs.push_back(i);
    }
    std::default_random_engine e(rand());
    std::shuffle(jobs.begin(), jobs.end(), e);
    // std::random_shuffle(jobs.begin(), jobs.end());

    std::set<int> I1, I2;
   int n = rand() % JOBS;
   for(int i=0; i<n; i++) {
    I1.insert(jobs[i]);
   }
   for (int i = n; i < JOBS; i++) {
    I2.insert(jobs[i]);
   }

   int p1 = 0;
   for (int i = 0; i < sum_operations; i++) {
       int job1 = schedule1[i];
       if(I1.find(job1) != I1.end()) {
           new_s1[i] = job1;
       } else {
           for (int j = p1; j < sum_operations; j++) {
               int job2 = schedule2[j];
               if (I2.find(job2) != I2.end()) {
                   new_s1[i] = job2;
                   p1 = j+1;
                   break;
               }
           }
       }
   }

   int p2 = 0;
   for (int i = 0; i < sum_operations; i++) {
       int job2 = schedule2[i];
       if (I2.find(job2) != I2.end()) {
           new_s2[i] = job2;
       } else {
           for (int j = p2; j < sum_operations; j++) {
               int job1 = schedule1[j];
               if (I1.find(job1) != I1.end()) {
                   new_s2[i] = job1;
                   p2 = j+1;
                   break;
               }
           }
       }
   }

   return std::make_pair(new_s1, new_s2);
}

std::pair<std::vector<int>, std::vector<int>> UX(const std::vector<int> & sequence1, const std::vector<int> & sequence2) {
   std::vector<int> random_binary_string(sequence1.size());
   for (int i = 0; i < sequence1.size(); i++) {
       random_binary_string[i] = rand() % 2;
   }

   std::vector<int> result1, result2;
   for (int i = 0; i < sequence1.size(); i++) {
       if (random_binary_string[i] == 1) {
           result1.push_back(sequence2[i]);
           result2.push_back(sequence1[i]);
       } else {
           result1.push_back(sequence1[i]);
           result2.push_back(sequence2[i]);
       }
   }
   return std::make_pair(result1, result2);
}

std::vector<Individual> DHFJSP_cross_over(const Individual & f1, const Individual & f2, const Dset_info & dset_data, const std::vector<cand_info> & cand_data) {
    std::pair<std::vector<int>, std::vector<int>> new_schedule = POX(f1.schedules, f2.schedules, dset_data.JOBS);
    std::pair<std::vector<int>, std::vector<int>> new_factory = UX(f1.factories, f2.factories);
    std::pair<std::vector<int>, std::vector<int>> new_machine = UX(f1.machines, f2.machines);
    std::vector<Individual> output;
    output.push_back({new_factory.first, new_machine.first, new_schedule.first, std::make_tuple(0, 0, 0)});
    output.push_back({new_factory.second, new_machine.second, new_schedule.second, std::make_tuple(0, 0, 0)});
    return output;
}

std::vector<Individual> crossover(const std::vector<Individual> & pop, const Dset_info & dset_data, const std::vector<cand_info> & cand_data, double Pc = 0.9) {
    int POPSIZE = pop.size();
    std::vector<Individual> pop_new;

    while(pop_new.size() < POPSIZE) {
        int f1 = std::rand()%pop.size(), f2 = std::rand()%pop.size();
        double rd = (std::rand()%100+1) * 1.0 / 100;
        if(rd <= Pc) {
            std::vector<Individual> co_result = DHFJSP_cross_over(pop[f1], pop[f2], dset_data, cand_data);
            pop_new.push_back(co_result[0]);
            pop_new.push_back(co_result[1]);
        } else {
            pop_new.push_back(pop[f1]);
            pop_new.push_back(pop[f2]);
        }
    }
    return pop_new;
}

void mutation(std::vector<Individual> & pop, const Dset_info & dset_data, const std::vector<cand_info> & cand_data, double Pm = 0.1) {
    int FACTORIES = dset_data.FACTORIES;
    int MACHINES = dset_data.MACHINES;
    int JOBS = dset_data.JOBS;
    int POPSIZE = pop.size();
    for(int i=0; i<POPSIZE; i++) {
        double rd = (std::rand()%100+1) * 1.0 / 100;
        if(rd <= Pm) {
            int rm = rand() % 4;
            if(rm == 0) {
                swap_all(pop[i], FACTORIES, JOBS);
            } else if(rm == 1) {
                swap_key(pop[i], JOBS);
            } else if(rm == 2) {
                insert_all(pop[i], FACTORIES, JOBS);
            } else {
                insert_key(pop[i], JOBS);
            }

            rm = rand() % 2;
            if(rm) {
                machine_all(pop[i], dset_data, cand_data);
            } else {
                machine_roule(pop[i], dset_data, cand_data);
            }

            factory_mu(pop[i], JOBS, FACTORIES);
        }
    }
}

void mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]){
    const mwSize *Dims0 = mxGetDimensions(prhs[0]);
    double *inData0 = mxGetPr(prhs[0]);
    int POPSIZE = int(inData0[0]), FACTORIES = int(inData0[1]), JOBS = int(inData0[2]);
    
    const mwSize *Dims2 = mxGetDimensions(prhs[2]);

    double *inData1 = mxGetPr(prhs[1]);
    double *inData2 = mxGetPr(prhs[2]);
    std::vector<cand_info> cand_data;
    cand_data.push_back(cand_info());

    int cnt1 = 0, cnt2 = 0;
    for(mwSize node=0; node<Dims2[2]; node++) {
        std::vector<int> machines;
        std::vector<std::vector<int>> times;
        for(mwSize mac=0; mac<Dims2[0]; mac++) {
            if(int(inData1[cnt1])==1) {
                machines.push_back(mac);
            }
            cnt1++;
        }

        for(mwSize fac=0; fac<Dims2[1]; fac++) {
            std::vector<int> times_;
            for(mwSize mac=0; mac<Dims2[0]; mac++) {
                if(int(inData1[node*Dims2[0]+mac])==1) {
                    times_.push_back(inData2[cnt2]);
                }
                cnt2++;
            }
            times.push_back(times_);
        }

        cand_data.push_back({machines, times});
    }

    Dset_info dset_data({FACTORIES, 5, JOBS});

    const mwSize *Dims3 = mxGetDimensions(prhs[3]);
    double *inData3 = mxGetPr(prhs[3]);

    int cnt3 = 0;
    std::vector<Individual> pop;
    for(int j=0; j<Dims3[1]; j++) {
        Individual ind;
        for(int k=0; k<Dims3[0]; k++) {
            if(k<dset_data.JOBS) {
                ind.factories.push_back(int(inData3[cnt3]));
            } else if(k<dset_data.JOBS+dset_data.JOBS*5) {
                ind.machines.push_back(int(inData3[cnt3]));
            } else {
                ind.schedules.push_back(int(inData3[cnt3]));
            }
            cnt3++;
        }
        ind.objectives = std::make_tuple(0, 0, 0);
        pop.push_back(ind);
    }

    POPSIZE = pop.size();
    std::vector<Individual> new_pop = crossover(pop, dset_data, cand_data);
    mutation(new_pop, dset_data, cand_data);

    std::vector<std::vector<int>> inData4;
    for(Individual ind : pop) {
        std::vector<int> temp;
        for(auto it : ind.factories) temp.push_back(it);
        for(auto it : ind.machines) temp.push_back(it);
        for(auto it : ind.schedules) temp.push_back(it);
        inData4.push_back(temp);
    }

    int D = JOBS + 5 * JOBS + 5 * JOBS;
    plhs[0] = mxCreateDoubleMatrix(POPSIZE, D, mxREAL);
    double *outData = mxGetPr(plhs[0]);
    int cnt4 = 0;
    for(int i=0; i<D; i++) {
        for(int j=0; j<POPSIZE; j++) {
            outData[cnt4] = double(inData4[j][i]);
            cnt4++;
        }
    }
}

#endif