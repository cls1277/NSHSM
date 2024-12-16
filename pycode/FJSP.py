# Date: 2023/12/17 18:23
# Author: cls1277
# Email: cls1277@163.com

import random
import numpy as np
import tools
import N7
import N8
import Ntec1
import Nopt1
import Ntec2

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
def RMS(data):
    machine = np.zeros(data['sum_operations'], dtype='int32')
    index = 0
    for job in range(data['JOBS']):
        for operation in range(data['operations'][job]):
            node = tools.get_node(job, operation, data)
            machine[index] = random.choice(data['machines'][0][node])
            index += 1
    return machine

def read_data(setting, data):
    operations = [row[0] for row in data]
    setting['operations'] = operations
    setting['sum_operations'] = sum(operations)
    machines = {}
    times = {}
    node = 0
    for job in range(setting['JOBS']):
        ind = 1
        for operation in range(operations[job]):
            node += 1
            machines[node] = []
            times[node] = []
            # count of optional machines
            count = data[job][ind]
            for i in range(count):
                machines[node].append(data[job][ind + 2 * i + 1] - 1)
                times[node].append(data[job][ind + 2 * i + 2])
            ind += 2 * count + 1
    setting['machines'] = [machines]
    setting['times'] = [times]

def neighbor(schedule, machines, factories, data, iter, NS):
    # if NS == 'Nopt1':
    #     return Nopt1.neighbor(schedule, machines, factories, data, iter)
    # elif NS == 'Nopt2':
    #     return Nopt2.neighbor(schedule, machines, factories, data, iter)
    # else:
    #     print("Please select the correct neighborhood structure!")
    if NS == 'N4':
        return N4.neighbor(schedule, machines, factories, data, iter)
    elif NS == 'N5':
        return N5.neighbor(schedule, machines, factories, data, iter)
    elif NS == 'N6':
        return N6.neighbor(schedule, machines, factories, data, iter)
    elif NS == 'N7':
        return N7.neighbor(schedule, machines, factories, data, iter)
    elif NS == 'N8':
        return N8.neighbor(schedule, machines, factories, data, iter)
    elif NS == 'Nopt1':
        return Nopt1.neighbor(schedule, machines, factories, data, iter)
    elif NS == 'Nopt2':
        return Nopt2.neighbor(schedule, machines, factories, data, iter)
    elif NS == 'Ntec1':
        return Ntec1.neighbor(schedule, machines, factories, data, iter)
    elif NS == 'Ntec2':
        return Ntec2.neighbor(schedule, machines, factories, data, iter)
    elif NS == 'Ntec3':
        return Ntec3.neighbor(schedule, machines, factories, data, iter)
    else:
        print("Please select the correct neighborhood structure!")

def cross_over(f1, f2, data, iter):
    pass

def mu_tation(f, data, iter):
    pass