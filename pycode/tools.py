import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import json
from operator import sub
import random
import matplotlib.patches as mpatches
import popSort

# job starting from 0, operation 0
def get_job_operation(node, data):
    sum_operations = 0
    for job, operations in enumerate(data['operations']):
        sum_operations += operations
        if node <= sum_operations:
            operation = node - (sum_operations - operations) - 1
            return int(job), int(operation)

def get_node(job, operation, data):
    return int(sum(data['operations'][:job]) + operation + 1)

def get_machine(job, operation, machines, data):
    index = int(sum(data['operations'][:job]) + operation)
    return  machines[index]

def get_time(job, operation, machine, factory, data):
    node = get_node(job, operation, data)
    for i, m in enumerate(data['machines'][factory][node]):
        if m == machine:
            return float(data['times'][factory][node][i])


# map: (one) graph nodes -> schedule vector index(i)
def get_node_to_index(node, schedule, data):
    node_job, node_operation = get_job_operation(node, data)
    operation = np.ones((data['JOBS']), dtype='int32') * (-1)
    for i, job in enumerate(schedule):
        operation[job] += 1
        if job == node_job and operation[job] == node_operation:
            return i


# map: (all) graph nodes -> schedule vector index(i)
def get_nodes_to_indexes(schedule, data):
    # adding 1: because 'node' starts from 1
    nodes_to_indexes = np.zeros(data['sum_operations']+1, dtype='int32')
    operation = np.ones((data['JOBS']), dtype='int32') * (-1)
    for i, job in enumerate(schedule):
        job = int(job)
        operation[job] += 1
        nodes_to_indexes[get_node(job, operation[job], data)] = i
    return nodes_to_indexes


# map: (one) schedule vector index(i) -> graph nodes
def get_index_to_node(index, schedule, data):
    operation = np.ones((data['JOBS']), dtype='int32') * (-1)
    for i, job in enumerate(schedule):
        operation[job] += 1
        if i == index:
            return get_node(job, operation[job], data)


# map: (all) schedule vector index(i) -> graph nodes
def get_indexes_to_nodes(schedule, data):
    indexes_to_nodes = np.zeros(len(schedule), dtype='int32')
    operation = np.ones((data['JOBS']), dtype='int32') * (-1)
    for i, job in enumerate(schedule):
        operation[job] += 1
        indexes_to_nodes[i] = get_node(job, operation[job], data)
    return indexes_to_nodes


# get where the operation in blocks, -1:first, 0:between, 1:last
def get_operation_in_blocks(index, blocks):
    for block in blocks:
        if index in blocks[block]:
            i = blocks[block].index(index)
            if i == 0:
                return -1
            elif i == len(blocks[block]) - 1:
                return 1
            else:
                return 0

# get start time and end time of a schedule
# nodes, it needs to be changed into index
def get_start_end_time(schedule, machines, factories, data, factory):
    start_time_nodes = np.zeros((data['sum_operations'] + 2), dtype='int32')
    end_time_nodes = np.zeros((data['sum_operations'] + 2), dtype='int32')

    endtime_job = np.zeros((data['JOBS']))
    endtime_machine = np.zeros((data['MACHINES']))
    operation = np.ones((data['JOBS']), dtype='int32') * (-1)
    for index, job in enumerate(schedule):
        if factories[job] != factory:
            continue
        operation[job] += 1
        machine = get_machine(job, operation[job], machines, data)
        time = get_time(job, operation[job], machine, factories[job], data)

        node = get_node(job, operation[job], data)
        start_time_nodes[node] = max(endtime_job[job], endtime_machine[machine])

        end_time_nodes[node] = endtime = start_time_nodes[node] + time
        endtime_job[job] = endtime_machine[machine] = endtime

    return start_time_nodes, end_time_nodes

# get elements of a list, which in critical path
# be used to choose u (v) of N8, the same start time
def get_list_in_critical_path(l, critical_path):
    result = []
    for i in l:
        if i in critical_path:
           result.append(i)
    return result

