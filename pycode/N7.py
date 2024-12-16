import random

import numpy as np
import Graph
import solveSchedule
import tools
import copy

# random.seed(1)

def neighbor(schedule, machines, factories, data, iter):
    newind_schedule = np.empty((0, len(schedule)), dtype='int32')
    newind_makespan = np.empty((0, data['objective_number']+1), dtype='int32')

    for factory in range(data['FACTORIES']):
        if factory != 0:
            continue

        N = data['sum_operations'] + 1
        graph, PM, PJ, SM, SJ = Graph.init_graph(schedule, machines, factories, factory, data, True)

        # critical path
        critical_path, _ = Graph.get_distance(graph, 0, N, data, True)

        # delete the first and the last node
        critical_path = critical_path[1:-1]

        # devide critical path by machines
        critical_path_machines = Graph.get_path_machine(critical_path, machines, data)

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
        for i, node in enumerate(critical_path):
            critical_path[i] = nodes_to_indexes[node]
        for machine in critical_path_machines:
            for i, node in enumerate(critical_path_machines[machine]):
                critical_path_machines[machine][i] = nodes_to_indexes[node]
        for block in right_blocks:
            for i, node in enumerate(right_blocks[block]):
                right_blocks[block][i] = nodes_to_indexes[node]

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

        # check this condition
        forward = []
        backward = []
        for u in critical_path:
            node = indexes_to_nodes[u]
            job, operation = tools.get_job_operation(node, data)
            machine = tools.get_machine(job, operation, machines, data)
            if len(critical_path_machines[machine]) <= 1:
                continue
            if (u not in forward) and (SJ_index[u] in critical_path) and (u != critical_path_machines[machine][0]):
                forward.append(u)
            if (u not in backward) and (PJ_index[u] in critical_path) and (u != critical_path_machines[machine][-1]):
                backward.append(u)

        used = {}

        # start doing N6 -> N2
        for v in forward:
            if iter == 0:
                break
            node = indexes_to_nodes[v]
            job, operation = tools.get_job_operation(node, data)
            machine = tools.get_machine(job, operation, machines, data)
            cpm = np.array(critical_path_machines[machine])
            for u in cpm[cpm < v]:
                if iter == 0:
                    break
                trip = ("for", u, v)
                if trip not in used:
                    used[trip] = True
                    output = forward_interchange(v, u, schedule, machines, factories, indexes_to_nodes,
                                                 PM_index, PJ_index, SM_index, SJ_index, graph, data, PM, PJ, SM, SJ)
                    if output != -1:
                        new_schedule, new_makespan = output
                        if not np.any(np.all(newind_makespan == new_makespan, axis=1)):
                            newind_schedule = np.concatenate((newind_schedule, new_schedule), axis=0)
                            newind_makespan = np.concatenate((newind_makespan, new_makespan))
                            iter -= 1

                trip = ("back", u, v)
                if trip not in used:
                    used[trip] = True
                    output = backward_iterchange(u, v, schedule, machines, factories, indexes_to_nodes,
                                                 PM_index, PJ_index, SM_index, SJ_index, graph, data, PM, PJ, SM, SJ)
                    if output != -1:
                        new_schedule, new_makespan = output
                        if not np.any(np.all(newind_makespan == new_makespan, axis=1)):
                            newind_schedule = np.concatenate((newind_schedule, new_schedule), axis=0)
                            newind_makespan = np.concatenate((newind_makespan, new_makespan))
                            iter -= 1

        for u in backward:
            if iter == 0:
                break
            node = indexes_to_nodes[u]
            job, operation = tools.get_job_operation(node, data)
            machine = tools.get_machine(job, operation, machines, data)
            cpm = np.array(critical_path_machines[machine])
            for v in cpm[cpm > u]:
                if iter == 0:
                    break
                trip = ("back", u, v)
                if trip not in used:
                    used[trip] = True
                    output = backward_iterchange(u, v, schedule, machines, factories, indexes_to_nodes,
                                                 PM_index, PJ_index, SM_index, SJ_index, graph, data, PM, PJ, SM, SJ)
                    if output != -1:
                        new_schedule, new_makespan = output
                        if not np.any(np.all(newind_makespan == new_makespan, axis=1)):
                            newind_schedule = np.concatenate((newind_schedule, new_schedule), axis=0)
                            newind_makespan = np.concatenate((newind_makespan, new_makespan))
                            iter -= 1

                trip = ("for", u, v)
                if trip not in used:
                    used[trip] = True
                    output = forward_interchange(v, u, schedule, machines, factories, indexes_to_nodes,
                                                 PM_index, PJ_index, SM_index, SJ_index, graph, data, PM, PJ, SM, SJ)
                    if output != -1:
                        new_schedule, new_makespan = output
                        if not np.any(np.all(newind_makespan == new_makespan, axis=1)):
                            newind_schedule = np.concatenate((newind_schedule, new_schedule), axis=0)
                            newind_makespan = np.concatenate((newind_makespan, new_makespan))
                            iter -= 1

    if len(newind_schedule) < 1:
        return -1
    else:
        return newind_schedule, np.tile(machines, (len(newind_schedule), 1)), newind_makespan, iter

