import numpy as np
from queue import Queue

# add an edge from u to v and its length = w
def add_edge(graph, u, v, w):
    if u not in graph:
        graph[u] = []
    graph[u].append((v, w))

# remove an edge from u to v
def remove_edge(graph, u, v):
    if u in graph:
        graph[u] = [(neighbor, weight) for (neighbor, weight) in graph[u] if neighbor != v]
    return graph

def find_path(pre, u, v):
    path = []
    current = v
    while current is not None:
        path.append(current)
        current = pre[current]
    return path[::-1]

# DAG: topological order
def get_distance(graph, s, t, data, get_path = False):
    N = data['sum_operations'] + 1
    ind = np.zeros(N+1, dtype='int32')
    q = Queue()

    for u in graph:
        for (v, w) in graph[u]:
            ind[v] += 1
    for u in graph:
        if ind[u] == 0:
            q.put(u)

    dp = {node: float('-inf') for node in range(N+1)}
    pre = {node: None for node in range(N+1)}
    dp[s] = 0

    while q.empty() == False:
        # get and erase (x)
        x = q.get()
        for (v, w) in graph[x]:
            ind[v] -= 1
            if ind[v] == 0:
                q.put(v)
            if dp[x] + w > dp[v]:
                pre[v] = x
                dp[v] = dp[x] + w
    if get_path == False:
        return dp[t]
    else:
        return find_path(pre, s, t), dp[t]

# left: the length of (i,j) is p_i, otherwise right is p_j
def init_graph(schedule, machines, factories, factory, data, left=False):
    import tools

    graph = {}
    N = data['sum_operations'] + 1
    PM = np.ones((N + 1), dtype='int32') * (-1)
    PJ = np.ones((N + 1), dtype='int32') * (-1)
    SM = np.ones((N + 1), dtype='int32') * (-1)
    SJ = np.ones((N + 1), dtype='int32') * (-1)
    for job in range(data['JOBS']):
        if factories[job] != factory:
            continue
        if left == False:
            first_node = tools.get_node(job, 0, data)
            machine = tools.get_machine(job, 0, machines, data)
            first_time = tools.get_time(job, 0, machine, factory, data)
            add_edge(graph, 0, first_node, first_time)
            last_node = tools.get_node(job, data['operations'][job] - 1, data)
            add_edge(graph, last_node, N, 0)
            for operation in range(data['operations'][job]):
                node = tools.get_node(job, operation, data)
                machine = tools.get_machine(job, operation, machines, data)
                time = tools.get_time(job, operation, machine, factory, data)
                if operation == 0:
                    PJ[node] = 0
                    SJ[node] = node + 1
                elif operation == data['operations'][job]-1:
                    PJ[node] = node - 1
                    SJ[node] = N
                    add_edge(graph, node-1, node, time)
                else :
                    PJ[node] = node - 1
                    SJ[node] = node + 1
                    add_edge(graph, node-1, node, time)
        else :
            last_node = tools.get_node(job, data['operations'][job]-1, data)
            machine = tools.get_machine(job, data['operations'][job]-1, machines, data)
            last_time = tools.get_time(job, data['operations'][job]-1, machine, factory, data)
            add_edge(graph, last_node, N, last_time)
            first_node = tools.get_node(job, 0, data)
            add_edge(graph, 0, first_node, 0)
            for operation in range(data['operations'][job]):
                node = tools.get_node(job, operation, data)
                if operation == 0:
                    PJ[node] = 0
                    SJ[node] = node + 1
                    continue
                machine = tools.get_machine(job, operation-1, machines, data)
                time = tools.get_time(job, operation-1, machine, factory, data)
                if 0 < operation < data['operations'][job] - 1:
                    PJ[node] = node - 1
                    SJ[node] = node + 1
                    add_edge(graph, node-1, node, time)
                else:
                    PJ[node] = node - 1
                    SJ[node] = N
                    add_edge(graph, node-1, node, time)

    endtime_job = np.zeros((data['JOBS']))
    endtime_machine = np.zeros((data['MACHINES']))
    last_node_machine = np.ones((data['MACHINES']), dtype='int32') * (-1)
    operation = np.ones((data['JOBS']), dtype='int32') * (-1)

    for index, job in enumerate(schedule):
        if factories[job] != factory:
            continue
        operation[job] += 1
        machine = tools.get_machine(job, operation[job], machines, data)
        time = tools.get_time(job, operation[job], machine, factory, data)
        node = tools.get_node(job, operation[job], data)
        PM[node] = last_node_machine[machine]
        if last_node_machine[machine] != -1:
            SM[last_node_machine[machine]] = node
        last_node_machine[machine] = node
        endtime = max(endtime_job[job], endtime_machine[machine]) + time
        endtime_job[job] = endtime_machine[machine] = endtime

    for node in range(1, N):
        if PM[node] == -1:
            continue
        if left == False:
            job, operation = tools.get_job_operation(node, data)
        else:
            job, operation = tools.get_job_operation(PM[node], data)
        machine = tools.get_machine(job, operation, machines, data)
        time = tools.get_time(job, operation, machine, factory, data)
        add_edge(graph, PM[node], node, time)

    # adding N, the end point, into graph, solving some problems
    graph[N] = []

    return graph, PM, PJ, SM, SJ

# Separate the points on the path according to the machining machine
def get_path_machine(path, machines, data):
    import tools

    path_machines = {}
    for node in path:
        job, operation = tools.get_job_operation(node, data)
        machine = tools.get_machine(job, operation, machines, data)
        if machine not in path_machines:
            path_machines[machine] = []
        path_machines[machine].append(node)
    return path_machines

def get_path_blocks(path, machines, data):
    import tools

    # critical block
    pre_machine = -1
    now_block = 0
    path_blocks = {}

    # devide critical path by machines
    # get all of critical blocks
    for node in path:
        job, operation = tools.get_job_operation(node, data)
        machine = tools.get_machine(job, operation, machines, data)

        # the first critical block
        if pre_machine != machine:
            pre_machine = machine
            now_block += 1
            path_blocks[now_block] = [node]
        else:
            path_blocks[now_block].append(node)

    return path_blocks