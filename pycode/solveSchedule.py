import numpy as np
import tools
import evalPop
import Graph

def mb_dfs(x, SM_index, SJ_index, u, v, vis, is_move):
    is_move[x] = 1
    # The condition ensures that it will not return to the machines of u and v again
    if x != u and u < SM_index[x] < v and vis[SM_index[x]] == 0:
        vis[SM_index[x]] = 1
        mb_dfs(SM_index[x], SM_index, SJ_index, u, v, vis, is_move)
    if u < SJ_index[x] < v and vis[SJ_index[x]] == 0:
        vis[SJ_index[x]] = 1
        mb_dfs(SJ_index[x], SM_index, SJ_index, u, v, vis, is_move)

'''
Given a sequence S between u and v, 
return the sequence s1 that needs to follow u backward and the sequence s2 that does not need to be backward
'''
def move_back(SM_index, SJ_index, u, v, data):
    vis = [0] * data['sum_operations']
    is_move = [0] * data['sum_operations']
    vis[u] = 1
    mb_dfs(u, SM_index, SJ_index, u, v, vis, is_move)
    return is_move

# a forward interchange if u is moved right after v.
def forward_schedule(schedule, machines, factories, PM_index, PJ_index, SM_index, SJ_index, u, v, data, **kwargs):
    if u < v:
        is_move = move_back(SM_index, SJ_index, u, v, data)[u:v]
        S = schedule[u:v]
        move = [S[i] for i in range(len(S)) if is_move[i] == 1]
        not_move = [S[i] for i in range(len(S)) if is_move[i] == 0]
        schedule = np.concatenate((schedule[:u], not_move, np.array([schedule[v]]), move, schedule[v+1:]))
        schedule = schedule.astype(np.int32)
    else :
        is_move = move_for(PM_index, PJ_index, v, u, data)[v+1:u+1]
        S = schedule[v+1:u+1]
        move = [S[i] for i in range(len(S)) if is_move[i] == 1]
        not_move = [S[i] for i in range(len(S)) if is_move[i] == 0]
        schedule = np.concatenate((schedule[:v], np.array([schedule[v]]), move, not_move, schedule[u+1:]))
        schedule = schedule.astype(np.int32)
    if 'factory' in kwargs:
        factory = kwargs['factory']
        N = data['sum_operations'] + 1
        graph, PM, PJ, SM, SJ = Graph.init_graph(schedule, machines, factories, factory, data, True)

        # critical path
        critical_path, _ = Graph.get_distance(graph, 0, N, data, True)

        # delete the first and the last node
        critical_path = critical_path[1:-1]

        nodes_to_indexes = tools.get_nodes_to_indexes(schedule, data)
        indexes_to_nodes = tools.get_indexes_to_nodes(schedule, data)

        # start_time and end_time
        # nodes -> indexes
        start_time_index = np.zeros((len(schedule)), dtype='int32')
        end_time_index = np.zeros((len(schedule)), dtype='int32')
        operations_machines = {}  # index
        start_time_nodes = np.zeros((data['sum_operations'] + 2), dtype='int32')
        end_time_nodes = np.zeros((data['sum_operations'] + 2), dtype='int32')
        endtime_job = np.zeros((data['JOBS']))
        endtime_machine = np.zeros((data['MACHINES']))
        operation = np.ones((data['JOBS']), dtype='int32') * (-1)
        for index, job in enumerate(schedule):
            if factories[job] != factory:
                continue
            operation[job] += 1
            machine = tools.get_machine(job, operation[job], machines, data)
            if machine not in operations_machines:
                operations_machines[machine] = []
            operations_machines[machine].append(index)
            time = tools.get_time(job, operation[job], machine, 0, data)
            node = tools.get_node(job, operation[job], data)
            start_time_nodes[node] = max(endtime_job[job], endtime_machine[machine])
            end_time_nodes[node] = endtime = start_time_nodes[node] + time
            endtime_job[job] = endtime_machine[machine] = endtime

        for node, st in enumerate(start_time_nodes):
            if 0 < node < N:
                start_time_index[nodes_to_indexes[node]] = st
        for node, et in enumerate(end_time_nodes):
            if 0 < node < N:
                end_time_index[nodes_to_indexes[node]] = et

        # devide critical path by machines
        critical_path_machines = Graph.get_path_machine(critical_path, machines, data)

        for i, node in enumerate(critical_path):
            critical_path[i] = nodes_to_indexes[node]
        for machine in critical_path_machines:
            for i, node in enumerate(critical_path_machines[machine]):
                critical_path_machines[machine][i] = nodes_to_indexes[node]

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
        vis = [False] * data['sum_operations']
        st_index_copy = np.copy(start_time_index)
        et_index_copy = np.copy(end_time_index)
        for machine in operations_machines:
            w = operations_machines[machine][0]
            if w in critical_path:
                continue
            # 记忆化搜索：对每个有希望后移的工序搜索一遍
            if not vis[w]:
                vis[w] = True
                delay_schedule(schedule, machines, factories, w, SJ_index, SM_index, st_index_copy, et_index_copy, vis, critical_path, data)
        return schedule, evalPop.TEC_se(schedule, machines, factories, data, (4, 1), st_index_copy, et_index_copy)
    else:
        return schedule, evalPop.evaluate_ind(schedule, machines, factories, data)

