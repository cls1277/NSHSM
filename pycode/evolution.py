# Date: 2024/1/2 21:15
# Author: cls1277
# Email: cls1277@163.com

import numpy as np
import random
import JSP
import FJSP
import DHFJSP
import evalPop
import selectionPool


def crossover(pop, data, iter, Pc=0.9):
    POPSIZE = len(pop['schedules'])

    schedules_new = np.empty((0, len(pop['schedules'][0])), dtype='int32')
    machines_new = np.empty((0, len(pop['machines'][0])), dtype='int32')
    factories_new = np.empty((0, len(pop['factories'][0])), dtype='int32')
    # objectives_new = np.empty((0, data['objective_number']), dtype='int32')

    pop_pool = selectionPool.tournament_selection(pop, data)
    while schedules_new.shape[0] < pop['schedules'].shape[0]:
        father = random.sample(range(POPSIZE), 2)
        f1 = {
            'schedules': pop_pool['schedules'][father[0]],
            'machines': pop_pool['machines'][father[0]],
            'factories': pop_pool['factories'][father[0]],
            data['objective']: pop_pool[data['objective']][father[0]]
        }
        f2 = {
            'schedules': pop_pool['schedules'][father[1]],
            'machines': pop_pool['machines'][father[1]],
            'factories': pop_pool['factories'][father[1]],
            data['objective']: pop_pool[data['objective']][father[1]]
        }
        rd = random.random()
        if rd <= Pc:
            if data['problem'] == 'DHFJSP':
                # iter 不变
                schedule_new, machine_new, factory_new, iter = DHFJSP.cross_over(f1, f2, data, iter)
            elif data['problem'] == 'FJSP':
                schedule_new, machine_new, factory_new, objective_new, iter = FJSP.cross_over(f1, f2, data, iter)
            elif data['problem'] == 'JSP':
                schedule_new, machine_new, factory_new, objective_new, iter = JSP.cross_over(f1, f2, data, iter)
            else:
                print("please choose a correct problem!")
                return -1
        else:
            schedule_new = pop_pool['schedules'][father[0]], pop_pool['schedules'][father[1]]
            machine_new = pop_pool['machines'][father[0]], pop_pool['machines'][father[1]]
            factory_new = pop_pool['factories'][father[0]], pop_pool['factories'][father[1]]

        schedules_new = np.concatenate((schedules_new, schedule_new), axis=0)
        machines_new = np.concatenate((machines_new, machine_new), axis=0)
        factories_new = np.concatenate((factories_new, factory_new), axis=0)
        # objectives_new = np.concatenate((objectives_new, objective_new))

    # pop_new = {
    #     # data['objective']: np.tile(0, (schedules_new.shape[0], data['objective_number'])),
    #     data['objective']: evalPop.evaluate(schedules_new, machines_new, factories_new, data)[:, 0:2],
    #     'schedules': schedules_new,
    #     'machines': machines_new,
    #     'factories': factories_new,
    #     'key': evalPop.evaluate(schedules_new, machines_new, factories_new, data)[:, 2]
    # }
    pop_new = {
        data['objective']: np.tile(0, (schedules_new.shape[0], data['objective_number'])),
        'schedules': schedules_new,
        'machines': machines_new,
        'factories': factories_new,
        'key': np.tile(0, (schedules_new.shape[0]))
    }
    return pop_new, iter


def mutation(pop, data, iter, Pm=0.1):
    for i in range(len(pop['schedules'])):
        rd = random.random()
        if rd <= Pm:
            f = {
                'schedules': pop['schedules'][i],
                'machines': pop['machines'][i],
                'factories': pop['factories'][i],
                'key': pop['key'][i]
            }
            if data['problem'] == 'DHFJSP':
                schedule_new, machine_new, factory_new = DHFJSP.mu_tation(f, data)
                pop['schedules'][i] = schedule_new
                pop['machines'][i] = machine_new
                pop['factories'][i] = factory_new
            elif data['problem'] == 'FJSP':
                schedule_new, machine_new, factory_new, objective_new, iter = FJSP.mu_tation(f, data, iter)
                pop['schedules'][i] = schedule_new
                pop['machines'][i] = machine_new
                pop['factories'][i] = factory_new
                pop[data['objective']][i] = objective_new
            elif data['problem'] == 'JSP':
                schedule_new, machine_new, factory_new, objective_new, iter = JSP.mu_tation(f, data, iter)
                pop['schedules'][i] = schedule_new
                pop['machines'][i] = machine_new
                pop['factories'][i] = factory_new
                pop[data['objective']][i] = objective_new
        obj_key = evalPop.evaluate_ind(pop['schedules'][i], pop['machines'][i], pop['factories'][i],
                                       data)
        pop[data['objective']][i] = obj_key[:, 0:2]
        pop['key'][i] = obj_key[0, 2]
        iter -= 1
    return pop, iter
