import numpy as np
import tools

def evaluate(schedules, machines, factories, data, P = (4,1)):
    if data['objective'] == 'makespan':
        mksp = np.array([makespan(schedules[i], machines[i], factories[i], data) for i in range(schedules.shape[0])])
        return np.reshape(mksp, (-1, 1))
    elif data['objective'] == 'TEC':
        p = np.empty((2, 1))
        p[0, 0], p[1, 0] = P
        tec = np.array([TEC(schedules[i], machines[i], factories[i], data, p) for i in range(schedules.shape[0])])
        return np.reshape(tec, (-1, 1))
    elif data['objective'] == 'makespan+TEC':
        mksp = np.array([makespan(schedules[i], machines[i], factories[i], data) for i in range(schedules.shape[0])])
        p = np.empty((2, 1))
        p[0, 0], p[1, 0] = P
        tec = np.array([TEC(schedules[i], machines[i], factories[i], data, p) for i in range(schedules.shape[0])])

        mksp = np.reshape(mksp, (-1, 2))
        mk = mksp[:,0]
        mk = np.reshape(mk, (-1, 1))
        key = mksp[:,1]
        key = np.reshape(key, (-1, 1))
        tec = np.reshape(tec, (-1, 1))
        return np.concatenate((mk, tec, key), axis=1)
    else:
        print("Please select the correct objective function!")
        return -1

def evaluate_ind(schedule, machine, factories, data, P = (4,1)):
    if data['objective'] == 'makespan':
        return np.reshape(np.array(makespan(schedule, machine, factories, data)), (1, -1))
    elif data['objective'] == 'TEC':
        p = np.empty((2, 1))
        p[0, 0], p[1, 0] = P
        return np.reshape(np.array(TEC(schedule, machine, factories, data, p)), (1, -1))
    elif data['objective'] == 'makespan+TEC':
        mksp = np.array([makespan(schedule, machine, factories, data)])
        p = np.empty((2, 1))
        p[0, 0], p[1, 0] = P
        tec = np.array([TEC(schedule, machine, factories, data, p)])

        mksp = np.reshape(mksp, (-1, 2))
        mk = mksp[:,0]
        mk = np.reshape(mk, (-1, 1))
        key = mksp[:,1]
        key = np.reshape(key, (-1, 1))
        tec = np.reshape(tec, (-1, 1))
        return np.concatenate((mk, tec, key), axis=1)
    else:
        print("Please select the correct objective function!")
        return -1

def makespan(schedule, machines, factories, data):
    mksp = -1
    key_f = -1
    for factory in range(data['FACTORIES']):
        endtime_job = np.zeros((data['JOBS']))
        endtime_machine = np.zeros((data['MACHINES']))
        operation = np.ones((data['JOBS']), dtype='int32') * (-1)
        for index, job in enumerate(schedule):
            if factories[job] != factory:
                continue
            operation[job] += 1
            machine = tools.get_machine(job, operation[job], machines, data)
            time = tools.get_time(job, operation[job], machine, factory, data)
            endtime = max(endtime_job[job], endtime_machine[machine]) + time
            endtime_job[job] = endtime_machine[machine] = endtime
        if np.max(endtime_machine) > mksp:
            key_f = factory
        mksp = max(mksp, np.max(endtime_machine))
    return mksp, key_f

def TEC(schedule, machines, factories, data, p):
    t = np.zeros((1, 2))
    for factory in range(data['FACTORIES']):
        endtime_job = np.zeros((data['JOBS']))
        endtime_machine = np.zeros((data['MACHINES']))
        operation = np.ones((data['JOBS']), dtype='int32') * (-1)
        for index, job in enumerate(schedule):
            if factories[job] != factory:
                continue
            operation[job] += 1
            machine = tools.get_machine(job, operation[job], machines, data)
            time = tools.get_time(job, operation[job], machine, factory, data)
            starttime = max(endtime_job[job], endtime_machine[machine])
            t[0,0] += time
            t[0, 1] += starttime - endtime_machine[machine]
            # if endtime_machine[machine] != 0:
            #     t[0,1] += starttime - endtime_machine[machine]
            endtime_job[job] = endtime_machine[machine] = starttime + time
    return np.dot(t, p)[0,0]

def TEC_se(schedule, machines, factories, data, P, st_index, et_index):
    if data['objective'] != 'makespan+TEC':
        print("Please select the correct objective function!")
        return -1

    mksp = np.array([makespan(schedule, machines, factories, data)])

    p = np.empty((2, 1))
    p[0, 0], p[1, 0] = P
    t = np.zeros((1, 2))
    for factory in range(data['FACTORIES']):
        endtime_machine = np.zeros((data['MACHINES']))
        operation = np.ones((data['JOBS']), dtype='int32') * (-1)
        for index, job in enumerate(schedule):
            if factories[job] != factory:
                continue
            operation[job] += 1
            machine = tools.get_machine(job, operation[job], machines, data)
            time = tools.get_time(job, operation[job], machine, factory, data)
            starttime = st_index[index]
            t[0,0] += time
            t[0, 1] += starttime - endtime_machine[machine]
            # if endtime_machine[machine] != 0:
            #     t[0,1] += starttime - endtime_machine[machine]
            endtime_machine[machine] = et_index[index]
    tec = np.dot(t, p)[0,0]

    mksp = np.reshape(mksp, (-1, 2))
    mk = mksp[:, 0]
    mk = np.reshape(mk, (-1, 1))
    key = mksp[:, 1]
    key = np.reshape(key, (-1, 1))
    tec = np.reshape(tec, (-1, 1))
    return np.concatenate((mk, tec, key), axis=1)