# Date: 2024/4/10 19:37
# Author: cls1277
# Email: cls1277@163.com

import readData
import initPop
import localSearch2
import popSort
import copy
import evolution
import energySave
import tools
import numpy as np
import os
import time
import json
np.set_printoptions(suppress=True)


OBJECTIVE = 'makespan+TEC'
PROBLEM = 'DHFJSP'
POPSIZEs = [100, 150, 200]
PCs = [0.8, 0.9, 1.0]
PMs = [0.1, 0.15, 0.2]
PKs = [0.3, 0.4, 0.5]
LP = [[1, 1, 1, 1], [1, 2, 3, 2], [1, 3, 2, 3], [2, 1, 3, 3], [2, 2, 2, 1], [2, 3, 1, 2], [3, 1, 2, 2], [3, 2, 1, 3], [3, 3, 3, 1]]
COUNT = 20
EXPERIMENT = 'Runningtime'

for lpi in range(len(LP)):
    lp = LP[lpi]
    POPSIZE = POPSIZEs[lp[0]-1]
    PC = PCs[lp[1]-1]
    PM = PMs[lp[2]-1]
    PK = PKs[lp[3]-1]
    EXPERIMENT = 'Parameters_POPSIZE' + str(POPSIZE) + '_Pc' + str(PC) + '_Pm' + str(PM) + '_Pk' + str(PK)

    all_start_time = time.time()
    current_path = os.path.dirname(os.path.abspath(__file__))
    # current_path = 'C:\\cls\\cls1277\\DHFJS\\EEDHFJSP\\NS'
    file_path = os.path.join(current_path, '..', PROBLEM+'-benchmark', 'instances.json')
    with open(file_path, "r", encoding="utf-8") as f:
        js = json.load(f)
    for i in range(len(js)):
        DATASET = js[i]["name"]
        count = 0
        # start experiment
        while count < COUNT:
            start_time = time.time()
            count += 1

            data = readData.read_data(PROBLEM, DATASET, OBJECTIVE)
            ITERTHRE = 200 * data['sum_operations']
            iter = ITERTHRE
            pop = initPop.init_pop(POPSIZE, data, PROBLEM)

            pop1 = copy.deepcopy(pop)
            while iter > 0:
                st = time.time()
                pop_new, iter = evolution.crossover(pop1, data, iter, Pc=PC)
                et1 = time.time()
                pop_new, iter = evolution.mutation(pop_new, data, iter, Pm=PM)
                et2 = time.time()
                pop1, length = popSort.pop_sort(pop1, pop_new, OBJECTIVE)
                et3 = time.time()
                pop1, iter = energySave.full_active(pop1, length, data, iter)
                et4 = time.time()

                pop_new, iter = localSearch2.local_search(pop1, data, iter, Pk=PK)
                et5 = time.time()
                pop1, length = popSort.pop_sort(pop1, pop_new, OBJECTIVE)
                et6 = time.time()
                # print(popSort.get_min(pop1, length, data))
                print(et1-st, et2-et1, et3-et2, et4-et3, et5-et4, et6-et5)
                # print(f"{EXPERIMENT} on {DATASET}, {count}th iteration, {((ITERTHRE - iter) / ITERTHRE) * 100:.2f}%")
            end_time = time.time()

            # create the directory to save the result
            current_path = os.path.dirname(os.path.abspath(__file__))
            # other_info = 'POPSIZE'+str(POPSIZE)+'_Pc'+str(PC)+'_Pm'+str(PM)+'_Pk'+str(PK)+'_'+str(DATASET)
            other_info = str(DATASET)
            exper_path = os.path.join(current_path, 'result', EXPERIMENT, other_info)
            if not os.path.exists(exper_path):
                os.makedirs(exper_path)

            # save results
            file_path = os.path.join(exper_path, 'res_'+str(count)+'.txt')
            tools.write_objective(pop1, file_path, data)

            file_path = os.path.join(exper_path, 'pop_'+str(count)+'.txt')
            tools.write_population(pop1, file_path, data)

            file_path = os.path.join(exper_path, 'time_'+str(count)+'.txt')
            tools.write_time(end_time-start_time, file_path)

            print(f"{EXPERIMENT} on {DATASET}, {count}th iteration end, {time.time() - all_start_time:.2f}s passed...")