def get_PSJM(schedule, machines, factories, key, data):
    import Graph

    factory = int(key)

    N = data['sum_operations'] + 1
    graph, PM, PJ, SM, SJ = Graph.init_graph(schedule, machines, factories, factory, data)

    nodes_to_indexes = get_nodes_to_indexes(schedule, data)
    indexes_to_nodes = get_indexes_to_nodes(schedule, data)

    PM_index = np.zeros((data['sum_operations']), dtype='int32')
    PJ_index = np.zeros((data['sum_operations']), dtype='int32')
    SM_index = np.zeros((data['sum_operations']), dtype='int32')
    SJ_index = np.zeros((data['sum_operations']), dtype='int32')
    operation = np.ones((data['JOBS']), dtype='int32') * (-1)
    for index, job in enumerate(schedule):
        operation[job] += 1
        if 0 < PM[indexes_to_nodes[index]] < N:
            PM_index[index] = nodes_to_indexes[PM[indexes_to_nodes[index]]]
        else:
            PM_index[index] = -1
        if 0 < PJ[indexes_to_nodes[index]] < N:
            PJ_index[index] = nodes_to_indexes[PJ[indexes_to_nodes[index]]]
        else:
            PJ_index[index] = -1
        if 0 < SM[indexes_to_nodes[index]] < N:
            SM_index[index] = nodes_to_indexes[SM[indexes_to_nodes[index]]]
        else:
            SM_index[index] = -1
        if 0 < SJ[indexes_to_nodes[index]] < N:
            SJ_index[index] = nodes_to_indexes[SJ[indexes_to_nodes[index]]]
        else:
            SJ_index[index] = -1
    return indexes_to_nodes, nodes_to_indexes, PM_index, PJ_index, SM_index, SJ_index

# mapping from a schedule to a json file of gantt
def get_gantt(schedule, machines, factories, data, path="gantt.json", title="gantt", factory=0):

    gantt = dict()
    gantt['machines'] = data['MACHINES']
    gantt['jobs'] = data['JOBS']
    gantt['xlabel'] = 'time'
    gantt['title'] = title
    gantt["packages"] = []

    endtime_job = np.zeros((data['JOBS']))
    endtime_machine = np.zeros((data['MACHINES']))
    operation = np.ones((data['JOBS']), dtype='int32') * (-1)
    for index, job in enumerate(schedule):
        if factories[job] != factory:
            continue
        operation[job] += 1
        machine = get_machine(job, operation[job], machines, data)
        time = get_time(job, operation[job], machine, 0, data)
        starttime = max(endtime_job[job], endtime_machine[machine])
        endtime = starttime + time
        endtime_job[job] = endtime_machine[machine] = endtime
        package = {
            "start": starttime,
            "end": endtime,
            "machine": int(machine),
            "job": int(job)
        }
        gantt["packages"].append(package)

    with open(path, 'w') as json_file:
        json.dump(gantt, json_file, indent=2)
    # print("JSON file saved successfully.")
    gantt_show()

def get_gantt_se(schedule, machines, factories, data, start_time_index, end_time_index, path="gantt.json", title="gantt", factory=0):
    gantt = dict()
    gantt['machines'] = data['MACHINES']
    gantt['jobs'] = data['JOBS']
    gantt['xlabel'] = 'time'
    gantt['title'] = title
    gantt["packages"] = []
    operation = np.ones((data['JOBS']), dtype='int32') * (-1)
    for index, job in enumerate(schedule):
        if factories[job] != factory:
            continue
        operation[job] += 1
        machine = get_machine(job, operation[job], machines, data)
        package = {
            "start": int(start_time_index[index]),
            "end": int(end_time_index[index]),
            "machine": int(machine),
            "job": int(job)
        }
        gantt["packages"].append(package)
    with open(path, 'w') as json_file:
        json.dump(gantt, json_file, indent=2)
    gantt_show()

# https://csacademy.com/app/graph_editor/
def get_graph_editor(graph, path="graph_editor.txt"):
    with open(path, 'w') as file:
        for u, edges in graph.items():
            for (v, w) in edges:
                file.write(f"{u} {v} {w}\n")
    print("Graph Editor file saved successfully.")

def write_objective(pop, path, data):
    obj = popSort.get_min(pop, -1, data)
    with open(path, 'w') as file:
        file.write(f"{obj}\n")
    # print("Objective value saved successfully.")

def write_population(pop, path, data):
    with open(path, 'w') as file:
        for i, makespan in enumerate(pop[data['objective']]):
            file.write(f"objective: {makespan}\nschedule: {pop['schedules'][i]}\nmachine: {pop['machines'][i]}\nfactories: {pop['factories'][i]}\n")
    # print("Population saved successfully.")

def write_time(time, path):
    with open(path, 'w') as file:
        file.write(f"{time}\n")
    # print("Time saved successfully.")

def graph_view(graph):
    G = nx.DiGraph()
    G.add_weighted_edges_from([(u, v, w) for u, edges in graph.items() for v, w in edges])
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True)
    labels = nx.get_edge_attributes(G, 'weight')
    nx.draw_networkx_edge_labels(G, pos, edge_labels=labels)
    plt.show()

