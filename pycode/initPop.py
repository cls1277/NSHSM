import random

import numpy as np
import evalPop
import JSP
import FJSP
import DHFJSP


def init_pop(POPSIZE, data, PROBLEM):
    factories = np.zeros((POPSIZE, data['JOBS']), dtype='int32')
    machines = np.zeros((POPSIZE, data['sum_operations']), dtype='int32')
    schedules = np.zeros((POPSIZE, data['sum_operations']), dtype='int32')

    for i in range(POPSIZE):
        if PROBLEM == 'DHFJSP':
            if i <= POPSIZE * 0.6:
                factories[i] = DHFJSP.HFS_global(data)
                machines[i] = DHFJSP.HMS_global(factories[i], data)
                schedules[i] = DHFJSP.ROS(data)
            elif i <= POPSIZE * 0.9:
                factories[i] = DHFJSP.HFS_local(data)
                machines[i] = DHFJSP.HMS_local(factories[i], data)
                schedules[i] = DHFJSP.ROS(data)
            else:
                factories[i] = DHFJSP.RFS(data)
                machines[i] = DHFJSP.RMS(factories[i], data)
                schedules[i] = DHFJSP.ROS(data)
        elif PROBLEM == 'FJSP':
            for job in range(data['JOBS']):
                factories[i, job] = 0
            machines[i] = FJSP.RMS(data)
            schedules[i] = FJSP.ROS(data)
        elif PROBLEM == 'JSP':
            for job in range(data['JOBS']):
                factories[i, job] = 0
            machines[i] = JSP.RMS(data)
            schedules[i] = JSP.ROS(data)
        else :
            print("Please select the correct problem!")


    pop = {
        data['objective']: evalPop.evaluate(schedules, machines, factories, data),
        'schedules': schedules,
        'machines': machines,
        'factories': factories
    }
    key = pop[data['objective']][:,2]
    pop[data['objective']] = pop[data['objective']][:,0:2]
    pop['key'] = key
    return pop