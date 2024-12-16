# Date: 2023/12/17 16:57
# Author: cls1277
# Email: cls1277@163.com
import random
import time
import readData
import initPop
import localSearch
import popSort
import numpy as np
import copy


# DATASET = "20J3F"
OBJECTIVE = 'makespan'
# PROBLEM = 'DHFJSP'

# DATASET = "DP10"
# PROBLEM = 'FJSP'

DATASET = "la40"
PROBLEM = 'JSP'
ITER = 20000
POPSIZE = 100
data = readData.read_data(PROBLEM, DATASET, OBJECTIVE)
pop = initPop.init_pop(POPSIZE, data, PROBLEM)
print('origin:', np.min(pop[OBJECTIVE]))

iter = ITER
pop2 = copy.deepcopy(pop)
while iter > 0:
    pop_new, iter = localSearch.local_search(pop2, data, iter, 'N5', PROBLEM)
    pop2 = popSort.pop_sort(pop2, pop_new, OBJECTIVE)
    print(np.min(pop2[OBJECTIVE]))
# print(pop2[OBJECTIVE])
print('N5:', np.min(pop2[OBJECTIVE]))

iter = ITER
pop3 = copy.deepcopy(pop)
while iter > 0:
    pop_new, iter = localSearch.local_search(pop3, data, iter, OBJECTIVE, 'N5', PROBLEM)
    pop3 = popSort.pop_sort(pop3, pop_new, OBJECTIVE)
# print(pop3[OBJECTIVE])
print('N5:', np.min(pop3[OBJECTIVE]))

iter = ITER
pop1 = copy.deepcopy(pop)
while iter > 0:
    pop_new, iter = localSearch.local_search(pop1, data, iter, OBJECTIVE, 'N6', PROBLEM)
    pop1 = popSort.pop_sort(pop1, pop_new, OBJECTIVE)
# print(pop1[OBJECTIVE])
print('N6:', np.min(pop1[OBJECTIVE]))

iter = ITER
pop4 = copy.deepcopy(pop)
while iter > 0:
    pop_new, iter = localSearch.local_search(pop4, data, iter, OBJECTIVE, 'N7', PROBLEM)
    pop4 = popSort.pop_sort(pop4, pop_new, OBJECTIVE)
# print(pop4[OBJECTIVE])
print('N7:', np.min(pop4[OBJECTIVE]))

iter = ITER
pop5 = copy.deepcopy(pop)
while iter > 0:
    pop_new, iter = localSearch.local_search(pop5, data, iter, OBJECTIVE, 'N8', PROBLEM)
    pop5 = popSort.pop_sort(pop5, pop_new, OBJECTIVE)
# print(pop5[OBJECTIVE])
print('my:', np.min(pop5[OBJECTIVE]))