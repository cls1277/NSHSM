import numpy as np
import JSP
import FJSP
import DHFJSP
import popSort

def neighbor(schedule, machines, factories, objetives, key, data, iter, NS):
    if data['problem'] == 'DHFJSP':
        return DHFJSP.neighbor(schedule, machines, factories, objetives, key, data, iter, NS)
    elif data['problem'] == 'FJSP':
        return FJSP.neighbor(schedule, machines, factories, data, iter, NS)
    elif data['problem'] == 'JSP':
        return JSP.neighbor(schedule, machines, factories, data, iter, NS)
    else:
        print("please choose a correct neighborhood structure!")
        return -1

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
    schedules_new = np.empty((0, len(pop['schedules'][0])), dtype='int32')
    machines_new = np.empty((0, len(pop['machines'][0])), dtype='int32')
    factories_new = np.empty((0, len(pop['factories'][0])), dtype='int32')
    objectives_new = np.empty((0, data['objective_number']), dtype='int32')
    keys_new = np.empty((0), dtype='int32')

    for i, schedule in enumerate(pop['schedules']):
        output = neighbor(schedule, pop['machines'][i], pop['factories'][i], pop[data['objective']][i], pop['key'][i], data, iter, NS)
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

    pop_new = {
        data['objective']: objectives_new,
        'schedules': schedules_new,
        'machines': machines_new,
        'factories': factories_new,
        'key': keys_new
    }
    return pop_new, iter