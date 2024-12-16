# Date: 2023/12/22 21:54
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

def neighbor(schedule, machines, factories, key, data, iter):
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

            time_v = tools.get_time(job_v, operation_v, machine, factory, data)

            if machine not in all_operations_of_machine:
                nowPop = {
                    'objective': time_v + new_sv + new_tv,
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
                            'objective': time_v + new_sv + time_u + mksp - end_time_index[index_u],
                            'machine': machine,
                            'index': index_u,
                            'direction': 'backward',
                        }
                    else:
                        nowPop = {
                            'objective': time_v + new_tv + time_u + mksp - end_time_index[index_u],
                            'machine': machine,
                            'index': index_u,
                            'direction': 'forward',
                        }
                else:
                    if random.random() < 0.5:
                        nowPop = {
                            'objective': time_v + new_sv + time_u + mksp - end_time_index[index_u],
                            'machine': machine,
                            'index': index_u,
                            'direction': 'backward',
                        }
                    else:
                        nowPop = {
                            'objective': time_v + new_tv + time_u + mksp - end_time_index[index_u],
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

                flag = 0
                if L < R:
                    ind = L
                    obj = mksp
                else:
                    # if machine == machines[v - 1]:
                    #     # before pi(1)
                    #     ind = R
                    #     flag = 0
                    #     index_r = all_operations_of_machine[machine][ind]
                    #     if PJ_index[index_r] == -1:
                    #         et = 0
                    #     else:
                    #         et = max(new_sv + time_v, end_time_index[PJ_index[index_r]]) - (new_sv + time_v)
                    #     obj = new_sv + time_v + et + mksp - start_time_index[index_r]
                    #
                    #     # after pi(1) ... pi(l)
                    #     for pos in range(R, L+1):
                    #         index_pos = all_operations_of_machine[machine][pos]
                    #         if PJ_index[index_v] == -1:
                    #             st = 0
                    #         else:
                    #             st = max(end_time_index[PJ_index[index_v]], end_time_index[index_pos]) - end_time_index[index_pos]
                    #         now_obj = end_time_index[index_pos] + st + time_v
                    #         mx = 0
                    #         for pre in range(pos+1, len(all_operations_of_machine[machine])):
                    #             index_pre = all_operations_of_machine[machine][pre]
                    #             mx = max(mx, mksp - start_time_index[index_pre])
                    #         now_obj += mx
                    #         if now_obj < obj:
                    #             ind = pos # after pi(i)
                    #             obj = now_obj
                    #             if ind == R:
                    #                 flag = 1
                    # else:
                    # pi(0)
                    ind = R # before pi(1)
                    index_r = all_operations_of_machine[machine][ind]
                    node_r = indexes_to_nodes[index_r]
                    job_r, op_r = tools.get_job_operation(node_r, data)
                    time_r = tools.get_time(job_r, op_r, machine, factory, data)
                    if PJ_index[index_r] == -1:
                        et = 0
                    else:
                        et = max(new_sv + time_v, end_time_index[PJ_index[index_r]]) - (new_sv + time_v)
                    obj = new_sv + time_v + et + mksp - start_time_index[index_r]
                    flag = 0 # check before or after R

                    # 1 ~ l-1
                    for pos in range(R, L): # from R to L-1
                        index_pre = all_operations_of_machine[machine][pos+1]
                        node_pre = indexes_to_nodes[index_pre]
                        job_pre, op_pre = tools.get_job_operation(node_pre, data)
                        time_pre = tools.get_time(job_pre, op_pre, machine, factory, data)

                        index_pos = all_operations_of_machine[machine][pos]
                        node_pos = indexes_to_nodes[index_pos]
                        job_pos, op_pos = tools.get_job_operation(node_pos, data)
                        time_pos = tools.get_time(job_pos, op_pos, machine, factory, data)
                        if PJ_index[index_v] == -1:
                            st = 0
                        else:
                            st = max(end_time_index[PJ_index[index_v]], end_time_index[index_pos]) - end_time_index[index_pos]
                        if PJ_index[index_pre] == -1:
                            et = 0
                        else:
                            et = max(end_time_index[index_pos] + st + time_v, end_time_index[PJ_index[index_pre]]) - (end_time_index[index_pos] + st + time_v)
                        now_obj = end_time_index[index_pos] + st + time_v + et + mksp - start_time_index[index_pre]
                        if now_obj < obj:
                            ind = pos # after pi(i)
                            obj = now_obj
                            if ind == R:
                                flag = 1

                    # pi(l)
                    index_l = all_operations_of_machine[machine][L]
                    node_l = indexes_to_nodes[index_l]
                    job_l, op_l = tools.get_job_operation(node_l, data)
                    time_l = tools.get_time(job_l, op_l, machine, factory, data)
                    if PJ_index[index_v] == -1:
                        st = 0
                    else:
                        st = max(end_time_index[PJ_index[index_v]], end_time_index[index_l]) - end_time_index[index_l]
                    now_obj = start_time_index[index_l] + time_l + st + time_v + new_tv
                    if now_obj < obj:
                        ind = L  # after pi(l)
                        obj = now_obj

                if ind == R and flag == 0:
                    nowPop = {
                        'objective': obj,
                        'machine': machine,
                        'index': all_operations_of_machine[machine][ind],
                        'direction': 'backward'
                    }
                else:
                    nowPop = {
                        'objective': obj,
                        'machine': machine,
                        'index': all_operations_of_machine[machine][ind],
                        'direction': 'forward'
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
                                                                         data)
        else:
            new_schedule, new_makespan = solveSchedule.backward_schedule(schedule, new_machine, factories, PM_index,
                                                                         PJ_index, SM_index, SJ_index, bestPop['index'], index_v,
                                                                         data)
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