import os
import json
from multiprocessing import Pool
import LS

EXPERIMENT = "origin"
POPSIZE = 100
COUNT = 2
PC = 1
PM = 0.3
PK = 0.5

current_path = os.path.dirname(os.path.abspath(__file__))
file_path = os.path.join(current_path, '..', 'DHFJSP-benchmark', 'instances_temp.json')
with open(file_path, "r", encoding="utf-8") as f:
    js = json.load(f)
for i in range(len(js)):
    DATASET = js[i]["name"]
    for j in range(1, COUNT+1):
        LS.run(POPSIZE, PC, PM, PK, j, DATASET, EXPERIMENT)
    # pool = Pool(processes=COUNT)
    # pool.starmap(LS.run, [(POPSIZE, PC, PM, PK, j, DATASET, EXPERIMENT) for j in range(1, COUNT+1)])
    # pool.close()
    # pool.join()