# get which is better solution
# 1: f1 better; 2: f2 better; 0: all
def nds(f1, f2, data):
    op = np.zeros(3)
    for k in range(data['objective_number']):
        if f1[k] > f2[k]:
            op[0] += 1
        elif f1[k] == f2[k]:
            op[1] += 1
        else:
            op[2] += 1
    if op[0] == 0 and op[1] != data['objective_number']:
        return 1
    if op[2] == 0 and op[1] != data['objective_number']:
        return 2
    return 0

def gantt_show():
    def load_data(data_file):
        with open(data_file) as fh:
            data = json.load(fh)

        packages = []
        machine = [pkg['machine'] for pkg in data['packages']]
        job = [pkg['job'] for pkg in data['packages']]
        title = data.get('title', 'Gantt for JSP')
        xticks = data.get('xticks', "")
        machines = data.get('machines', 100)
        labels = [f"machine-{i}" for i in range(machines)]
        jobs = data.get('jobs', 100)
        operations = [0] * jobs

        for pkg in data['packages']:
            packages.append({
                'start': pkg['start'],
                'end': pkg['end'],
                'machine': pkg['machine'],
                'job': pkg['job'],
                'operation': operations[pkg['job']]
            })
            operations[pkg['job']] += 1

        return packages, machine, job, title, xticks, labels, machines, jobs

    def process_data(packages):
        start = [pkg['start'] for pkg in packages]
        end = [pkg['end'] for pkg in packages]
        durations = list(map(sub, end, start))
        ypos = np.arange(machines, 0, -1)

        return start, end, durations, ypos

    def random_color():
        red = random.randint(150, 255)
        green = random.randint(150, 255)
        blue = random.randint(150, 255)
        return "#{:02X}{:02X}{:02X}".format(red, green, blue)

    def render_gantt(packages, machines, start, end, ypos, jobs, xticks, labels):
        def on_hover(event):
            for i, rect in enumerate(rectangles):
                if rect.contains(event)[0]:
                    rect.set_edgecolor('black')
                    rect.set_linewidth(2)
                    txt = 'job:' + str(packages[i]['job']) + '\noperation:' + str(
                        packages[i]['operation']) + '\ntime:[' + str(packages[i]['start']) + ',' + str(
                        packages[i]['end']) + ']'
                    text.set_text(txt)
                    for j, rect1 in enumerate(rectangles):
                        if i == j or packages[i]['job'] != packages[j]['job']:
                            continue
                        rect1.set_edgecolor('red')
                        rect1.set_linewidth(2)
                else:
                    rect.set_edgecolor('none')
                    rect.set_linewidth(1)
            plt.draw()

        fig, ax = plt.subplots()
        ax.yaxis.grid(False)
        ax.xaxis.grid(True)

        rectangles = []
        text = ax.text(0.5, 1.05, '', transform=ax.transAxes, ha='center', va='center', color='black', fontsize=12)

        job_colors = [random_color() for _ in range(jobs)]
        colors = [job_colors[pkg['job'] - 1] for pkg in packages]

        for i, pkg in enumerate(packages):
            rect = mpatches.Rectangle((start[i], machines - pkg['machine'] - 0.25),
                                      end[i] - start[i], 0.5, facecolor=colors[i])
            rectangles.append(rect)
            plt.gca().add_patch(rect)

        plt.rc('font', family='serif', size=15)
        # for i in range(len(start)):
        #     plt.text((end[i] + start[i]) / 2, machines - packages[i]['machine'] - 0.05, str(job[i]))
        for i, rect in enumerate(rectangles):
            x_center = rect.get_x() + rect.get_width() / 2
            y_center = rect.get_y() + rect.get_height() / 2
            plt.text(x_center, y_center, str(job[i]), ha='center', va='center')

        plt.tick_params(axis='both', which='both', bottom='on', top='off', left='off', right='off')
        plt.xlim(0, max(end))
        plt.ylim(0.5, machines + 0.5)
        plt.yticks(ypos, labels)
        fig.canvas.mpl_connect('motion_notify_event', on_hover)

        if xticks:
            plt.xticks(xticks, map(str, xticks))

    def show_plot():
        plt.show()

    data_file = 'gantt.json'
    packages, machine, job, title, xticks, labels, machines, jobs = load_data(data_file)
    start, end, durations, ypos = process_data(packages)
    render_gantt(packages, machines, start, end, ypos, jobs, xticks, labels)
    show_plot()