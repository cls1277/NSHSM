import copy

import numpy as np
import math

def pop_sort(pop1, pop2, OBJECTIVE):
    POPSIZE = pop1['schedules'].shape[0]
    pop12_objective = np.concatenate((pop1[OBJECTIVE], pop2[OBJECTIVE]))
    pop12_schedules = np.concatenate((pop1['schedules'], pop2['schedules']))
    pop12_machines = np.concatenate((pop1['machines'], pop2['machines']))
    pop12_factories = np.concatenate((pop1['factories'], pop2['factories']))
    pop12_keys = np.concatenate((pop1['key'], pop2['key']))

    _, unique_indices = np.unique(pop12_objective, axis=0, return_index=True)
    pop12_objective = pop12_objective[unique_indices]
    pop12_schedules = pop12_schedules[unique_indices]
    pop12_machines = pop12_machines[unique_indices]
    pop12_factories = pop12_factories[unique_indices]
    pop12_keys = pop12_keys[unique_indices]

    if pop12_objective.shape[1] > 1:
        non_dominated_sorted_solution2 = fast_non_dominated_sort(pop12_objective[:,:])
        length = min(POPSIZE, len(non_dominated_sorted_solution2[0]))
        crowding_distance_values2 = []
        for i in range(0, len(non_dominated_sorted_solution2)):
            crowding_distance_values2.append(
                crowding_distance(pop12_objective[:,0], pop12_objective[:,1], non_dominated_sorted_solution2[i][:]))
        new_solution = []
        for i in range(0, len(non_dominated_sorted_solution2)):
            non_dominated_sorted_solution2_1 = [
                index_of(non_dominated_sorted_solution2[i][j], non_dominated_sorted_solution2[i]) for j in
                range(0, len(non_dominated_sorted_solution2[i]))]
            front22 = sort_by_values(non_dominated_sorted_solution2_1[:], crowding_distance_values2[i][:])
            front = [non_dominated_sorted_solution2[i][front22[j]] for j in
                     range(0, len(non_dominated_sorted_solution2[i]))]
            front.reverse()
            for value in front:
                new_solution.append(value)
                if (len(new_solution) == POPSIZE):
                    break
            if (len(new_solution) == POPSIZE):
                break
        pop12_indices = [i for i in new_solution]
        # pop12_indices = [element for sublist in non_dominated_sorted_solution2 for element in sublist][::-1][:POPSIZE]
    else:
        length = POPSIZE
        temp = [element for sublist in pop12_objective for element in sublist]
        pop12_indices = np.argsort(temp)[:POPSIZE]
    pop3_objective = pop12_objective[pop12_indices]
    pop3_schedules = pop12_schedules[pop12_indices]
    pop3_machines = pop12_machines[pop12_indices]
    pop3_factories = pop12_factories[pop12_indices]
    pop3_keys = pop12_keys[pop12_indices]
    pop3 = {
        OBJECTIVE: pop3_objective,
        'schedules': pop3_schedules,
        'machines': pop3_machines,
        'factories': pop3_factories,
        'key': pop3_keys
    }
    return pop3, length

