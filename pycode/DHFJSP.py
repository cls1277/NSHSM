# Date: 2023/12/17 18:23
# Author: cls1277
# Email: cls1277@163.com

import random
import numpy as np
import tools
import N7
import N8
import Ntec1
import crossover
import mutation
import Nopt1
import Ntec2
import Ntec3
import Nrand
import Nall

def ROS(data):
    schedule = np.zeros(data['sum_operations'], dtype='int32')
    jobs = list(range(data['JOBS']))
    operation = [0] * data['JOBS']
    for j in range(data['sum_operations']):
        job = random.choice(jobs)
        operation[job] += 1
        schedule[j] = job
        if operation[job] == data['operations'][job]:
            jobs.remove(job)
    return schedule

# random machines sequence
def RMS(factory, data):
    machine = np.zeros(data['sum_operations'], dtype='int32')
    for i in range(data['sum_operations']):
        job, _ = tools.get_job_operation(i+1, data)
        machine[i] = random.choice(data['machines'][factory[job]][i+1])
    return machine

# heuristic machines sequence
def HMS_global(factory, data):
    machine = np.zeros(data['sum_operations'], dtype='int32')
    time_machines = np.zeros((data['FACTORIES'], data['MACHINES']), dtype='int32')
    for i in range(data['sum_operations']):
        node = i+1
        job, operation = tools.get_job_operation(node, data)
        f = factory[job]
        time_min = 2147483647
        machine_min = -1
        for m in data['machines'][f][node]:
            time_node = tools.get_time(job, operation, m, f, data) + time_machines[f][m]
            if time_min > time_node:
                time_min = time_node
                machine_min = m
        machine[i] = machine_min
        time_machines[f][machine_min] += time_min
    return machine

# heuristic machines sequence
def HMS_local(factory, data):
    machine = np.zeros(data['sum_operations'], dtype='int32')
    time_machines = np.zeros((data['FACTORIES'], data['MACHINES']), dtype='int32')
    for i in range(data['sum_operations']):
        node = i+1
        job, operation = tools.get_job_operation(node, data)
        if operation == 0:
            time_machines = np.zeros((data['FACTORIES'], data['MACHINES']), dtype='int32')
        f = factory[job]
        time_min = 2147483647
        machine_min = -1
        for m in data['machines'][f][node]:
            time_node = tools.get_time(job, operation, m, f, data)
            if time_min > time_node:
                time_min = time_node
                machine_min = m
        machine[i] = machine_min
        time_machines[f][machine_min] += time_min
    return machine


def RFS(data):
    factory = np.zeros(data['JOBS'], dtype='int32')
    for job in range(data['JOBS']):
        factory[job] = random.randint(0, data['FACTORIES'] - 1)
    return factory

# heuristic factory sequence
def HFS_global(data):
    factory = np.zeros(data['JOBS'], dtype='int32')
    time_all = np.zeros(data['FACTORIES'], dtype='int32')
    for job in range(data['JOBS']):
        # time_factory = np.zeros(data['FACTORIES'], dtype='int32')
        time_factory = np.copy(time_all)
        for f in range(data['FACTORIES']):
            for operation in range(data['operations'][job]):
                node = tools.get_node(job, operation, data)
                time_min = 2147483647
                for machine in data['machines'][f][node]:
                    time_node = tools.get_time(job, operation, machine, f, data)
                    time_min = min(time_min, time_node)
                time_factory[f] += time_min
        factory[job] = np.argmin(time_factory)
        time_all[factory[job]] += np.min(time_factory)
    return factory

# heuristic factory sequence
def HFS_local(data):
    factory = np.zeros(data['JOBS'], dtype='int32')
    for job in range(data['JOBS']):
        time_factory = np.zeros(data['FACTORIES'], dtype='int32')
        for f in range(data['FACTORIES']):
            for operation in range(data['operations'][job]):
                node = tools.get_node(job, operation, data)
                time_min = 2147483647
                for machine in data['machines'][f][node]:
                    time_node = tools.get_time(job, operation, machine, f, data)
                    time_min = min(time_min, time_node)
                time_factory[f] += time_min
        factory[job] = np.argmin(time_factory)
    return factory

