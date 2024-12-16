# Date: 2023/12/30 21:17
# Author: cls1277
# Email: cls1277@163.com

import numpy as np
import random

def POX(schedule1, schedule2, data):
    new_s1 = np.ones(data['sum_operations'], dtype='int32') * (-1)
    new_s2 = np.ones(data['sum_operations'], dtype='int32') * (-1)
    jobs = list(range(data['JOBS']))

    I1 = random.sample(jobs, k=random.randint(0, data['JOBS']))
    I2 = [number for number in jobs if number not in I1]

    for i in range(data['sum_operations']):
        job1 = schedule1[i]
        if job1 in I1:
            new_s1[i] = job1
        job2 = schedule2[i]
        if job2 in I2:
            new_s2[i] = job2
    p1, p2 = 0, 0
    for i in range(data['sum_operations']):
        if new_s1[i] == -1:
            for j in range(p1, data['sum_operations']):
                if schedule2[j] in I2:
                    new_s1[i] = schedule2[j]
                    p1 = j+1
                    break
        if new_s2[i] == -1:
            for j in range(p2, data['sum_operations']):
                if schedule1[j] in I1:
                    new_s2[i] = schedule1[j]
                    p2 = j+1
                    break
    return new_s1, new_s2


def UX(sequence1, sequence2):
    if sequence1.shape != sequence2.shape:
        print("Please ensure that the two intersecting sequences have the same shape!")
        return -1
    random_binary_string = np.random.randint(2, size=len(sequence1))
    return np.where(random_binary_string == 1, sequence2, sequence1), np.where(random_binary_string == 1, sequence1, sequence2)