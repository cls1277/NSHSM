#ifndef _EVALPOP_H
#define _EVALPOP_H

#include <algorithm>
#include <vector>
#include <tuple>
#include "tools.h"

std::tuple<int, int, int> evaluate(const std::vector<int> & factories, const std::vector<int> & machines, const std::vector<int> & schedules, const Dset_info & dset_data, const std::vector<cand_info> & cand_data, int & iter) {
   iter --;
   int FACTORIES = dset_data.FACTORIES;
   int JOBS = dset_data.JOBS;
   int MACHINES = dset_data.MACHINES;
   int mksp = -1;
   int key_f = -1;
   int idle_time = 0, work_time = 0;
   for (int factory = 0; factory < FACTORIES; factory++) {
       std::vector<int> endtime_job(JOBS, 0);
       std::vector<int> endtime_machine(MACHINES, 0);
       std::vector<int> operation(JOBS, -1);
       for (int index = 0; index < schedules.size(); index++) {
           int job = schedules[index];
           if (factories[job] != factory) {
               continue;
           }
           operation[job]++;
           int node = get_node(job, operation[job]);
           int machine = machines[node-1];
           int time = get_time(node, factory, machine, cand_data);
           work_time += time;
           int start_time = std::max(endtime_job[job], endtime_machine[machine]);
           idle_time += start_time - endtime_machine[machine];
           endtime_machine[machine] = endtime_job[job] = start_time + time;
       }
       int max_endtime_machine = std::max_element(endtime_machine.begin(), endtime_machine.end()) - endtime_machine.begin();
       int max_endtime = endtime_machine[max_endtime_machine];
	   if (max_endtime > mksp) {
           key_f = factory;
           mksp = max_endtime;
       }
   }
   int TEC = work_time * 4 + idle_time;
   return std::make_tuple(mksp, TEC, key_f);
}

#endif