# --------------

def mf_dfs(x, PM_index, PJ_index, u, v, vis, is_move):
    is_move[x] = 1
    # The condition ensures that it will not return to the machines of u and v again
    if x != v and u < PM_index[x] < v and vis[PM_index[x]] == 0:
        vis[PM_index[x]] = 1
        mf_dfs(PM_index[x], PM_index, PJ_index, u, v, vis, is_move)
    if u < PJ_index[x] < v and vis[PJ_index[x]] == 0:
        vis[PJ_index[x]] = 1
        mf_dfs(PJ_index[x], PM_index, PJ_index, u, v, vis, is_move)

def move_for(PM_index, PJ_index, u, v, data):
    vis = [0] * data['sum_operations']
    is_move = [0] * data['sum_operations']
    vis[v] = 1
    mf_dfs(v, PM_index, PJ_index, u, v, vis, is_move)
    return is_move

# a backward interchange if v is moved right before u
def backward_schedule(schedule, machines, factories, PM_index, PJ_index, SM_index, SJ_index, u, v, data, **kwargs):
    if u < v:
        is_move = move_for(PM_index, PJ_index, u, v, data)[u+1:v+1]
        S = schedule[u+1:v+1]
        move = [S[i] for i in range(len(S)) if is_move[i] == 1]
        not_move = [S[i] for i in range(len(S)) if is_move[i] == 0]
        schedule = np.concatenate((schedule[:u], move, np.array([schedule[u]]), not_move, schedule[v+1:]))
        schedule = schedule.astype(np.int32)
    else:
        is_move = move_back(SM_index, SJ_index, v, u, data)[v:u]
        S = schedule[v:u]
        move = [S[i] for i in range(len(S)) if is_move[i] == 1]
        not_move = [S[i] for i in range(len(S)) if is_move[i] == 0]
        schedule = np.concatenate((schedule[:v], not_move, move, np.array([schedule[u]]), schedule[u+1:]))
        schedule = schedule.astype(np.int32)
    if 'eval' in kwargs:
        if kwargs['eval'] == False:
            return schedule
    if 'factory' in kwargs:
        factory = kwargs['factory']
        N = data['sum_operations'] + 1
        graph, PM, PJ, SM, SJ = Graph.init_graph(schedule, machines, factories, factory, data, True)

        # critical path
        critical_path, _ = Graph.get_distance(graph, 0, N, data, True)

        # delete the first and the last node
        critical_path = critical_path[1:-1]

        nodes_to_indexes = tools.get_nodes_to_indexes(schedule, data)
        indexes_to_nodes = tools.get_indexes_to_nodes(schedule, data)

        # start_time and end_time
        # nodes -> indexes
        start_time_index = np.zeros((len(schedule)), dtype='int32')
        end_time_index = np.zeros((len(schedule)), dtype='int32')
        operations_machines = {}  # index
        start_time_nodes = np.zeros((data['sum_operations'] + 2), dtype='int32')
        end_time_nodes = np.zeros((data['sum_operations'] + 2), dtype='int32')
        endtime_job = np.zeros((data['JOBS']))
        endtime_machine = np.zeros((data['MACHINES']))
        operation = np.ones((data['JOBS']), dtype='int32') * (-1)
        for index, job in enumerate(schedule):
            if factories[job] != factory:
                continue
            operation[job] += 1
            machine = tools.get_machine(job, operation[job], machines, data)
            if machine not in operations_machines:
                operations_machines[machine] = []
            operations_machines[machine].append(index)
            time = tools.get_time(job, operation[job], machine, 0, data)
            node = tools.get_node(job, operation[job], data)
            start_time_nodes[node] = max(endtime_job[job], endtime_machine[machine])
            end_time_nodes[node] = endtime = start_time_nodes[node] + time
            endtime_job[job] = endtime_machine[machine] = endtime

        for node, st in enumerate(start_time_nodes):
            if 0 < node < N:
                start_time_index[nodes_to_indexes[node]] = st
        for node, et in enumerate(end_time_nodes):
            if 0 < node < N:
                end_time_index[nodes_to_indexes[node]] = et

        # devide critical path by machines
        critical_path_machines = Graph.get_path_machine(critical_path, machines, data)

        for i, node in enumerate(critical_path):
            critical_path[i] = nodes_to_indexes[node]
        for machine in critical_path_machines:
            for i, node in enumerate(critical_path_machines[machine]):
                critical_path_machines[machine][i] = nodes_to_indexes[node]

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

        vis = [False] * data['sum_operations']
        st_index_copy = np.copy(start_time_index)
        et_index_copy = np.copy(end_time_index)
        for machine in operations_machines:
            w = operations_machines[machine][0]
            if w in critical_path:
                continue
            # 记忆化搜索：对每个有希望后移的工序搜索一遍
            if not vis[w]:
                vis[w] = True
                delay_schedule(schedule, machines, factories, w, SJ_index, SM_index, st_index_copy, et_index_copy, vis, critical_path, data)
        return schedule, evalPop.TEC_se(schedule, machines, factories, data, (4, 1), st_index_copy, et_index_copy)
    else:
        return schedule, evalPop.evaluate_ind(schedule, machines, factories, data)

