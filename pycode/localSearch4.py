# Date: 2024/2/3 10:53
# Author: cls1277
# Email: cls1277@163.com
import math

import numpy as np
import JSP
import FJSP
import DHFJSP
import Nopt1
import popSort
import guessObj
import solveSchedule
import evalPop
import tools
import Ntec3


def local_search(pop_old, data, iter, NS):
    # to pareto solutions
    indices = popSort.fast_non_dominated_sort(pop_old[data['objective']][:, :])[0]
    pop = {
        'schedules': pop_old['schedules'][indices],
        'machines': pop_old['machines'][indices],
        'factories': pop_old['factories'][indices],
        data['objective']: pop_old[data['objective']][indices],
        'key': pop_old['key'][indices]
    }

    objs = {}
    min_objs = np.empty((len(pop['schedules']), data['objective_number']), dtype='int32')

    schedules_new = np.empty((0, len(pop['schedules'][0])), dtype='int32')
    machines_new = np.empty((0, len(pop['machines'][0])), dtype='int32')
    factories_new = np.empty((0, len(pop['factories'][0])), dtype='int32')
    objectives_new = np.empty((0, data['objective_number']), dtype='int32')
    keys_new = np.empty((0), dtype='int32')

    for i, schedule in enumerate(pop['schedules']):
        # obtain the minimum makespan and TEC that each individual can obtain, rather than the same individual
        min_mksp, min_tec = pop[data['objective']][i][0], pop[data['objective']][i][1]
        min_objs[i] =  np.array([min_mksp, min_tec])

    K = math.ceil(len(pop['schedules']) / 2)
    do_mksp = np.argsort(min_objs[:, 1])[::-1][:K]
    do_tec = np.argsort(min_objs[:, 0])[::-1][:K]

    for i in do_mksp:
        schedule, machines, factories, key = pop['schedules'][i], pop['machines'][i], pop['factories'][i], int(pop['key'][i])
        output = Nopt1.neighbor(schedule, pop['machines'][i], pop['factories'][i], pop['key'][i], data, iter)
        # if the neighborhood have no neighbor
        if output == -1 or output == None:
            continue
        schedule_new, machine_new, objective_new, iter = output
        key_new = objective_new[:,2]
        objective_new = objective_new[:,0:2]

        factory_new = np.reshape(pop['factories'][i], (1, -1))

        schedules_new = np.concatenate((schedules_new, schedule_new), axis=0)
        machines_new = np.concatenate((machines_new, machine_new), axis=0)
        factories_new = np.concatenate((factories_new, np.tile(factory_new, (len(schedule_new), 1))), axis=0)
        objectives_new = np.concatenate((objectives_new, objective_new))
        keys_new = np.concatenate((keys_new, key_new))
        if iter == 0:
            break

    for i in do_tec:
        schedule, machines, factories, key = pop['schedules'][i], pop['machines'][i], pop['factories'][i], int(pop['key'][i])
        output = Ntec3.neighbor(schedule, pop['machines'][i], pop['factories'][i], pop[data['objective']][i],pop['key'][i], data, iter)
        # if the neighborhood have no neighbor
        if output == -1 or output == None:
            continue
        schedule_new, machine_new, objective_new, iter = output
        key_new = objective_new[:, 2]
        objective_new = objective_new[:, 0:2]

        factory_new = np.reshape(pop['factories'][i], (1, -1))

        schedules_new = np.concatenate((schedules_new, schedule_new), axis=0)
        machines_new = np.concatenate((machines_new, machine_new), axis=0)
        factories_new = np.concatenate((factories_new, np.tile(factory_new, (len(schedule_new), 1))), axis=0)
        objectives_new = np.concatenate((objectives_new, objective_new))
        keys_new = np.concatenate((keys_new, key_new))
        if iter == 0:
            break

    pop_new = {
        data['objective']: objectives_new,
        'schedules': schedules_new,
        'machines': machines_new,
        'factories': factories_new,
        'key': keys_new
    }
    return pop_new, iter