def forward_interchange(v, u, schedule, machines, factories, indexes_to_nodes, PM_index, PJ_index, SM_index, SJ_index, graph, data, PM, PJ, SM, SJ):
    node_u = indexes_to_nodes[u]
    node_v = indexes_to_nodes[v]
    job_u, operation_u = tools.get_job_operation(node_u, data)
    j_v, o_v = tools.get_job_operation(node_v, data)
    N = data['sum_operations'] + 1
    node_v = indexes_to_nodes[v]
    if SJ_index[u] == -1 or Graph.get_distance(graph, node_v, N, data) > Graph.get_distance(graph, indexes_to_nodes[SJ_index[u]], N, data):
        new_schedule, new_makespan = solveSchedule.forward_schedule(schedule, machines, factories, PM_index, PJ_index, SM_index, SJ_index, u, v, data)
        # print("u 移到 v 之后", job_u, '-', operation_u, ' , ', j_v, '-', o_v, ' , ', new_makespan)
        # tools.get_gantt(new_schedule, machines, factories, data)
        new_schedule = np.reshape(new_schedule, (1, -1))
        return new_schedule, new_makespan
    return -1


def backward_iterchange(u, v, schedule, machines, factories, indexes_to_nodes, PM_index, PJ_index, SM_index, SJ_index, graph, data, PM, PJ, SM, SJ):
    node_u = indexes_to_nodes[u]
    node_v = indexes_to_nodes[v]
    job_u, operation_u = tools.get_job_operation(node_u, data)
    j_v, o_v = tools.get_job_operation(node_v, data)
    N = data['sum_operations'] + 1
    node_u = indexes_to_nodes[u]
    job, operation = tools.get_job_operation(node_u, data)
    machine = tools.get_machine(job, operation, machines, data)
    if PJ_index[v] != -1:
        node_pj = indexes_to_nodes[PJ_index[v]]
        job_pj, operation_pj = tools.get_job_operation(node_pj, data)
        machine_pj = tools.get_machine(job_pj, operation_pj, machines, data)
    if PJ_index[v] == -1 or Graph.get_distance(graph, 0, indexes_to_nodes[u], data) + tools.get_time(job, operation, machine, 0, data) > Graph.get_distance(graph, 0, indexes_to_nodes[PJ_index[v]], data) + tools.get_time(job_pj, operation_pj, machine_pj, 0, data):
        new_schedule, new_makespan = solveSchedule.backward_schedule(schedule, machines, factories, PM_index, PJ_index, SM_index, SJ_index, u, v, data)
        # print("v 移到 u 之前", job_u, '-', operation_u, ' , ', j_v, '-', o_v, ' , ', new_makespan)
        # tools.get_gantt(new_schedule, machines, factories, data)
        new_schedule = np.reshape(new_schedule, (1, -1))
        return new_schedule, new_makespan
    return -1