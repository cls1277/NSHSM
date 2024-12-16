#ifndef _INITPOP_CPP
#define _INITPOP_CPP

#include "mex.h"
#include <vector>
#include <time.h>
#include <algorithm>
#include <tuple>
#include <random>       // std::default_random_engine
#include <chrono>       // std::chrono::system_clock
#include "tools.h"

std::vector<int> ROS(int JOBS) {
    int sum_operations = JOBS * 5;
    std::vector<int> schedule;
    for(int i=0; i<JOBS; i++) {
    	for(int j=0; j<5; j++) {
    		schedule.push_back(i);
		}
	}
    std::default_random_engine e(rand());
    std::shuffle(schedule.begin(), schedule.end(), e);
	// std::random_shuffle(schedule.begin(), schedule.end());
    return schedule;
}

std::vector<int> HMS_global(std::vector<int> factory, int JOBS, int FACTORIES, int MACHINES, const std::vector<cand_info> & cand_data) {
    int sum_operations = JOBS * 5;
    std::vector<int> machine(sum_operations, 0);
    std::vector<std::vector<int>> time_machines(FACTORIES, std::vector<int>(MACHINES, 0));

    for (int j = 0; j < sum_operations; ++j) {
        int node = j+1;
        std::pair<int, int> job_operation = get_job_operation(node);
        int f = factory[job_operation.first];
        int time_min = 2147483647;
        int machine_min = -1;

        for(int i=0; i<cand_data[node].machines.size(); i++) {
            int machine = cand_data[node].machines[i];
            int time_node = cand_data[node].times[f][i];
            if (time_min > time_node) {
                time_min = time_node;
                machine_min = machine;
            }
        }

        machine[j] = machine_min;
        time_machines[f][machine_min] += time_min;
    }

    return machine;
}

std::vector<int> HMS_local(std::vector<int> factory, int JOBS, int FACTORIES, int MACHINES, const std::vector<cand_info> & cand_data) {
    int sum_operations = JOBS * 5;
    std::vector<int> machine(sum_operations, 0);

    for (int i = 0; i < sum_operations; ++i) {
        int node = i+1;
        std::pair<int, int> job_operation = get_job_operation(node);
        int f = factory[job_operation.first];
        int time_min = 2147483647;
        int machine_min = -1;

        for(int i=0; i<cand_data[node].machines.size(); i++) {
            int machine = cand_data[node].machines[i];
            int time_node = cand_data[node].times[f][i];
            if (time_min > time_node) {
                time_min = time_node;
                machine_min = machine;
            }
        }

        machine[i] = machine_min;
    }

    return machine;
}

std::vector<int> RMS(std::vector<int> factory, int JOBS, const std::vector<cand_info> & cand_data) {
    int sum_operations = JOBS * 5;
    std::vector<int> machine(sum_operations, 0);

    for (int i = 0; i < sum_operations; ++i) {
        std::pair<int, int> job_operation = get_job_operation(i+1);
        int rd_index = rand() % (cand_data[i+1].machines.size());
        machine[i] = cand_data[i+1].machines[rd_index];
    }

    return machine;
}

std::vector<int> HFS_global(int JOBS, int FACTORIES, const std::vector<cand_info> & cand_data) {
    std::vector<int> factory(JOBS, 0);
    std::vector<int> time_all(FACTORIES, 0);

    for (int job = 0; job < JOBS; ++job) {
        std::vector<int> time_factory(time_all);
        for (int f = 0; f < FACTORIES; ++f) {
            for (int operation = 0; operation < 5; ++operation) {
                int node = get_node(job, operation);
                int time_min = 2147483647;
                for(int i = 0; i<cand_data[node].machines.size(); i++) {
                    int machine = cand_data[node].machines[i];
                    int time_node = cand_data[node].times[f][i];
                    time_min = std::min(time_min, time_node);
                }
                time_factory[f] += time_min;
            }
        }
        int min_index = std::min_element(time_factory.begin(), time_factory.end()) - time_factory.begin();
        factory[job] = min_index;
        time_all[min_index] += time_factory[min_index];
    }

    return factory;
}

std::vector<int> HFS_local(int JOBS, int FACTORIES, const std::vector<cand_info> & cand_data) {
    std::vector<int> factory(JOBS, 0);

    for (int job = 0; job < JOBS; ++job) {
        std::vector<int> time_factory(FACTORIES, 0);
        for (int f = 0; f < FACTORIES; ++f) {
            for (int operation = 0; operation < 5; ++operation) {
                int node = get_node(job, operation);
                int time_min = 2147483647;
                for(int i = 0; i<cand_data[node].machines.size(); i++) {
                    int machine = cand_data[node].machines[i];
                    int time_node = cand_data[node].times[f][i];
                    time_min = std::min(time_min, time_node);
                }
                time_factory[f] += time_min;
            }
        }
        int min_index = std::min_element(time_factory.begin(), time_factory.end()) - time_factory.begin();
        factory[job] = min_index;
    }

    return factory;
}

std::vector<int> RFS(int JOBS, int FACTORIES) {
    std::vector<int> factory(JOBS, 0);

    for (int job = 0; job < JOBS; ++job) {
        factory[job] = std::rand() % FACTORIES;
    }

    return factory;
}

std::vector<std::vector<int>> init_pop(int POPSIZE, const Dset_info & dset_data, const std::vector<cand_info> & cand_data) {
    int FACTORIES = dset_data.FACTORIES;
    int JOBS = dset_data.JOBS;
    int MACHINES = dset_data.MACHINES;
    // std::vector<Individual> population;
    std::vector<std::vector<int>> population;
    int sum_operations = JOBS * 5;
    for(int i=1; i<=POPSIZE; i++) {
        std::vector<int> factory, machines, schedules;
        if(i <= POPSIZE * 0.6) {
            factory = HFS_global(JOBS, FACTORIES, cand_data);
            machines = HMS_global(factory, JOBS, FACTORIES, MACHINES, cand_data);
            schedules = ROS(JOBS);
        } else if(i <= POPSIZE * 0.9) {
            factory = HFS_local(JOBS, FACTORIES, cand_data);
            machines = HMS_local(factory, JOBS, FACTORIES, MACHINES, cand_data);
            schedules = ROS(JOBS);            
        } else {
            factory = RFS(JOBS, FACTORIES);
            machines = RMS(factory, JOBS, cand_data);
            schedules = ROS(JOBS);
        }
        std::vector<int> ind;
        for(int x : factory) {
            ind.push_back(x);
        }
        for(int x : machines) {
            ind.push_back(x);
        }
        for(int x : schedules) {
            ind.push_back(x);
        }
        population.push_back(ind);
    }
    return population;
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
    std::vector<std::vector<int>> inData3 = init_pop(POPSIZE, dset_data, cand_data);

    int D = JOBS + 5 * JOBS + 5 * JOBS;
    plhs[0] = mxCreateDoubleMatrix(POPSIZE, D, mxREAL);
    double *outData = mxGetPr(plhs[0]);
    int cnt3 = 0;
    for(int i=0; i<D; i++) {
        for(int j=0; j<POPSIZE; j++) {
            outData[cnt3] = double(inData3[j][i]);
            cnt3++;
        }
    }
}

#endif

