# Date: 2023/12/30 21:52
# Author: cls1277
# Email: cls1277@163.com
import random

import tools
import numpy as np
import Graph
import fullActive
import evalPop

def full_active(pop, length, data, iter):
    # EnergysavingDHFJSP(p_chrom, m_chrom, f_chrom, fitness, N, H, TM, time, SH, F)
    N = data['JOBS']
    F = data['FACTORIES']
    TM = data['MACHINES']
    SH = data['sum_operations']
    H = data['operations']
    time = np.zeros(shape=(F,N, int(max(H)), TM))
    for f in range(F):
        for j in range(N):
            for o in range(int(H[j])):
                node = tools.get_node(j, o, data)
                for index, m in enumerate(data['machines'][f][node]):
                    time[f][j][o][m] = data['times'][f][node][index]
    for i in range(length):
        p_chrom = pop['schedules'][i]
        m_chrom = pop['machines'][i]
        f_chrom = pop['factories'][i]
        fitness = pop[data['objective']][i]
        newp, newm, newf = fullActive.EnergysavingDHFJSP(p_chrom, m_chrom, f_chrom, fitness, N, H, TM, time, SH, F)
        obj_key = evalPop.evaluate_ind(newp, newm, newf, data)
        f1 = {
            'schedules': newp,
            'machines': newm,
            'factories': newf,
            data['objective']: obj_key[:, 0:2],
            'key': obj_key[0, 2]
        }
        nds = tools.nds(pop[data['objective']][i], f1[data['objective']][0], data)
        iter -= 1
        if nds == 2 or (nds == 0 and random.random() <= 0.5):
            pop['schedules'][i] = newp
            pop['machines'][i] = newm
            pop['factories'][i] = newf
            pop[data['objective']][i] = f1[data['objective']]
    return pop, iter

def delay(schedule, machines, factories, data, P = (4,1)):
    p = np.empty((2, 1))
    p[0, 0], p[1, 0] = P
    t = np.zeros((1, 2))
    for factory in range(data['FACTORIES']):
        N = data['sum_operations'] + 1
        graph, PM, PJ, SM, SJ = Graph.init_graph(schedule, machines, factories, factory, data, True)

        # critical path and end time
        critical_path, _ = Graph.get_distance(graph, 0, N, data, True)

        # delete the first and the last node
        critical_path = critical_path[1:-1]

        # critical blocks
        critical_blocks = Graph.get_path_blocks(critical_path, machines, data)

        # right blocks: they can do N4 neighborhood structure
        count_right_blocks = 0
        right_blocks = {}

        for i, block in enumerate(critical_blocks):
            if len(critical_blocks[block]) > 1:
                count_right_blocks += 1
                right_blocks[count_right_blocks] = copy.deepcopy(critical_blocks[block])

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

        vis = [False] * data['sum_operations']
        st_index_copy = np.copy(start_time_index)
        et_index_copy = np.copy(end_time_index)
        for machine in range(data['MACHINES']):
            w = operations_machines[machine][0]
            if w in critical_path:
                continue
            # 记忆化搜索：对每个有希望后移的工序搜索一遍
            if not vis[w]:
                vis[w] = True
                delay_schedule(schedule, machines, factories, w, SJ_index, SM_index, st_index_copy, et_index_copy, vis, critical_path, data)
        for machine in range(data['MACHINES']):
            for index in operations_machines[machine]:
                t[0,0] += et_index_copy[index] - st_index_copy[index]
                if PM_index[index] != -1:
                    t[0,1] += st_index_copy[index] - et_index_copy[PM_index[index]]

    return np.dot(t, p)[0,0]


def delay_schedule(schedule, machines, factories, u, SJ_index, SM_index, st_index, et_index, vis, critical_path, data):
    if (SJ_index[u] != -1) and (vis[SJ_index[u]] == False) and (SJ_index[u] not in critical_path):
        vis[SJ_index[u]] = True
        delay_schedule(schedule, machines, factories, SJ_index[u], SJ_index, SM_index, st_index, et_index, vis, critical_path, data)
        et_index[u] = max(et_index[u], st_index[SJ_index[u]])
    if (SM_index[u] != -1) and (vis[SM_index[u]] == False) and (SM_index[u] not in critical_path):
        vis[SM_index[u]] = True
        delay_schedule(schedule, machines, factories, SM_index[u], SJ_index, SM_index, st_index, et_index, vis, critical_path, data)
        et_index[u] = max(et_index[u], st_index[SM_index[u]])
    if (SJ_index[u] == -1) and (SM_index[u] == -1):
        # makespan
        et_index[u] = et_index[critical_path[-1]]
    node = tools.get_index_to_node(u, schedule, data)
    job_u, operation_u = tools.get_job_operation(node, data)
    st_index[u] = et_index[u] - tools.get_time(job_u, operation_u, machines[node-1], factories[job_u], data)