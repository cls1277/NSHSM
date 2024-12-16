# Date: 2024/1/17 21:50
# Author: cls1277
# Email: cls1277@163.com

import numpy as np

def pareto(P):
    p = []
    N = P.shape[0]
    cntn = np.zeros(N)
    for i in range(N):
        for j in range(N):
            cnt = np.zeros(3)
            if P[i][0] > P[j][0]:
                cnt[0] += 1
            elif P[i][0] == P[j][0]:
                cnt[1] += 1
            else:
                cnt[2] += 1
            if P[i][1] > P[j][1]:
                cnt[0] += 1
            elif P[i][1] == P[j][1]:
                cnt[1] += 1
            else:
                cnt[2] += 1
            if cnt[2] == 0 and cnt[1] != 2:
                cntn[i] += 1
        pp = P[i]
        if cntn[i] == 0 and all(pp not in p for p in p):
            p.append(pp)
    return p