def read_data(setting, data):
    operations = []
    row = 0
    while data[row][0] == 1:
        operations.append(data[row][2])
        row += data[row][2] + 1
    setting['operations'] = operations
    setting['sum_operations'] = sum(operations)
    setting['machines'] = []
    setting['times'] = []
    row = 1
    for factory in range(setting['FACTORIES']):
        machines = {}
        times = {}
        node = 0
        for job in range(setting['JOBS']):
            for operation in range(operations[job]):
                node += 1
                machines[node] = []
                times[node] = []
                count = data[row][1]
                for i in range(count):
                    machines[node].append(data[row][(i+1)*2]-1)
                    times[node].append(data[row][(i+1)*2+1])
                row += 1
            row += 1
        setting['machines'].append(machines)
        setting['times'].append(times)

def neighbor(schedule, machines, factories, objetives, key, data, iter, NS):
    if NS == 'N7':
        return N7.neighbor(schedule, machines, factories, data, iter)
    elif NS == 'N8':
        return N8.neighbor(schedule, machines, factories, data, iter)
    elif NS == 'Nopt1':
        return Nopt1.neighbor(schedule, machines, factories, key, data, iter)
    elif NS == 'Ntec1':
        return Ntec1.neighbor(schedule, machines, factories, data, iter)
    elif NS == 'Ntec2':
        return Ntec2.neighbor(schedule, machines, factories, data, iter)
    elif NS == 'Ntec3':
        return Ntec3.neighbor(schedule, machines, factories, objetives, key, data, iter)
    elif NS == 'Nall':
        return Nall.neighbor(schedule, machines, factories, objetives, key, data, iter)
    elif NS == 'RAND':
        rd = random.randint(1, 2)
        if rd == 1:
            return Nopt1.neighbor(schedule, machines, factories, key, data, iter)
        elif rd == 2:
            return Ntec3.neighbor(schedule, machines, factories, objetives, key, data, iter)
    else:
        print("Please select the correct neighborhood structure!")

def cross_over(f1, f2, data, iter):
    new_schedule = crossover.POX(f1['schedules'], f2['schedules'], data)
    new_factory = crossover.UX(f1['factories'], f2['factories'])
    new_machine = crossover.UX(f1['machines'], f2['machines'])
    # new_objective = np.empty((0, data['objective_number']), dtype='int32')
    for i in range(len(new_schedule)):
        for j in range(data['sum_operations']):
            node = j+1
            job, _ = tools.get_job_operation(node, data)
            f = new_factory[i][job]
            if new_machine[i][j] not in data['machines'][f][node]:
                new_machine[i][j] = random.choice(data['machines'][f][node])
        # output = evalPop.evaluate_ind(new_schedule[i], new_machine[i], new_factory[i], data)
        # new_objective = np.concatenate((new_objective, output))
        # iter -= 1
        # if iter == 0:
        #     break
    return new_schedule, new_machine, new_factory, iter

def mu_tation(f, data):
    schedule = f['schedules']
    machines = f['machines']
    factories = f['factories']
    key = f['key']
    rd = random.randint(1, 5)
    if rd == 1:
        new_schedule = Nrand.swap_all(schedule, factories, data)
    elif rd == 2:
        new_schedule = Nrand.swap_key(schedule, factories, data, key)
    elif rd == 3:
        new_schedule = Nrand.insert_all(schedule, machines, factories, data)
    elif rd == 4:
        new_schedule = Nrand.insert_key(schedule, machines, factories, data, key)
    else:
        new_schedule = schedule

    rd = random.randint(1, 3)
    if rd == 1:
        new_machines = Nrand.machine_all(schedule, machines, factories, data, key)
    elif rd == 2:
        new_machines = Nrand.machine_roule(schedule, machines, factories, data, key)
    else:
        new_machines = machines

    rd = random.randint(1, 2)
    if rd == 1:
        new_factory = mutation.MuFS(f['factories'], data)
    else:
        new_factory = factories

    return new_schedule, new_machines, new_factory