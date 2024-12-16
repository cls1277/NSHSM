# Date: 2024/1/14 21:13
# Author: cls1277
# Email: cls1277@163.com

import copy
import random
import numpy as np
import tools
import Graph
import solveSchedule
import evalPop

def swap_all(schedule, factories, data):
    new_schedule = copy.deepcopy(schedule)
    key = random.randint(0, data['FACTORIES']-1)
    indices = np.where(factories == key)[0]
    if len(indices) < 2:
        return -1
    selected_indices = np.random.choice(indices, size=2, replace=True)
    job1, job2 = selected_indices[0], selected_indices[1]
    if job1 != job2:
        op1 = random.randint(0, data['operations'][job1]-1)
        op2 = random.randint(0, data['operations'][job2]-1)
    else:
        random_numbers = random.sample(range(data['operations'][job1]), 2)
        op1, op2 = random_numbers[0], random_numbers[1]
    node1 = tools.get_node(job1, op1, data)
    node2 = tools.get_node(job2, op2, data)
    index1 = tools.get_node_to_index(node1, schedule, data)
    index2 = tools.get_node_to_index(node2, schedule, data)
    new_schedule[index1], new_schedule[index2] = new_schedule[index2], new_schedule[index1]
    new_schedule = np.reshape(new_schedule, (1, -1))
    return new_schedule

def swap_key(schedule, factories, data, key):
    key = int(key)
    new_schedule = copy.deepcopy(schedule)
    indices = np.where(factories == key)[0]
    if len(indices) < 2:
        return -1
    selected_indices = np.random.choice(indices, size=2, replace=True)
    job1, job2 = selected_indices[0], selected_indices[1]
    if job1 != job2:
        op1 = random.randint(0, data['operations'][job1]-1)
        op2 = random.randint(0, data['operations'][job2]-1)
    else:
        random_numbers = random.sample(range(data['operations'][job1]), 2)
        op1, op2 = random_numbers[0], random_numbers[1]
    node1 = tools.get_node(job1, op1, data)
    node2 = tools.get_node(job2, op2, data)
    index1 = tools.get_node_to_index(node1, schedule, data)
    index2 = tools.get_node_to_index(node2, schedule, data)
    new_schedule[index1], new_schedule[index2] = new_schedule[index2], new_schedule[index1]
    new_schedule = np.reshape(new_schedule, (1, -1))
    return new_schedule

def insert_all(schedule, machines, factories, data):
    N = data['sum_operations'] + 1
    key = random.randint(0, data['FACTORIES']-1)
    indices = np.where(factories == key)[0]
    if len(indices) < 2:
        return -1

    graph, PM, PJ, SM, SJ = Graph.init_graph(schedule, machines, factories, key, data)
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

    selected_indices = np.random.choice(indices, size=2, replace=True)
    job1, job2 = selected_indices[0], selected_indices[1]
    if job1 != job2:
        op1 = random.randint(0, data['operations'][job1]-1)
        op2 = random.randint(0, data['operations'][job2]-1)
    else:
        random_numbers = random.sample(range(data['operations'][job1]), 2)
        op1, op2 = random_numbers[0], random_numbers[1]
    node1 = tools.get_node(job1, op1, data)
    node2 = tools.get_node(job2, op2, data)
    index1 = tools.get_node_to_index(node1, schedule, data)
    index2 = tools.get_node_to_index(node2, schedule, data)
    if index1 > index2:
        index1, index2 = index2, index1
    new_schedule = solveSchedule.backward_schedule(schedule, machines, factories, PM_index,
                                                                 PJ_index, SM_index, SJ_index, index1, index2,
                                                                 data, eval = False)

    new_schedule = np.reshape(new_schedule, (1, -1))
    return new_schedule

def insert_key(schedule, machines, factories, data, key):
    key = int(key)
    N = data['sum_operations'] + 1
    indices = np.where(factories == key)[0]
    if len(indices) < 2:
        return -1

    graph, PM, PJ, SM, SJ = Graph.init_graph(schedule, machines, factories, key, data)
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

    selected_indices = np.random.choice(indices, size=2, replace=True)
    job1, job2 = selected_indices[0], selected_indices[1]
    if job1 != job2:
        op1 = random.randint(0, data['operations'][job1]-1)
        op2 = random.randint(0, data['operations'][job2]-1)
    else:
        random_numbers = random.sample(range(data['operations'][job1]), 2)
        op1, op2 = random_numbers[0], random_numbers[1]
    node1 = tools.get_node(job1, op1, data)
    node2 = tools.get_node(job2, op2, data)
    index1 = tools.get_node_to_index(node1, schedule, data)
    index2 = tools.get_node_to_index(node2, schedule, data)
    if index1 > index2:
        index1, index2 = index2, index1
    new_schedule = solveSchedule.backward_schedule(schedule, machines, factories, PM_index,
                                                                 PJ_index, SM_index, SJ_index, index1, index2,
                                                                 data, eval = False)

    new_schedule = np.reshape(new_schedule, (1, -1))
    return new_schedule

def machine_all(schedule, machines, factories, data, key):
    key = int(key)
    N = data['sum_operations'] + 1
    graph, PM, PJ, SM, SJ = Graph.init_graph(schedule, machines, factories, key, data)

    # critical path
    critical_path, mksp = Graph.get_distance(graph, 0, N, data, True)

    # delete the first and the last node
    critical_path = critical_path[1:-1]

    node = random.choice(critical_path)
    new_m = np.random.choice(np.setdiff1d(data['machines'][key][node], machines[node-1]), size=1)[0]
    new_machines = copy.deepcopy(machines)
    new_machines[node-1]= new_m
    new_machines = np.reshape(new_machines, (1, -1))
    return new_machines

def machine_roule(schedule, machines, factories, data, key):
    key = int(key)
    N = data['sum_operations'] + 1
    graph, PM, PJ, SM, SJ = Graph.init_graph(schedule, machines, factories, key, data)

    # critical path
    critical_path, mksp = Graph.get_distance(graph, 0, N, data, True)

    # delete the first and the last node
    critical_path = critical_path[1:-1]

    node = random.choice(critical_path)
    total_weight = sum(data['times'][key][node])
    relative_weights = np.array(data['times'][key][node]) / total_weight
    selected_index = np.random.choice(len(data['times'][key][node]), p=relative_weights)

    new_m = data['machines'][key][node][selected_index]
    new_machines = copy.deepcopy(machines)
    new_machines[node-1] = new_m
    new_machines = np.reshape(new_machines, (1, -1))
    return new_machines