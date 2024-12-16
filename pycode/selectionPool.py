# Date: 2024/1/4 16:59
# Author: cls1277
# Email: cls1277@163.com

import numpy as np
import random
import tools

def tournament_selection(pop, data):
    POPSIZE = len(pop['schedules'])
    tour = 2

    schedules_new = np.zeros((POPSIZE, len(pop['schedules'][0])), dtype='int32')
    machines_new = np.zeros((POPSIZE, len(pop['machines'][0])), dtype='int32')
    factories_new = np.zeros((POPSIZE, len(pop['factories'][0])), dtype='int32')
    objectives_new = np.zeros((POPSIZE, data['objective_number']), dtype='int32')
    for i in range(POPSIZE):
        father = random.sample(range(len(pop['schedules'])), tour)
        nds = tools.nds(pop[data['objective']][father[0]], pop[data['objective']][father[1]], data)
        if nds == 1:
            schedules_new[i,:] = pop['schedules'][father[0]]
            machines_new[i,:] = pop['machines'][father[0]]
            factories_new[i,:] = pop['factories'][father[0]]
            objectives_new[i,:] = pop[data['objective']][father[0]]
        elif nds == 2:
            schedules_new[i,:] = pop['schedules'][father[1]]
            machines_new[i,:] = pop['machines'][father[1]]
            factories_new[i,:] = pop['factories'][father[1]]
            objectives_new[i,:] = pop[data['objective']][father[1]]
        else:
            if random.random() <= 0.5:
                schedules_new[i, :] = pop['schedules'][father[0]]
                machines_new[i, :] = pop['machines'][father[0]]
                factories_new[i, :] = pop['factories'][father[0]]
                objectives_new[i, :] = pop[data['objective']][father[0]]
            else:
                schedules_new[i, :] = pop['schedules'][father[1]]
                machines_new[i, :] = pop['machines'][father[1]]
                factories_new[i, :] = pop['factories'][father[1]]
                objectives_new[i, :] = pop[data['objective']][father[1]]

    output = {
        'schedules': schedules_new,
        'machines': machines_new,
        'factories': factories_new,
        data['objective']: objectives_new
    }
    return output