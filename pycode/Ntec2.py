# Date: 2023/12/22 21:54
# Author: cls1277
# Email: cls1277@163.com
import copy
import random
import numpy as np
import tools
import Graph
import solveSchedule
import evalPop


def neighbor(schedule, machines, factories, data, iter):
    newind_schedule = np.empty((0, len(schedule)), dtype='int32')
    newind_machines = np.empty((0, len(machines)), dtype='int32')
    newind_makespan = np.empty((0, data['objective_number']+1), dtype='int32')

    for factory in range(data['FACTORIES']):

        N = data['sum_operations'] + 1
        graph, PM, PJ, SM, SJ = Graph.init_graph(schedule, machines, factories, factory, data)

        # critical path
        critical_path, _ = Graph.get_distance(graph, 0, N, data, True)

        # delete the first and the last node
        critical_path = critical_path[1:-1]

        nodes_to_indexes = tools.get_nodes_to_indexes(schedule, data)
        indexes_to_nodes = tools.get_indexes_to_nodes(schedule, data)

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

        # init sx+px and px+tx
        sxpx = np.zeros((N))
        pxtx = np.zeros((N))
        for node in range(1, N):
            job, operation = tools.get_job_operation(node, data)
            machine = tools.get_machine(job, operation, machines, data)
            px = tools.get_time(job, operation, machine, 0, data)
            # in my graph, sx includes px
            sx = Graph.get_distance(graph, 0, node, data)
            tx = Graph.get_distance(graph, node, N, data)
            sxpx[node] = sx
            pxtx[node] = px + tx

        # get all operations on each machine
        all_operations_of_machine = {}
        operation = np.ones((data['JOBS']), dtype='int32') * (-1)
        for index, job in enumerate(schedule):
            if factories[job] != factory:
                continue
            operation[job] += 1
            machine = tools.get_machine(job, operation[job], machines, data)
            if machine not in all_operations_of_machine:
                all_operations_of_machine[machine] = []
            all_operations_of_machine[machine].append(index)

        # start doing Nopt1
        # the subscript of v is "node"
        # condition: v has more than 1 candidate machines
        candidate_v = []
        for i in critical_path:
            if len(data['machines'][0][i]) > 1:
                candidate_v.append(i)

        flag = False
        cnt0 = 0
        while 2 * cnt0 < len(candidate_v):
            if flag == True:
                break
            cnt0 += 1
            v = random.choice(candidate_v)
        # for v in candidate_v:

            index_v = nodes_to_indexes[v]
            job_v, operation_v = tools.get_job_operation(v, data)

            for k in data['machines'][0][v]:
                if k not in all_operations_of_machine and k != machines[v-1]:
                    new_machine = np.copy(machines)
                    new_machine[v - 1] = k
                    new_makespan = evalPop.evaluate_ind(schedule, new_machine, factories, data)
                    new_schedule = np.reshape(schedule, (1, -1))
                    newind_schedule = np.concatenate((newind_schedule, new_schedule), axis=0)
                    newind_makespan = np.concatenate((newind_makespan, new_makespan))

                    new_machine = np.reshape(new_machine, (1, -1))
                    newind_machines = np.concatenate((newind_machines, new_machine), axis=0)
                    iter -= 1
                    if iter < 1:
                        if len(newind_schedule) < 1:
                            return -1
                        else:
                            return newind_schedule, newind_machines, newind_makespan, iter

            # get the new graph by moving two edges and adding one edge
            new_graph = copy.deepcopy(graph)
            if PM[v] != -1:
                new_graph = Graph.remove_edge(new_graph, PM[v], v)
            if SM[v] != -1:
                new_graph = Graph.remove_edge(new_graph, v, SM[v])
            if PM[v] != -1 and SM[v] != -1:
                job_smv, operation_smv = tools.get_job_operation(SM[v], data)
                machine_smv = tools.get_machine(job_smv, operation_smv, machines, data)
                Graph.add_edge(new_graph, PM[v], SM[v], tools.get_time(job_smv, operation_smv, machine_smv, 0, data))

            # tools.get_graph_editor(new_graph, path='new_graph_editor.txt')

            # job_v, operation_v = tools.get_job_operation(v, data)
            if PJ[v] == -1:
                new_sv = 0
            else:
                new_sv = Graph.get_distance(new_graph, 0, PJ[v], data)
            new_tv = Graph.get_distance(new_graph, v, N, data)

            # get correct machine and positions to do FN2 by inserting v
            positions = {}
            for machine in data['machines'][0][v]:
                L = set()
                R = set()
                # this machine has no operations
                if machine not in all_operations_of_machine or machine == machines[v-1]:
                    continue
                for index_x in all_operations_of_machine[machine]:
                    x = indexes_to_nodes[index_x]
                    if index_x == index_v:
                        continue
                    if sxpx[x] > new_sv:
                        L.add(index_x)
                        # st.discard(index_x)
                    if pxtx[x] > new_tv:
                        R.add(index_x)
                        # st.discard(index_x)
                # position = list(st)
                if L.isdisjoint(R):
                    position = list(set(all_operations_of_machine[machine]) - (L | R))
                else:
                    position = list(L & R)
                if index_v in position:
                    position.remove(index_v)
                if len(position) > 0:
                    positions[machine] = copy.deepcopy(position)

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

            vis = [False] * data['sum_operations']
            st_index_copy = np.copy(start_time_index)
            et_index_copy = np.copy(end_time_index)
            for machine in positions:
                u = positions[machine][0]
                if u in critical_path:
                    continue
                # 记忆化搜索：对每个有希望后移的工序搜索一遍
                if not vis[u]:
                    vis[u] = True
                    solveSchedule.delay_schedule(schedule, machines, factories, u, SJ_index, SM_index, st_index_copy, et_index_copy,
                                                 vis, critical_path, data)

            time_v_origin = tools.get_time(job_v, operation_v, machines[v-1], 0, data)

            # "k" is the new machine
            cnt1 = 0
            while 2 * cnt1 < len(positions.keys()):
                if flag == True:
                    break
                cnt1 += 1
                k = random.choice(list(positions.keys()))
            # for k in positions:
                if iter == 0:
                    break

                time_v_k = tools.get_time(job_v, operation_v, k, 0, data)

                cnt2 = 0
                while 2 * cnt2 < len(positions[k]):
                    if flag == True:
                        break
                    cnt2 += 1
                    u = random.choice(positions[k])
                # for u in positions[k]:
                    if PM_index[u] == -1:
                        dettime = st_index_copy[u]
                    else:
                        dettime = st_index_copy[u] - end_time_index[PM_index[u]]
                    if (dettime >= time_v_k) or (time_v_origin + dettime >= data['MACHINES'] * (time_v_k - dettime)):
                        # 不能到SJ的后面去
                        if (SJ_index[index_v] == -1) or (end_time_index[index_v] + time_v_k <= st_index_copy[SJ_index[index_v]]):
                            new_machine = np.copy(machines)
                            new_machine[v - 1] = k
                            new_schedule, new_makespan = solveSchedule.backward_schedule(schedule, new_machine, factories, PM_index, PJ_index, SM_index,
                                                            SJ_index, u, index_v, data, factory=factory)
                            new_schedule = np.reshape(new_schedule, (1, -1))
                            newind_schedule = np.concatenate((newind_schedule, new_schedule), axis=0)
                            newind_makespan = np.concatenate((newind_makespan, new_makespan))

                            new_machine = np.reshape(new_machine, (1, -1))
                            newind_machines = np.concatenate((newind_machines, new_machine), axis=0)
                            iter -= 1
                            flag = True

                cnt3 = 0
                while 2 * cnt3 < len(positions[k]):
                    if flag == True:
                        break
                    cnt3 += 1
                    u = random.choice(positions[k])
                # for u in reversed(positions[k]):
                    if SM_index[u] == -1:
                        # int32 max
                        dettime = 2147483647
                    else:
                        dettime = st_index_copy[SM_index[u]] - end_time_index[u]
                    if (dettime >= time_v_k) or (dettime >= data['MACHINES'] * (time_v_k - dettime)):
                        # 不能到SJ的后面去
                        if (PJ_index[index_v] == -1) or (et_index_copy[u] >= end_time_index[PJ_index[index_v]]):
                            new_machine = np.copy(machines)
                            new_machine[v - 1] = k
                            new_schedule, new_makespan = solveSchedule.forward_schedule(schedule, new_machine, factories,
                                                                                        PM_index, PJ_index, SM_index,
                                                                                        SJ_index, index_v, u, data,
                                                                                        factory=factory)
                            new_schedule = np.reshape(new_schedule, (1, -1))
                            newind_schedule = np.concatenate((newind_schedule, new_schedule), axis=0)
                            newind_makespan = np.concatenate((newind_makespan, new_makespan))

                            new_machine = np.reshape(new_machine, (1, -1))
                            newind_machines = np.concatenate((newind_machines, new_machine), axis=0)
                            iter -= 1
                            flag = True

    if len(newind_schedule) < 1:
        return -1
    else:
        return newind_schedule, newind_machines, newind_makespan, iter