def fast_non_dominated_sort(value):
    values = copy.deepcopy(value)
    values = values.T
    """
    优化问题一般是求最小值
    :param values: 解集【目标函数1解集，目标函数2解集...】
    :return:返回解的各层分布集合序号。类似[[1], [9], [0, 8], [7, 6], [3, 5], [2, 4]] 其中[1]表示Pareto 最优解对应的序号
    """
    values11=values[0]#函数1解集
    S = [[] for i in range(0, len(values11))]#存放 每个个体支配解的集合。
    front = [[]] #存放群体的级别集合，一个级别对应一个[]
    n = [0 for i in range(0, len(values11))]#每个个体被支配解的个数 。即针对每个解，存放有多少好于这个解的个数
    rank = [np.inf for i in range(0, len(values11))]#存放每个个体的级别

    for p in range(0, len(values11)):#遍历每一个个体
        # ====得到各个个体 的被支配解个数 和支配解集合====
        S[p] = [] #该个体支配解的集合 。即存放差于该解的解
        n[p] = 0  #该个体被支配的解的个数初始化为0  即找到有多少好于该解的 解的个数
        for q in range(0, len(values11)):#遍历每一个个体
            less = 0 #的目标函数值小于p个体的目标函数值数目
            equal = 0 #的目标函数值等于p个体的目标函数值数目
            greater = 0 #的目标函数值大于p个体的目标函数值数目
            for k in range(len(values)):  # 遍历每一个目标函数
                if values[k][p] > values[k][q]:  # 目标函数k时，q个体值 小于p个体
                    less = less + 1  # q比p 好
                if values[k][p] == values[k][q]:  # 目标函数k时，p个体值 等于于q个体
                    equal = equal + 1
                if values[k][p] < values[k][q]:  # 目标函数k时，q个体值 大于p个体
                    greater = greater + 1  # q比p 差

            if (less + equal == len(values)) and (equal != len(values)):
                n[p] = n[p] + 1  # q比p,  比p好的个体个数加1

            elif (greater + equal == len(values)) and (equal != len(values)):
                S[p].append(q)  # q比p差，存放比p差的个体解序号

        #=====找出Pareto 最优解，即n[p]===0 的 个体p序号。=====
        if n[p]==0:
            rank[p] = 0 #序号为p的个体，等级为0即最优
            if p not in front[0]:
                # 如果p不在第0层中
                # 将其追加到第0层中
                front[0].append(p) #存放Pareto 最优解序号

    # print(front[0])

    # =======划分各层解========

    i = 0
    while (front[i] != []):  # 如果分层集合为不为空
        Q = []
        for p in front[i]:  # 遍历当前分层集合的各个个体p
            for q in S[p]:  # 遍历p 个体 的每个支配解q
                n[q] = n[q] - 1  # 则将fk中所有给对应的个体np-1
                if (n[q] == 0):
                    # 如果nq==0
                    rank[q] = i + 1
                    if q not in Q:
                        Q.append(q)  # 存放front=i+1 的个体序号

        i = i + 1  # front 等级+1
        front.append(Q)

    del front[len(front) - 1]  # 删除循环退出 时 i+1产生的[]

    return front #返回各层 的解序号集合 # 类似[[1], [9], [0, 8], [7, 6], [3, 5], [2, 4]]

def get_min(pop, length, data):
    objective = pop[data['objective']]
    if length == -1:
        indices = fast_non_dominated_sort(objective[:,:])[0]
    else:
        indices = list(range(length))
    # unique
    output = np.unique(objective[indices], axis=0)
    return output

# Function to find index of list,且是找到的第一个索引
def index_of(a, list):
    for i in range(0, len(list)):
        if list[i] == a:
            return i
    return -1

# Function to sort by values 找出front中对应值的索引序列
def sort_by_values(list1, values):
    sorted_list = []
    while (len(sorted_list) != len(list1)):
        if index_of(min(values), values) in list1:
            sorted_list.append(index_of(min(values), values))
        values[index_of(min(values), values)] = math.inf
    return sorted_list

#Function to calculate crowding distance
def crowding_distance(values1, values2, front):
    lenth= len(front)
    for i in range(lenth):
        values1_copy = copy.deepcopy(values1)
        values2_copy = copy.deepcopy(values2)
        distance = [0 for j in range(lenth)]
        sorted1 = sort_by_values(front, values1_copy)  #找到front中的个体索引序列
        sorted2 = sort_by_values(front, values2_copy)  #找到front中的个体索引序列
        distance[0] = 2147483647
        distance[lenth-1] = 2147483647
        for k in range(2,lenth-1):
            distance[k] = distance[k]+ (values1[sorted1[k+1]] - values1[sorted1[k-1]])/(max(values1)-min(values1))
        for k in range(2,lenth-1):
            distance[k] = distance[k]+ (values2[sorted2[k+1]] - values2[sorted2[k-1]])/(max(values2)-min(values2))
    return distance