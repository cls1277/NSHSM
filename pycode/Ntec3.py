# Date: 2024/1/30 19:23
# Author: cls1277
# Email: cls1277@163.com
import copy
import random
import numpy as np
import tools
import Graph
import solveSchedule
import evalPop

# random.seed(1)

def neighbor(schedule, machines, factories, objetives, key, data, iter):
    newind_schedule = np.empty((0, len(schedule)), dtype='int32')
    newind_machines = np.empty((0, len(machines)), dtype='int32')
    newind_makespan = np.empty((0, data['objective_number']+1), dtype='int32')

    factory = int(key)

    N = data['sum_operations'] + 1
    graph, PM, PJ, SM, SJ = Graph.init_graph(schedule, machines, factories, factory, data)

    # critical path
    critical_path, mksp = Graph.get_distance(graph, 0, N, data, True)

    # delete the first and the last node
    critical_path = critical_path[1:-1]

    nodes_to_indexes = tools.get_nodes_to_indexes(schedule, data)
    indexes_to_nodes = tools.get_indexes_to_nodes(schedule, data)

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

    start_time_nodes, end_time_nodes = tools.get_start_end_time(schedule, machines, factories, data, factory)
    start_time_index = np.zeros((len(schedule)), dtype='int32')
    end_time_index = np.zeros((len(schedule)), dtype='int32')
    for node, st in enumerate(start_time_nodes):
        if 0 < node < N:
            start_time_index[nodes_to_indexes[node]] = st
    for node, et in enumerate(end_time_nodes):
        if 0 < node < N:
            end_time_index[nodes_to_indexes[node]] = et

    # devide critical path by machines
    critical_path_machines = Graph.get_path_machine(critical_path, machines, data)

    for machine in critical_path_machines:
        for i, node in enumerate(critical_path_machines[machine]):
            critical_path_machines[machine][i] = nodes_to_indexes[node]

    # get all operations on each machine
    all_operations_of_machine = {}
    operation = np.ones((data['JOBS']), dtype='int32') * (-1)
    for index, job in enumerate(schedule):
        if factories[job] != factory:
            continue
        operation[job] += 1
        machine = tools.get_machine(job, operation[job], machines, data)
        if machine not in all_operations_of_machine:
            all_operations_of_machine[machine] = []
        all_operations_of_machine[machine].append(index)

    # start doing Nopt1
    # the subscript of v is "node"
    for v in critical_path:
        index_v = nodes_to_indexes[v]
        job_v, operation_v = tools.get_job_operation(v, data)

        # get the new graph by moving two edges and adding one edge
        new_graph = copy.deepcopy(graph)
        if PM[v] != -1:
            new_graph = Graph.remove_edge(new_graph, PM[v], v)
        if SM[v] != -1 and SM[v] != SJ[v]:
            new_graph = Graph.remove_edge(new_graph, v, SM[v])
        if PM[v] != -1 and SM[v] != -1:
            job_smv, operation_smv = tools.get_job_operation(SM[v], data)
            machine_smv = tools.get_machine(job_smv, operation_smv, machines, data)
            Graph.add_edge(new_graph, PM[v], SM[v], tools.get_time(job_smv, operation_smv, machine_smv, 0, data))

        if PJ[v] == -1:
            new_sv = 0
        else:
            new_sv = Graph.get_distance(new_graph, 0, PJ[v], data)
        new_tv = Graph.get_distance(new_graph, v, N, data)

        # get correct machine and positions to do FN2 by inserting v
        bestPop = {
            'objective': 2147483647,
            'machine': -1,
            'index': -1,
            'direction': 'backward'
        }
        for machine in data['machines'][factory][v]:
            if iter == 0:
                break

            if machine not in all_operations_of_machine:
                nowPop = {
                    'objective': objetives[1],
                    'machine': machine,
                    'index': -1,
                    'direction': 'all'
                }
            elif len(all_operations_of_machine[machine]) == 1:
                index_u = all_operations_of_machine[machine][0]
                node_u = indexes_to_nodes[index_u]
                job_u, operation_u = tools.get_job_operation(node_u, data)
                time_u = tools.get_time(job_u, operation_u, machine, factory, data)
                if job_u == job_v:
                    if operation_u > operation_v:
                        nowPop = {
                            'objective': objetives[1],
                            'machine': machine,
                            'index': index_u,
                            'direction': 'backward',
                        }
                    else:
                        nowPop = {
                            'objective': objetives[1],
                            'machine': machine,
                            'index': index_u,
                            'direction': 'forward',
                        }
                else:
                    if random.random() < 0.5:
                        nowPop = {
                            'objective': objetives[1],
                            'machine': machine,
                            'index': index_u,
                            'direction': 'backward',
                        }
                    else:
                        nowPop = {
                            'objective': objetives[1],
                            'machine': machine,
                            'index': index_u,
                            'direction': 'forward',
                        }
            else:
                low = 0
                high = len(all_operations_of_machine[machine])-1
                mid = -1
                while low <= high:
                    mid = (low + high) // 2
                    index_mid = all_operations_of_machine[machine][mid]
                    node_mid = indexes_to_nodes[index_mid]
                    job_mid, op_mid = tools.get_job_operation(node_mid, data)
                    time_mid = tools.get_time(job_mid, op_mid, machine, factory, data)
                    if new_tv > mksp - end_time_index[index_mid] + time_mid:
                        high = mid - 1
                    elif new_tv < mksp - end_time_index[index_mid] + time_mid:
                        low = mid + 1
                    else:
                        break
                if new_tv == mksp - end_time_index[index_mid] + time_mid:
                    L = mid - 1
                else:
                    L = mid

                low = 0
                high = len(all_operations_of_machine[machine])-1
                mid = -1
                while low <= high:
                    mid = (low + high) // 2
                    index_mid = all_operations_of_machine[machine][mid]
                    node_mid = indexes_to_nodes[index_mid]
                    job_mid, op_mid = tools.get_job_operation(node_mid, data)
                    time_mid = tools.get_time(job_mid, op_mid, machine, factory, data)
                    if new_sv < start_time_index[index_mid] + time_mid:
                        high = mid - 1
                    elif new_sv > start_time_index[index_mid] + time_mid:
                        low = mid + 1
                    else:
                        break
                if new_sv == start_time_index[index_mid] + time_mid:
                    R = mid + 1
                else:
                    R = mid
                if L == R:
                    continue
                if L < R:
                    L, R = R, L

                if machine in critical_path_machines:
                    last_critical = critical_path_machines[machine][0]
                    last_critical_index = all_operations_of_machine[machine].index(last_critical)
                else:
                    last_critical_index = -1
                vis = [False] * data['sum_operations']
                st_index_copy = np.copy(start_time_index)
                et_index_copy = np.copy(end_time_index)
                # 记忆化搜索：对每个有希望后移的工序搜索一遍
                if last_critical_index + 1 < len(all_operations_of_machine[machine]) and last_critical_index < L:
                    R = max(last_critical_index + 1, R)
                    w = all_operations_of_machine[machine][R]
                    if not vis[w]:
                        vis[w] = True
                        solveSchedule.delay_schedule(schedule, machines, factories, w, SJ_index, SM_index,
                                                     st_index_copy, et_index_copy, vis, critical_path, data)
                time_v_origin = tools.get_time(job_v, operation_v, machines[v - 1], 0, data)
                time_v_k = tools.get_time(job_v, operation_v, machine, factory, data)
                ind = -1
                obj = 2147483647
                if L == len(all_operations_of_machine[machine]):
                    L -= 1
                if L + 1 == len(all_operations_of_machine[machine]):
                    L -= 1
                for pos in range(R, L+2):
                    u = all_operations_of_machine[machine][pos]
                    if PM_index[u] == -1:
                        dettime = st_index_copy[u]
                    else:
                        dettime = st_index_copy[u] - end_time_index[PM_index[u]]
                    if (dettime >= time_v_k) or (time_v_origin + dettime >= data['MACHINES'] * (time_v_k - dettime)):
                        # 不能到SJ的后面去
                        if (SJ_index[index_v] == -1) or (end_time_index[index_v] + time_v_k <= st_index_copy[SJ_index[index_v]]):
                            now_obj = objetives[1] - (time_v_origin + dettime) + data['MACHINES'] * (time_v_k - dettime)
                            if now_obj < obj:
                                obj = now_obj
                                ind = pos
                nowPop = {
                    'objective': obj,
                    'machine': machine,
                    'index': all_operations_of_machine[machine][ind],
                    'direction': 'backward'
                }
            if nowPop['objective'] < bestPop['objective']:
                bestPop = nowPop
        new_machine = np.copy(machines)
        new_machine[v - 1] = bestPop['machine']
        if bestPop['index'] == index_v or bestPop['index'] == -1:
            continue
        # print(bestPop['objective'])
        node_best = indexes_to_nodes[bestPop['index']]
        j_b, o_b = tools.get_job_operation(node_best, data)
        if bestPop['direction'] == 'all':
            new_makespan = evalPop.evaluate_ind(schedule, new_machine, factories, data)
            new_schedule = schedule
        elif bestPop['direction'] == 'forward':
            new_schedule, new_makespan = solveSchedule.forward_schedule(schedule, new_machine, factories, PM_index,
                                                                         PJ_index, SM_index, SJ_index, index_v, bestPop['index'],
                                                                         data, factory=factory)
        else:
            new_schedule, new_makespan = solveSchedule.backward_schedule(schedule, new_machine, factories, PM_index,
                                                                         PJ_index, SM_index, SJ_index, bestPop['index'], index_v,
                                                                         data, factory=factory)
        new_schedule = np.reshape(new_schedule, (1, -1))
        newind_schedule = np.concatenate((newind_schedule, new_schedule), axis=0)
        newind_makespan = np.concatenate((newind_makespan, new_makespan))
        new_machine = np.reshape(new_machine, (1, -1))
        newind_machines = np.concatenate((newind_machines, new_machine), axis=0)
        iter -= 1

    if len(newind_schedule) < 1:
        return -1
    else:
        return newind_schedule, newind_machines, newind_makespan, iter