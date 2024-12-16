# Date: 2024/5/19 23:51
# Author: cls1277
# Email: cls1277@163.com

import readData
import evalPop
import numpy as np
import tools

def get_start_end_time(schedule, machines, factories, data, factory):
    start_time = np.zeros((data['sum_operations']), dtype='int32')
    end_time = np.zeros((data['sum_operations']), dtype='int32')

    endtime_job = np.zeros((data['JOBS']))
    endtime_machine = np.zeros((data['MACHINES']))
    operation = np.ones((data['JOBS']), dtype='int32') * (-1)
    for index, job in enumerate(schedule):
        if factories[job] != factory:
            continue
        operation[job] += 1
        machine = tools.get_machine(job, operation[job], machines, data)
        time = tools.get_time(job, operation[job], machine, factories[job], data)

        # node = get_node(job, operation[job], data)
        start_time[index] = max(endtime_job[job], endtime_machine[machine])

        end_time[index] = endtime = start_time[index] + time
        endtime_job[job] = endtime_machine[machine] = endtime

    return start_time, end_time

head = "\\documentclass{article}\n\\usepackage{tikz,amsmath,siunitx}\n\\usetikzlibrary{arrows,decorations,backgrounds,patterns,matrix,shapes,fit,calc,shadows,plotmarks}\n\\usepackage[graphics,tightpage,active]{preview}\n\\usetikzlibrary{arrows.meta}\n\n\\PreviewEnvironment{tikzpicture}\n\\PreviewEnvironment{equation}\n\\PreviewEnvironment{equation*}\n\\newlength{\imagewidth}\n\\newlength{\imagescale}\n\\pagestyle{empty}\n\\thispagestyle{empty}\n\n% GNUPLOT required\n\\begin{document}\n\t\\pagestyle{empty}\n\n\t\\begin{tikzpicture}[\n\t\tdot/.style={circle,minimum size=8pt}]\n"
print(head)

arrays = []
data = readData.read_data('DHFJSP', '10J2F', 'makespan+TEC')
# file_path = 'C:/cls/cls1277/DHFJS/model-code/NS3/result/gantt/makespan.txt'
file_path = 'C:/cls/cls1277/DHFJS/model-code/NS3/result/gantt/TEC.txt'

colors = ['yellow!50', 'blue!50', 'orange!50', 'gray!50', 'pink!50', 'red!50', 'green!50', 'purple!50', 'cyan!50', 'white!50', 'yellow', 'blue', 'orange', 'gray', 'pink', 'red', 'green', 'purple', 'cyan', 'white']

with open(file_path, 'r') as file:
    content = file.read()
    lines = content.split("\n")
    for line in lines:
        numbers = line.split()
        array = np.array([int(num) for num in numbers])
        arrays.append(array)

factories = arrays[0]
machines = arrays[1]
schedule = arrays[2]
obj = evalPop.evaluate_ind(schedule, machines, factories, data)
mksp = obj[0, 0]

for i in range(0, int(mksp)+1):
    print('\coordinate (a%d) at (%d,0);' % (i, i))
for i in range(0, 5):
    print('\coordinate (b%d) at (0,%f);' % (i+1, i+0.5))
print('\draw[-latex][very thick] (-0.5,0) -- (%d,0) node[below] {\small $F1$};' % (mksp+1))
print('\draw[-latex][very thick] (0,-0) -- (0,%d) node[above] {\small $Machine$};' % (6))

for i in range(0, int(mksp)+1):
    print('\draw (a%d) node [below]{%d} -- ++(0, 3pt) ;' % (i, i))
for i in range(0, 5):
    print('\draw (b%d) node [left]{$M_%d$} -- ++(0, 3pt) ;' % (i+1, i+1))

factory = 1
st, et = get_start_end_time(schedule, machines, factories, data, factory)
operation = np.ones((data['JOBS']), dtype='int32') * (-1)
for index, job in enumerate(schedule):
    if factories[job] != factory:
        continue
    operation[job] += 1
    machine = tools.get_machine(job, operation[job], machines, data)
    time = tools.get_time(job, operation[job], machine, factories[job], data)
    print('\\filldraw[fill = %s][thick] (%d,%d) rectangle (%d,%f) node[left, black, xshift=%dpt, yshift = -12pt] {\small $O_{%d,%d}$};' % (colors[job%len(colors)], st[index], machine+factory*5, et[index], machine+0.75+factory*5, -(1+13*(time-1)), job, operation[job]))


tail = "\t\\end{tikzpicture}\n\n\\end{document}"
print(tail)