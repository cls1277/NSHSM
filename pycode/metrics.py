# Date: 2024/2/18 19:44
# Author: cls1277
# Email: cls1277@163.com

import os
from pymoo.indicators.hv import HV
from pymoo.indicators.gd import GD
import numpy as np
import json
import pandas as pd
import re
import popSort
import pareto

# pattern = r"_(\d+)\."
pattern = r"(\d+)\."

current_path = 'C:/cls/cls1277/DHFJS/EEDHFJSP/NS3'
file_path = os.path.join(current_path, '..', 'DHFJSP-benchmark', 'instances.json')
with open(file_path, "r", encoding="utf-8") as f:
    js = json.load(f)
DATASETS = [js[i]["name"] for i in range(len(js))]

# 要计算指标的result文件夹下的子目录名，即实验名
# exps = ['DOE_POPSIZE100_PC0.8_PM0.1_PK0.3', 'DOE_POPSIZE100_PC0.9_PM0.2_PK0.4', 'DOE_POPSIZE100_PC1.0_PM0.15_PK0.5', 'DOE_POPSIZE150_PC0.8_PM0.2_PK0.5', 'DOE_POPSIZE150_PC0.9_PM0.15_PK0.3', 'DOE_POPSIZE150_PC1.0_PM0.1_PK0.4', 'DOE_POPSIZE200_PC0.8_PM0.15_PK0.4', 'DOE_POPSIZE200_PC0.9_PM0.1_PK0.5', 'DOE_POPSIZE200_PC1.0_PM0.2_PK0.3']
# exps = ['no_globalsearch', 'no_localsearch', 'only_makespan', 'only_tec', 'rand_select', 'origin', 'origin_new']
# exps = ['MOEAD', 'NSGAII', 'TSNSGAII', 'IMANS', 'DQNPEA', 'NSHSM00']
exps = ['NSHSM1', 'NSHSM2', 'NSHSM3', 'NSHSM4', 'NSHSM5', 'NSHSM00']
exps_path = {}
# 实验重复次数
COUNT = 20

HVs = np.zeros((len(DATASETS)+1,len(exps)))
GDs = np.zeros((len(DATASETS)+1,len(exps)))
SPs = np.zeros((len(DATASETS)+1,len(exps)))

current_path = os.path.dirname(os.path.abspath(__file__))
result_path = os.path.join(current_path, 'result')
dirs = os.listdir(result_path)
for dir in dirs:
    if dir in exps:
        exps_path[dir] = os.listdir(os.path.join(result_path, dir))
# print(exps_path)

def Spread(objs, pf):
    if objs.shape[0] == 1:
        return 1
    Dis1 = np.linalg.norm(objs[:, None, :] - objs[None, :, :], axis=-1)
    np.fill_diagonal(Dis1, np.inf)
    E = np.argmax(pf, axis=0)
    Dis2 = np.linalg.norm(pf[E, :][:, None, :] - objs[None, :, :], axis=-1)
    d1 = np.sum(np.min(Dis2, axis=1))
    d2 = np.mean(np.min(Dis1, axis=1))
    score = (d1 + np.sum(np.abs(np.min(Dis1, axis=1) - d2))) / (d1 + (objs.shape[0] - objs.shape[1]) * d2)
    return score

