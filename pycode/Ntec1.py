# Date: 2023/12/11 16:19
# Author: cls1277
# Email: cls1277@163.com

import Graph
import tools
import numpy as np
import solveSchedule
import random


def neighbor(schedule, machines, factories, data, iter):
    newind_schedule = np.empty((0, len(schedule)), dtype='int32')
    newind_makespan = np.empty((0, data['objective_number']+1), dtype='int32')

    for factory in range(data['FACTORIES']):
        N = data['sum_operations'] + 1
        graph, PM, PJ, SM, SJ = Graph.init_graph(schedule, machines, factories, factory, data, True)

        # critical path
        critical_path, _ = Graph.get_distance(graph, 0, N, data, True)

        # delete the first and the last node
        critical_path = critical_path[1:-1]

        nodes_to_indexes = tools.get_nodes_to_indexes(schedule, data)
        indexes_to_nodes = tools.get_indexes_to_nodes(schedule, data)

        # start_time and end_time
        # nodes -> indexes
        start_time_index = np.zeros((len(schedule)), dtype='int32')
        end_time_index = np.zeros((len(schedule)), dtype='int32')
        operations_machines = {} # index
        start_time_nodes = np.zeros((data['sum_operations'] + 2), dtype='int32')
        end_time_nodes = np.zeros((data['sum_operations'] + 2), dtype='int32')
        endtime_job = np.zeros((data['JOBS']))
        endtime_machine = np.zeros((data['MACHINES']))
        operation = np.ones((data['JOBS']), dtype='int32') * (-1)
        for index, job in enumerate(schedule):
            if factories[job] != factory:
                continue
            operation[job] += 1
            machine = tools.get_machine(job, operation[job], machines, data)
            if machine not in operations_machines:
                operations_machines[machine] = []
            operations_machines[machine].append(index)
            time = tools.get_time(job, operation[job], machine, 0, data)
            node = tools.get_node(job, operation[job], data)
            start_time_nodes[node] = max(endtime_job[job], endtime_machine[machine])
            end_time_nodes[node] = endtime = start_time_nodes[node] + time
            endtime_job[job] = endtime_machine[machine] = endtime

        for node, st in enumerate(start_time_nodes):
            if 0 < node < N:
                start_time_index[nodes_to_indexes[node]] = st
        for node, et in enumerate(end_time_nodes):
            if 0 < node < N:
                end_time_index[nodes_to_indexes[node]] = et

        # devide critical path by machines
        critical_path_machines = Graph.get_path_machine(critical_path, machines, data)

        for i, node in enumerate(critical_path):
            critical_path[i] = nodes_to_indexes[node]
        for machine in critical_path_machines:
            for i, node in enumerate(critical_path_machines[machine]):
                critical_path_machines[machine][i] = nodes_to_indexes[node]

        PM_index = np.zeros((data['sum_operations']), dtype='int32')
        PJ_index = np.zeros((data['sum_operations']), dtype='int32')
        SM_index = np.zeros((data['sum_operations']), dtype='int32')
        SJ_index = np.zeros((data['sum_operations']), dtype='int32')
        operation = np.ones((data['JOBS']), dtype='int32') * (-1)
        for index, job in enumerate(schedule):
            operation[job] += 1
            if 0 < PM[indexes_to_nodes[index]] < N:
                PM_index[index] = nodes_to_indexes[PM[indexes_to_nodes[index]]]
            else:
                PM_index[index] = -1
            if 0 < PJ[indexes_to_nodes[index]] < N:
                PJ_index[index] = nodes_to_indexes[PJ[indexes_to_nodes[index]]]
            else:
                PJ_index[index] = -1
            if 0 < SM[indexes_to_nodes[index]] < N:
                SM_index[index] = nodes_to_indexes[SM[indexes_to_nodes[index]]]
            else:
                SM_index[index] = -1
            if 0 < SJ[indexes_to_nodes[index]] < N:
                SJ_index[index] = nodes_to_indexes[SJ[indexes_to_nodes[index]]]
            else:
                SJ_index[index] = -1

        '''
        提前关机条件：
        1. 在这台机器的最后一个关键工序之后的工序都可以尝试向前移动
        2. 向后移动不碰到关键工序，再插进空就行
        '''
        for machine in operations_machines:
            if machine in critical_path_machines:
                last_critical = critical_path_machines[machine][0]
                last_critical_index = operations_machines[machine].index(last_critical)
            else:
                last_critical_index = -1
            # 记忆化搜索：对每个有希望后移的工序搜索一遍
            if last_critical_index+1 < len(operations_machines[machine]):
                w = operations_machines[machine][last_critical_index+1]
                if not vis[w]:
                    vis[w] = True
                    solveSchedule.delay_schedule(schedule, machines, factories, w, SJ_index, SM_index, st_index_copy, et_index_copy, vis, critical_path, data)

        flag = False
        cnt2 = 0
        while 2 * cnt2 < len(operations_machines.keys()):
            if flag == True:
                break
            cnt2 += 1
            machine = random.choice(list(operations_machines.keys()))
        # for machine in operations_machines:
            if machine in critical_path_machines:
                last_critical = critical_path_machines[machine][-1]
                last_critical_index = operations_machines[machine].index(last_critical)
            else:
                last_critical_index = -1
            if last_critical_index+1 > len(operations_machines[machine])-1:
                continue
            cnt3 = 0
            while 2 * cnt3 < len(operations_machines[machine]) - last_critical_index:
                if flag == True:
                    break
                cnt3 += 1
                u_index = random.choice(range(last_critical_index+1, len(operations_machines[machine])))
            # for u_index in range(last_critical_index+1, len(operations_machines[machine])):
                if iter == 0:
                    break
                u = operations_machines[machine][u_index]
                node_u = indexes_to_nodes[u]
                job_u, operation_u = tools.get_job_operation(node_u, data)
                time_u = tools.get_time(job_u, operation_u, machines[node_u - 1], 0, data)
                if last_critical_index+1 > u_index-1 or iter == 0:
                    continue
                # u 插入到 v 的后面
                cnt4 = 0
                while 2 * cnt4 < (u_index - last_critical_index):
                    if flag == True:
                        break
                    cnt4 += 1
                    v_index = random.randint(last_critical_index+1, u_index-1)
                # for v_index in range(last_critical_index+1, u_index):
                    v = operations_machines[machine][v_index]
                    # node_v = indexes_to_nodes[v]
                    # j_v, o_v = tools.get_job_operation(node_v, data)
                    # 新的开始时间 - 旧的结束时间
                    dettime = st_index_copy[SM_index[v]] - end_time_index[v]
                    # 插空 或者 未交叉部分>machines*交叉部分
                    if (dettime >= time_u) or (dettime >= data['MACHINES'] * (time_u - dettime)):
                        # 不能到PJ的前面去
                        if (PJ_index[u] == -1) or (et_index_copy[v] >= end_time_index[PJ_index[u]]):
                            # print("u 插到 v 的后面", job_u, '-', operation_u, ' , ', j_v, '-', o_v)
                            new_schedule, new_makespan = solveSchedule.forward_schedule(schedule, machines, factories, PM_index, PJ_index, SM_index, SJ_index, u, v, data, factory=factory)

                            new_schedule = np.reshape(new_schedule, (1, -1))
                            newind_schedule = np.concatenate((newind_schedule, new_schedule), axis=0)
                            newind_makespan = np.concatenate((newind_makespan, new_makespan))
                            iter -= 1
                            flag = True

    return newind_schedule, np.tile(machines, (len(newind_schedule), 1)), newind_makespan, iter