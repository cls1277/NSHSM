import math
import numpy as np
import JSP
import FJSP
import DHFJSP
import popSort
import guessObj
import solveSchedule
import evalPop
import tools
import Ntec3


def local_search(pop_old, data, iter, Pk=0.5):
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
        mksps, tecs = guessObj.guess(schedule, pop['machines'][i], pop['factories'][i], pop[data['objective']][i], pop['key'][i], data)
        objs[i] = {'mksp': mksps, 'tec': tecs}

        if len(mksps) == 0:
            min_mksp = pop[data['objective']][i][0]
        else:
            min_mksp = min(item['objective'] for item in mksps)
        if len(tecs) == 0:
            min_tec = pop[data['objective']][i][1]
        else:
            min_tec = min(item['objective'] for item in tecs)
        min_objs[i] = np.array([min_mksp, min_tec])

    K = math.ceil(len(pop['schedules']) * Pk)
    do_mksp = np.argsort(min_objs[:, 0])[:K]
    do_tec = np.argsort(min_objs[:, 1])[:K]

    for i in do_mksp:
        schedule, machines, factories, key = pop['schedules'][i], pop['machines'][i], pop['factories'][i], int(pop['key'][i])
        for j in range(len(objs[i]['mksp'])):
            bestPop = objs[i]['mksp'][j]
            index_v = bestPop['v']
            if bestPop['index'] == index_v or bestPop['index'] == -1:
                continue
            indexes_to_nodes, nodes_to_indexes, PM_index, PJ_index, SM_index, SJ_index = tools.get_PSJM(schedule, machines, factories, key, data)
            v = indexes_to_nodes[index_v]

            new_machine = np.copy(machines)
            new_machine[v - 1] = bestPop['machine']
            node_best = indexes_to_nodes[bestPop['index']]
            j_b, o_b = tools.get_job_operation(node_best, data)
            if bestPop['direction'] == 'all':
                new_makespan = evalPop.evaluate_ind(schedule, new_machine, factories, data)
                new_schedule = schedule
            elif bestPop['direction'] == 'forward':
                new_schedule, new_makespan = solveSchedule.forward_schedule(schedule, new_machine, factories, PM_index,
                                                                             PJ_index, SM_index, SJ_index, index_v, bestPop['index'],
                                                                             data)
            else:
                new_schedule, new_makespan = solveSchedule.backward_schedule(schedule, new_machine, factories, PM_index,
                                                                             PJ_index, SM_index, SJ_index, bestPop['index'], index_v,
                                                                             data)


            new_schedule = np.reshape(new_schedule, (1, -1))
            schedules_new = np.concatenate((schedules_new, new_schedule), axis=0)
            new_machine = np.reshape(new_machine, (1, -1))
            machines_new = np.concatenate((machines_new, new_machine), axis=0)
            factory_new = np.reshape(factories, (1, -1))
            factories_new = np.concatenate((factories_new, np.tile(factory_new, (len(new_schedule), 1))), axis=0)
            objective_new = new_makespan[0, 0:2]
            objective_new = np.reshape(objective_new, (1, -1))
            objectives_new = np.concatenate((objectives_new, objective_new))
            key_new = new_makespan[0, 2]
            key_new = np.reshape(key_new, (-1))
            keys_new = np.concatenate((keys_new, key_new))
            iter -= 1
            if iter == 0:
                break

    for i in do_tec:
        schedule, machines, factories, key = pop['schedules'][i], pop['machines'][i], pop['factories'][i], int(pop['key'][i])

        for j in range(len(objs[i]['tec'])):
            bestPop = objs[i]['tec'][j]
            index_v = bestPop['v']
            if bestPop['index'] == index_v or bestPop['index'] == -1:
                continue
            indexes_to_nodes, nodes_to_indexes, PM_index, PJ_index, SM_index, SJ_index = tools.get_PSJM(schedule, machines, factories, key, data)
            v = indexes_to_nodes[index_v]

            new_machine = np.copy(machines)
            new_machine[v - 1] = bestPop['machine']
            node_best = indexes_to_nodes[bestPop['index']]
            j_b, o_b = tools.get_job_operation(node_best, data)
            if bestPop['direction'] == 'all':
                new_makespan = evalPop.evaluate_ind(schedule, new_machine, factories, data)
                new_schedule = schedule
            elif bestPop['direction'] == 'forward':
                new_schedule, new_makespan = solveSchedule.forward_schedule(schedule, new_machine, factories, PM_index,
                                                                            PJ_index, SM_index, SJ_index, index_v,
                                                                            bestPop['index'],
                                                                            data)
            else:
                new_schedule, new_makespan = solveSchedule.backward_schedule(schedule, new_machine, factories, PM_index,
                                                                             PJ_index, SM_index, SJ_index,
                                                                             bestPop['index'], index_v,
                                                                             data)


            new_schedule = np.reshape(new_schedule, (1, -1))
            schedules_new = np.concatenate((schedules_new, new_schedule), axis=0)
            new_machine = np.reshape(new_machine, (1, -1))
            machines_new = np.concatenate((machines_new, new_machine), axis=0)
            factory_new = np.reshape(factories, (1, -1))
            factories_new = np.concatenate((factories_new, np.tile(factory_new, (len(new_schedule), 1))), axis=0)
            objective_new = new_makespan[0, 0:2]
            objective_new = np.reshape(objective_new, (1, -1))
            objectives_new = np.concatenate((objectives_new, objective_new))
            key_new = new_makespan[0, 2]
            key_new = np.reshape(key_new, (-1))
            keys_new = np.concatenate((keys_new, key_new))
            iter -= 1
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