for i, DATASET in enumerate(DATASETS):
    objective = np.empty((0, 2), dtype='int32')

    solutions = {}

    for exp in exps:
        solutions[exp] = {}
        for p in exps_path[exp]:
            if DATASET not in p:
                continue
            path = os.path.join(result_path, exp, p)
            files = os.listdir(path)
            for file in files:
                if file[0:3] == 'res':
                    match = re.search(pattern, file)
                    cnt = int(match.group(1))
                    if cnt > COUNT:
                        continue
                    # COUNT = max(COUNT, cnt)
                    file_path = os.path.join(path, file)
                    with open(file_path, 'r') as file:
                        content = file.read()
                    pf = np.fromstring(content.replace('[', '').replace(']', ''), sep=' ').reshape(-1, 2)
                    pf = np.array(pareto.pareto(pf))
                    objective = np.concatenate((objective, pf), axis=0)
                    solutions[exp][cnt] = pf

    minn1 = max(np.min(objective[:, 0]), 0)
    minn2 = max(np.min(objective[:, 1]), 0)
    maxx1 = np.max(objective[:, 0]) * 1.1
    maxx2 = np.max(objective[:, 1]) * 1.1
    A = np.array([minn1, minn2])
    B = np.array([maxx1, maxx2])

    sorted_indices = np.argsort(objective[:, 0])
    sorted_arr = objective[sorted_indices]
    final_sorted_indices = np.lexsort((sorted_arr[:, 1], sorted_arr[:, 0]))
    obj0 = sorted_arr[final_sorted_indices]
    new_objective = obj0[0,:].reshape(1, -1)
    for j in range(1, len(obj0)):
        if obj0[j, 0] == obj0[j-1, 0]:
            continue
        else:
            new_objective = np.concatenate((new_objective, obj0[j,:].reshape(1, -1)), axis=0)

    pf = new_objective[popSort.fast_non_dominated_sort(new_objective[:,:])[0]]
    pf = (pf-A)/(B-A)
    ind_gd = GD(pf)
    ind_hv = HV(ref_point=np.array([1, 1]))

    HVresult = np.zeros((COUNT, len(exps)))
    GDresult = np.zeros((COUNT, len(exps)))
    SPresult = np.zeros((COUNT, len(exps)))

    for j, exp in enumerate(exps):
        hv_bar, gd_bar, sp_bar = 0, 0, 0
        for cnt in range(1, COUNT+1):
            S = (solutions[exp][cnt]-A)/(B-A)
            # hv
            hv = ind_hv(S)
            hv_bar += hv
            HVresult[cnt-1, j] = hv
            # gd
            gd = ind_gd(S)
            gd_bar += gd
            GDresult[cnt - 1, j] = gd
            # spread
            sp = Spread(S, pf)
            sp_bar += sp
            SPresult[cnt - 1, j] = sp
        hv_bar /= COUNT
        HVs[i, j] = hv_bar
        gd_bar /= COUNT
        GDs[i, j] = gd_bar
        sp_bar /= COUNT
        SPs[i, j] = sp_bar

    hv_result_path = result_path + '\\HVresult\\' + DATASET + '.xlsx'
    with pd.ExcelWriter(hv_result_path) as writer_hv:
        df_hv_result = pd.DataFrame(HVresult)
        df_hv_result.to_excel(writer_hv, index=False, header=False)
    gd_result_path = result_path + '\\GDresult\\' + DATASET + '.xlsx'
    with pd.ExcelWriter(gd_result_path) as writer_gd:
        df_gd_result = pd.DataFrame(GDresult)
        df_gd_result.to_excel(writer_gd, index=False, header=False)
    sp_result_path = result_path + '\\SPresult\\' + DATASET + '.xlsx'
    with pd.ExcelWriter(sp_result_path) as writer_sp:
        df_sp_result = pd.DataFrame(SPresult)
        df_sp_result.to_excel(writer_sp, index=False, header=False)

for i in range(len(DATASETS)):
    for j in range(len(exps)):
        HVs[-1, j] = np.mean(HVs[:, j])
        GDs[-1, j] = np.mean(GDs[:, j])
        SPs[-1, j] = np.mean(SPs[:, j])
HVs = np.round(HVs, 4)
GDs = np.round(GDs, 4)
SPs = np.round(SPs, 4)

DATASETS.insert(len(DATASETS), 'average')
exps.insert(0, ' ')

with pd.ExcelWriter(os.path.join(result_path, 'metrics.xlsx')) as writer:
    df_hv = pd.DataFrame(HVs)
    df_hv.insert(0, " ", DATASETS)
    df_hv.columns = exps
    df_hv.to_excel(writer, sheet_name='HV', index=False)

    df_gd = pd.DataFrame(GDs)
    df_gd.insert(0, " ", DATASETS)
    df_gd.columns = exps
    df_gd.to_excel(writer, sheet_name='GD', index=False)

    df_sp = pd.DataFrame(SPs)
    df_sp.insert(0, " ", DATASETS)
    df_sp.columns = exps
    df_sp.to_excel(writer, sheet_name='SP', index=False)

print("Done!")