# Date: 2023/12/30 21:36
# Author: cls1277
# Email: cls1277@163.com

import random
import tools
import copy

FAIL_TIMES = 10

def MuOS(schedule, data):
    new_schedule = copy.deepcopy(schedule)
    random_numbers = random.sample(range(data['sum_operations']), 2)
    new_schedule[random_numbers[0]], new_schedule[random_numbers[1]] = new_schedule[random_numbers[1]], new_schedule[random_numbers[0]]
    return new_schedule

def MuMS(machine, factory, data):
    new_machine = copy.deepcopy(machine)
    node = random.randint(1, data['sum_operations'])
    job, operation = tools.get_job_operation(node, data)
    f = factory[job]
    cnt = 0
    while len(data['machines'][f][node]) == 1:
        node = random.randint(1, data['sum_operations'])
        job, operation = tools.get_job_operation(node, data)
        f = factory[job]
        cnt += 1
        # something wrong
        if cnt == FAIL_TIMES:
            return machine
    machines = copy.deepcopy(data['machines'][f][node])
    machines.remove(new_machine[node-1])
    new_machine[node-1] = random.choice(machines)
    return new_machine

def MuFS(factory, data):
    new_factory = copy.deepcopy(factory)
    job = random.randint(0, data['JOBS']-1)
    new_f = random.choice([val for val in range(data['FACTORIES']) if val != factory[job]])
    new_factory[job] = new_f
    return new_factory