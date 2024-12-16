import copy
import numpy as np
import random
import Graph
import solveSchedule
import tools

# random.seed(1)

def neighbor(schedule, machines, factories, data, iter):
    newind_schedule = np.empty((0, len(schedule)), dtype='int32')
    newind_makespan = np.empty((0, data['objective_number']+1), dtype='int32')

    for factory in range(data['FACTORIES']):
        if factory != 0:
            continue

        N = data['sum_operations'] + 1
        graph, PM, PJ, SM, SJ = Graph.init_graph(schedule, machines, factories, factory, data, True)

        # critical path and end time
        critical_path, _ = Graph.get_distance(graph, 0, N, data, True)

        # delete the first and the last node
        critical_path = critical_path[1:-1]

        # critical blocks
        critical_blocks = Graph.get_path_blocks(critical_path, machines, data)

        # from there start, schedule vector will be used, so mapping from nodes to vector index
        # there is no Graph next
        nodes_to_indexes = tools.get_nodes_to_indexes(schedule, data)
        indexes_to_nodes = tools.get_indexes_to_nodes(schedule, data)

        # start_times and end_time : nodes -> indexes
        # start_time_nodes, end_time_nodes = tools.get_start_end_time(schedule, machines, data)

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

        for i, node in enumerate(critical_path):
            critical_path[i] = nodes_to_indexes[node]
        for block in critical_blocks:
            for i, node in enumerate(critical_blocks[block]):
                critical_blocks[block][i] = nodes_to_indexes[node]

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

        # first operation: backward
        # other operations: backward or forward
        # last operation: forward

        # satisfy N8 condition
        start_times = {}
        for index, st in enumerate(start_time_index):
            if factories[schedule[index]] != factory:
                continue
            if st not in start_times:
                start_times[st] = []
            start_times[st].append(index)

        critical_operation_same_start_times = {}
        same_start_times = {}
        for st in start_times.keys():
            if len(start_times[st]) > 1:
                critical_operations = tools.get_list_in_critical_path(start_times[st], critical_path)
                if len(critical_operations) > 0:
                    critical_operation_same_start_times[st] = copy.deepcopy(critical_operations)
                    same_start_times[st] = start_times[st]
        if len(same_start_times) == 0 or iter == 0:
            return newind_schedule, np.tile(machines, (len(newind_schedule), 1)), newind_makespan, iter

        # for st in same_start_times.keys():
        st = random.choice(list(same_start_times.keys()))
        if iter == 0:
            break
        u = random.choice(critical_operation_same_start_times[st])
    # for u in critical_operation_same_start_times[st]:
        if iter == 0:
            break
        flag = tools.get_operation_in_blocks(u, critical_blocks)
        if flag == -1:
            new_s = N8_backward_schedule(schedule, machines, factories, u, PM_index, PJ_index, SM_index, SJ_index, indexes_to_nodes,
                                     start_time_index, end_time_index, critical_path, operations_machines, data, iter)
            if new_s != None:
                new_schedule, new_makespan, iter = new_s
                newind_schedule = np.concatenate((newind_schedule, new_schedule), axis=0)
                newind_makespan = np.concatenate((newind_makespan, new_makespan))
        elif flag == 1:
            new_s = N8_forward_schedule(schedule, machines, factories, u, PM_index, PJ_index, SM_index, SJ_index, indexes_to_nodes, start_time_index,
                                    end_time_index, critical_path, operations_machines, data, iter)
            if new_s != None:
                new_schedule, new_makespan, iter = new_s
                newind_schedule = np.concatenate((newind_schedule, new_schedule), axis=0)
                newind_makespan = np.concatenate((newind_makespan, new_makespan))
        else :
            new_s = N8_backward_schedule(schedule, machines, factories, u, PM_index, PJ_index, SM_index, SJ_index, indexes_to_nodes,
                                     start_time_index, end_time_index, critical_path, operations_machines, data, iter)
            if new_s != None:
                new_schedule, new_makespan, iter = new_s
                newind_schedule = np.concatenate((newind_schedule, new_schedule), axis=0)
                newind_makespan = np.concatenate((newind_makespan, new_makespan))

            if iter > 0:
                new_s = N8_forward_schedule(schedule, machines, factories, u, PM_index, PJ_index, SM_index, SJ_index, indexes_to_nodes,
                                            start_time_index,
                                            end_time_index, critical_path, operations_machines, data, iter)
                if new_s != None:
                    new_schedule, new_makespan, iter = new_s
                    newind_schedule = np.concatenate((newind_schedule, new_schedule), axis=0)
                    newind_makespan = np.concatenate((newind_makespan, new_makespan))

    if len(newind_schedule) < 1:
        return -1
    else:
        return newind_schedule, np.tile(machines, (len(newind_schedule), 1)), newind_makespan, iter

