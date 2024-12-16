import json
import os
import JSP
import FJSP
import DHFJSP

def read_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def get_setting(problem, dataset):
    current_path = os.path.dirname(os.path.abspath(__file__))
    # current_path = 'C:\\cls\\cls1277\\DHFJS\\EEDHFJSP\\NS'
    file_path = os.path.join(current_path, '..', problem+'-benchmark', 'instances.json')
    js = read_json(file_path)
    for i in range(len(js)):
        if js[i]["name"] == dataset:
            return js[i]

def read_data(problem, dataset, objective):
    setting = get_setting(problem, dataset)
    data = []
    current_path = os.path.dirname(os.path.abspath(__file__))
    # current_path = 'C:\\cls\\cls1277\\DHFJS\\EEDHFJSP\\NS'
    file_path = os.path.join(current_path, '..', problem+'-benchmark', setting['path'])
    is_one_line = 0
    with open(file_path, 'r', encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line and not line.startswith('#'):
                # remove the firse row
                if is_one_line == 0:
                    is_one_line = 1
                    continue
                numbers = line.split()
                numbers = [int(num) for num in numbers]
                data.append(numbers)

    setting['objective'] = objective
    setting['objective_number'] = 2 if objective == 'makespan+TEC' else 1
    setting['problem'] = problem
    # the index of "operations" is job
    # the default problem is JSP
    # the index of "MACHINES" and "times" is node
    if problem == 'DHFJSP':
        DHFJSP.read_data(setting, data)
    elif problem == 'FJSP':
        setting['FACTORIES'] = 1
        FJSP.read_data(setting, data)
    elif problem == 'JSP':
        setting['FACTORIES'] = 1
        JSP.read_data(setting, data)
    else:
        print("Please select the correct problem!")

    return setting