# Date: 2023/12/20 17:56
# Author: cls1277
# Email: cls1277@163.com

import readData
import initPop
import localSearch
import popSort
import numpy as np
import copy
import tools


OBJECTIVE = 'makespan'
DATASET = "Mk01"
PROBLEM = 'FJSP'
NS = 'Nopt1'
ITER = 20000
POPSIZE = 100
data = readData.read_data(PROBLEM, DATASET, OBJECTIVE)
pop = initPop.init_pop(POPSIZE, data, PROBLEM)
print('origin:', np.min(pop[OBJECTIVE]))

iter = ITER
pop1 = copy.deepcopy(pop)
while iter > 0:
    pop_new, iter = localSearch.local_search(pop1, data, iter, NS, PROBLEM)
    pop1 = popSort.pop_sort(pop1, pop_new, OBJECTIVE)
    print(np.min(pop1[OBJECTIVE]))
print(NS, ':', np.min(pop1[OBJECTIVE]))