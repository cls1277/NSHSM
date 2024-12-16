import os
import sys
sys.path.append('./build')
import json
import multiprocessing as mp
import LS

EXPERIMENT = "delta_new"
COUNT = 20

POPSIZEs = [100, 150, 200]
PCs = [0.8, 0.9, 1.0]
PMs = [0.1, 0.15, 0.2]
PKs = [0.3, 0.4, 0.5]
# LP = [[1, 1, 1, 1], [1, 2, 3, 2], [1, 3, 2, 3], [2, 1, 3, 3], [2, 2, 2, 1], [2, 3, 1, 2], [3, 1, 2, 2], [3, 2, 1, 3], [3, 3, 3, 1]]
LP = [[2, 1, 3, 3]]


def run_experiment(args):
    popsize, pc, pm, pk, count, dataset, experiment = args
    LS.run(popsize, pc, pm, pk, count, dataset, experiment)


def main():
    current_path = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_path, '..', 'DHFJSP-benchmark', 'instances.json')

    with open(file_path, "r", encoding="utf-8") as f:
        js = json.load(f)

    args_list = []
    for lp in LP:
        POPSIZE = POPSIZEs[lp[0] - 1]
        PC = PCs[lp[1] - 1]
        PM = PMs[lp[2] - 1]
        PK = PKs[lp[3] - 1]
        for i in range(len(js)):
            dataset = js[i]["name"]
            for j in range(1, COUNT + 1):
                args_list.append((POPSIZE, PC, PM, PK, j, dataset, EXPERIMENT))

    with mp.Pool(processes=24) as pool:
        pool.map(run_experiment, args_list)


if __name__ == "__main__":
    main()