def N8_backward_schedule(schedule, machines, factories, u, PM_index, PJ_index, SM_index, SJ_index, indexes_to_nodes, start_time_index, end_time_index, critical_path, operations_machines, data, iter):
    newind_schedule = np.empty((0, len(schedule)), dtype='int32')
    newind_makespan = np.empty((0, data['objective_number']+1), dtype='int32')

    job_u, operation_u = tools.get_job_operation(indexes_to_nodes[u], data)
    mu = tools.get_machine(job_u, operation_u, machines, data)
    time_u = tools.get_time(job_u, operation_u, mu, 0, data)

    vis = [False] * data['sum_operations']
    st_index_copy = np.copy(start_time_index)
    et_index_copy = np.copy(end_time_index)
    vis[u] = True
    solveSchedule.delay_schedule(schedule, machines, factories, u, SJ_index, SM_index, st_index_copy, et_index_copy, vis, critical_path, data)
    u_index = operations_machines[mu].index(u)
    for v_index in range(u_index+1, len(operations_machines[mu])):
        if iter == 0:
            break
        v = operations_machines[mu][v_index]
        node_v = indexes_to_nodes[v]
        j_v, o_v = tools.get_job_operation(node_v, data)
        if v in critical_path:
            continue
        # u 插到 v 的前面
        dettime = st_index_copy[v] - end_time_index[PM_index[v]]
        # 简化前条件：if (dettime >= time_u) or (dettime >= 1 * (time_u - dettime)):
        if 2 * dettime >= time_u:
            # 不能到SJ的后面去
            if (SJ_index[u]== -1) or (end_time_index[v] + time_u <= st_index_copy[SJ_index[u]]):
                print("u 插到 v 的前面", job_u, '-', operation_u, ' , ', j_v, '-', o_v)
                new_schedule, new_makespan = solveSchedule.backward_schedule(schedule, machines, factories, PM_index, PJ_index, SM_index, SJ_index, v, u, data)
                new_schedule = np.reshape(new_schedule, (1, -1))
                newind_schedule = np.concatenate((newind_schedule, new_schedule), axis=0)
                newind_makespan = np.concatenate((newind_makespan, new_makespan))
                iter -= 1

    if len(newind_schedule) < 1:
        return None
    else:
        return newind_schedule, newind_makespan, iter


def N8_forward_schedule(schedule, machines, factories, u, PM_index, PJ_index, SM_index, SJ_index, indexes_to_nodes, start_time_index, end_time_index, critical_path, operations_machines, data, iter):
    newind_schedule = np.empty((0, len(schedule)), dtype='int32')
    newind_makespan = np.empty((0, data['objective_number']+1), dtype='int32')

    job_u, operation_u = tools.get_job_operation(indexes_to_nodes[u], data)
    mu = tools.get_machine(job_u, operation_u, machines, data)
    time_u = tools.get_time(job_u, operation_u, mu, 0, data)

    vis = [False] * data['sum_operations']
    st_index_copy = np.copy(start_time_index)
    et_index_copy = np.copy(end_time_index)
    for machine in operations_machines:
        w = operations_machines[machine][0]
        if w in critical_path:
            continue
        # 记忆化搜索：对每个有希望后移的工序搜索一遍
        if not vis[w]:
            vis[w] = True
            solveSchedule.delay_schedule(schedule, machines, factories, w, SJ_index, SM_index, st_index_copy, et_index_copy, vis, critical_path, data)

    u_index = operations_machines[mu].index(u)
    for v_index in range(0, u_index):
        if iter == 0:
            break
        v = operations_machines[mu][v_index]
        if v in critical_path:
            continue
        node_v = indexes_to_nodes[v]
        j_v, o_v = tools.get_job_operation(node_v, data)
        # u 插到 v 的后面
        dettime = st_index_copy[SM_index[v]] - end_time_index[v]
        # 简化前条件：if (dettime >= time_u) or (dettime >= 1 * (time_u - dettime)):
        if 2 * dettime >= time_u:
            # 不能到PJ的前面去
            if (PJ_index[u]== -1) or (et_index_copy[v] >= end_time_index[PJ_index[u]]):
                print("u 插到 v 的后面", job_u, '-', operation_u, ' , ', j_v, '-', o_v)
                new_schedule, new_makespan = solveSchedule.forward_schedule(schedule, machines, factories, PM_index, PJ_index, SM_index, SJ_index, u, v, data)
                new_schedule = np.reshape(new_schedule, (1, -1))
                newind_schedule = np.concatenate((newind_schedule, new_schedule), axis=0)
                newind_makespan = np.concatenate((newind_makespan, new_makespan))
                iter -= 1

    if len(newind_schedule) < 1:
        return None
    else:
        return newind_schedule, newind_makespan, iter