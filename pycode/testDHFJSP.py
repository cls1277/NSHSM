# Date: 2023/12/24 12:33
# Author: cls1277
# Email: cls1277@163.com

import readData
import initPop
import localSearch
import localSearch2
import localSearch3
import localSearch4
import localSearch5
import localSearch6
import copy
import tools
import numpy as np
import pandas as pd
import popSort
import evolution
import energySave
import evalPop
import fitFJSP

np.set_printoptions(suppress=True)


OBJECTIVE = 'makespan+TEC'
DATASET = "10J2F"
PROBLEM = 'DHFJSP'
NS = 'Nall'
ITER = 5000
POPSIZE = 100

data = readData.read_data(PROBLEM, DATASET, OBJECTIVE)
pop = initPop.init_pop(POPSIZE, data, PROBLEM)
print('origin:', popSort.get_min(pop, -1, data))

iter = ITER
pop1 = copy.deepcopy(pop)
pop_new, iter = evolution.crossover(pop1, data, iter)
pop_new, iter = evolution.mutation(pop_new, data, iter)
pop1, length = popSort.pop_sort(pop1, pop_new, OBJECTIVE)
pop1, iter = energySave.full_active(pop1, length, data, iter)

pop_new, iter = localSearch6.local_search(pop1, data, iter, NS)
# print(pop_new)

#
# # print(pop['key'])
#
# iter = ITER
# pop1 = copy.deepcopy(pop)
# pop_new, iter = evolution.crossover(pop1, data, iter)
# pop_new, iter = evolution.mutation(pop_new, data, iter)
# pop1, length = popSort.pop_sort(pop1, pop_new, OBJECTIVE)
# pop1, iter = energySave.full_active(pop1, length, data, iter)
# pop_new, iter = localSearch.local_search(pop1, data, iter, 'Ntec3')
# pop1, length = popSort.pop_sort(pop1, pop_new, OBJECTIVE)
# print('Ntec3:', popSort.get_min(pop1, -1, data))
#
# iter = ITER
# pop1 = copy.deepcopy(pop)
# pop_new, iter = evolution.crossover(pop1, data, iter)
# pop_new, iter = evolution.mutation(pop_new, data, iter)
# pop1, length = popSort.pop_sort(pop1, pop_new, OBJECTIVE)
# pop1, iter = energySave.full_active(pop1, length, data, iter)
# pop_new, iter = localSearch.local_search(pop1, data, iter, 'Nopt1')
# pop1, length = popSort.pop_sort(pop1, pop_new, OBJECTIVE)
# print('Nopt1:', popSort.get_min(pop1, -1, data))
#
# iter = ITER
# pop1 = copy.deepcopy(pop)
# while iter > 0:
#     pop_new, iter = evolution.crossover(pop1, data, iter)
#     pop_new, iter = evolution.mutation(pop_new, data, iter)
#     pop1, length = popSort.pop_sort(pop1, pop_new, OBJECTIVE)
#     pop1, iter = energySave.full_active(pop1, length, data, iter)
#     pop_new, iter = localSearch.local_search(pop1, data, iter, 'Nall')
#     pop1, length = popSort.pop_sort(pop1, pop_new, OBJECTIVE)
#     print(popSort.get_min(pop1, length, data))
# print('Nall:', popSort.get_min(pop1, -1, data))

# N = data['JOBS']
# F = data['FACTORIES']
# TM = data['MACHINES']
# SH = data['sum_operations']
# H = data['operations']
# time = np.zeros(shape=(F, N, int(max(H)), TM))
# for f in range(F):
#     for j in range(N):
#         for o in range(int(H[j])):
#             node = tools.get_node(j, o, data)
#             for index, m in enumerate(data['machines'][f][node]):
#                 time[f][j][o][m] = data['times'][f][node][index]
# p_chrom = pop1['schedules'][0]
# m_chrom = pop1['machines'][0]
# f_chrom = pop1['factories'][0]
# fitness = pop1[data['objective']][0]
# print(fitFJSP.CalfitDHFJFP(p_chrom,m_chrom,f_chrom,N,H,SH,F,TM,time))

# print(evalPop.evaluate(pop1['schedules'], pop1['machines'], pop1['factories'], data))
# tools.get_gantt(pop['schedules'][0], pop['machines'][0], pop['factories'][0], data)

# OBJECTIVE = 'makespan+TEC'
# # DATASET = "50J3F"
# DATASET = "10J2F"
# PROBLEM = 'DHFJSP'
# ITER = 10000
# POPSIZE = 1
#
#
# data = readData.read_data(PROBLEM, DATASET, OBJECTIVE)
# pop = initPop.init_pop(POPSIZE, data, PROBLEM)
# print(pop[OBJECTIVE])

# tools.get_gantt(pop['schedules'][0], pop['machines'][0], pop['factories'][0], data)

# pop_new, _ = localSearch2.local_search(copy.deepcopy(pop), data, ITER, 'Nopt1')

# pop_new1, _ = localSearch.local_search(copy.deepcopy(pop), data, ITER, 'Nopt1')
# pop_new2, _ = localSearch.local_search(copy.deepcopy(pop), data, ITER, 'Nall')
# pop_new3, _ = localSearch.local_search(copy.deepcopy(pop), data, ITER, 'RAND')

# print(pop_new[OBJECTIVE])
# print(pop_new1[OBJECTIVE])
# print(pop_new2[OBJECTIVE])
# print(pop_new3[OBJECTIVE])





# A = np.unique(pop_new[OBJECTIVE])
# df = pd.DataFrame(A)
# excel_file = "Nopt1.xlsx"
# df.to_excel(excel_file, index=False, header=False)
#
# # print("---")
#
# pop_new, _ = localSearch.local_search(copy.deepcopy(pop), data, ITER, 'N7')
#
# # print(pop_new[OBJECTIVE])
# B = np.unique(pop_new[OBJECTIVE])
# df1 = pd.DataFrame(B)
# excel_file = "N7.xlsx"
# df1.to_excel(excel_file, index=False, header=False)
#
# is_subset = np.isin(B, A).all()
#
# print(A)
#
# print(B)
#
# if is_subset:
#     print("True")
# else:
#     print("False")