# swap interchange between u and v, u < v
def swap_schedule(schedule, machines, factories, u, v, data):
    schedule[u], schedule[v] = schedule[v], schedule[u]
    return schedule, evalPop.evaluate_ind(schedule, machines, factories, data)

def delay_schedule(schedule, machines, factories, u, SJ_index, SM_index, st_index, et_index, vis, critical_path, data):
    if (SJ_index[u] != -1) and (vis[SJ_index[u]] == False) and (SJ_index[u] not in critical_path):
        vis[SJ_index[u]] = True
        delay_schedule(schedule, machines, factories, SJ_index[u], SJ_index, SM_index, st_index, et_index, vis, critical_path, data)
    if (SM_index[u] != -1) and (vis[SM_index[u]] == False) and (SM_index[u] not in critical_path):
        vis[SM_index[u]] = True
        delay_schedule(schedule, machines, factories, SM_index[u], SJ_index, SM_index, st_index, et_index, vis, critical_path, data)
    et = 2147483647
    if SJ_index[u] != -1:
        et = min(et, st_index[SJ_index[u]])
    if SM_index[u] != -1:
        et = min(et, st_index[SM_index[u]])
    if et == 2147483647:
        et = et_index[u]
    else:
        et = max(et, et_index[u])
    node = tools.get_index_to_node(u, schedule, data)
    job_u, operation_u = tools.get_job_operation(node, data)
    et_index[u] = et
    st_index[u] = et_index[u] - tools.get_time(job_u, operation_u, machines[node-1], factories[job_u], data)