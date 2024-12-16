# coding:utf-8
#energy saving by full-active scheduling
import copy

import numpy as np

# coding:utf-8
import numpy as np

def mylistRound(arr):
    l=len(arr)
    for i in range(l):
        arr[i]=round(arr[i])
    return arr

def find_all_index(arr, item):
    return [i for i, a in enumerate(arr) if a == item]

def find_all_index_not(arr, item):
    l=len(arr)
    flag=np.zeros(l)
    index=find_all_index(arr,item)
    flag[index]=1
    not_index=find_all_index(flag,0)
    return not_index

def NDS(fit1,fit2):
    v=0
    dom_less = 0;
    dom_equal = 0;
    dom_more = 0;
    for k in range(2):
        if fit1[k] > fit2[k]:
            dom_more = dom_more + 1;
        elif fit1[k] == fit2[k]:
            dom_equal = dom_equal + 1;
        else:
            dom_less = dom_less + 1;

    if dom_less == 0 and dom_equal != 2:
        v = 2
    if dom_more == 0 and dom_equal != 2:
        v = 1
    return v

def Ismemeber(item,list):
    l=len(list)
    flag=0
    for i in range(l):
        if list[i]==item:
            flag=1
            break
    return flag

def DeleteReapt(QP,QM,QF,QFit,ps):
    row=np.size(QFit,0)
    i=0
    while i<row:
        if i>=row:
            #print('break 1')
            break

        F=QFit[i,:]
        j=i+1
        while j<row:
            if QFit[j][0]==F[0] and QFit[j][1]==F[1]:
                QP = np.delete(QP, j, axis=0)
                QM = np.delete(QM, j, axis=0)
                QF = np.delete(QF, j, axis=0)
                QFit = np.delete(QFit, j, axis=0)
                j=j-1
                row=row-1
                if row<2*ps+1:
                    break
            j=j+1
        i=i+1
        if row < 2 * ps + 1:
            #print('break 2')
            break
    return QP,QM,QF,QFit

def DeleteReaptE(QP,QM,QF,QFit): #for elite strategy
    row=np.size(QFit,0)
    i=0
    while i<row:
        if i>=row:
            #print('break 1')
            break

        F=QFit[i,:]
        j=i+1
        while j<row:
            if QFit[j][0]==F[0] and QFit[j][1]==F[1]:
                QP = np.delete(QP, j, axis=0)
                QM = np.delete(QM, j, axis=0)
                QF = np.delete(QF, j, axis=0)
                QFit = np.delete(QFit, j, axis=0)
                j=j-1
                row=row-1
            j=j+1
        i=i+1

    return QP,QM,QF,QFit

def pareto(fitness):
    PF=[]
    L=np.size(fitness,axis=0)
    pn=np.zeros(L,dtype=int)
    for i in range(L):
        for j in range(L):
            dom_less = 0;
            dom_equal = 0;
            dom_more = 0;
            for k in range(2):#number of objectives
                if (fitness[i][k] > fitness[j][k]):
                    dom_more = dom_more + 1
                elif(fitness[i][k] == fitness[j][k]):
                    dom_equal = dom_equal + 1
                else:
                    dom_less = dom_less + 1

            if dom_less == 0 and dom_equal != 2: # i is dominated by j
                pn[i] = pn[i] + 1;
        if pn[i] == 0: # add i into pareto front
            PF.append(i)
    return PF

class Machine(object):
    def __init__(self):
        self.Op=[]
        self.GapT=[]
        self.MFT=[]

def SAS2AS(p_chrom,m_chrom,FJ,N,H,TM,time,f_index):
    SH = len(p_chrom)
    e=0
    opmax = int(max(H))
    # initial finish time matrix to record the finish time of each operation
    finish = np.zeros(shape=(N, opmax))
    start = np.zeros(shape=(N, opmax))
    mt = np.zeros(TM)
    MA=[]
    for i in range(TM):# creat a object array
        MA.append(Machine())

    s1 = p_chrom
    s2 = np.zeros(SH, dtype=int)
    p = np.zeros(N, dtype=int)
    for i in range(SH):
        p[s1[i]] = p[s1[i]] + 1
        s2[i] = p[s1[i]]
    mm = np.zeros(SH, dtype=int)
    for i in range(SH):
        t1 = s1[i]
        t2 = s2[i]
        t4 = 0
        for k in range(t1):  # sum from 0 to t1-1
            t4 = t4 + H[k]
        mm[i] = m_chrom[t4 + t2 - 1]
    #start decoding
    for i in range(SH):
        if s2[i]==1:
            ON=len(MA[mm[i]].Op)
            if ON>0:
                t=time[f_index][s1[i]][s2[i]-1][mm[i]]
                Index1=-1
                for j in range(ON):
                    if MA[mm[i]].GapT[j]-t>0:
                        Index1=j;break
                if Index1!=-1: #insert the operation
                    Index1=MA[mm[i]].Op[Index1]
                    tmp=s1[i]
                    for j in range(i,Index1,-1):
                        s1[j]=s1[j-1]
                    s1[Index1]=tmp
                    tmp=s2[i]
                    for j in range(i,Index1,-1):
                        s2[j]=s2[j-1]
                    s2[Index1]=tmp
                    tmp = mm[i]
                    for j in range(i, Index1, -1):
                        mm[j] = mm[j - 1]
                    mm[Index1] = tmp
                    for j in range(ON):
                        if MA[mm[Index1]].Op[j] >= Index1:
                            MA[mm[Index1]].Op[j] = MA[mm[Index1]].Op[j] + 1
                    for k in range(TM):
                        if k != mm[Index1]:
                            ON2 = len(MA[k].Op)
                            for h in range(ON2):
                                if MA[k].Op[h] > Index1 and MA[k].Op[h] < i:
                                    MA[k].Op[h] = MA[k].Op[h] + 1
                    MA[mm[Index1]].Op.append(Index1)
                    MA[mm[Index1]].GapT.append(0)
                    MA[mm[Index1]].MFT.append(0)
                    MA[mm[Index1]].Op.sort()  # sort ascend
                    IIndex = find_all_index(MA[mm[Index1]].Op, Index1)
                    if IIndex[0] == 0:
                        start[s1[Index1]][s2[Index1] - 1] = 0
                    else:
                        LastOp = MA[mm[Index1]].Op[IIndex[0] - 1]
                        start[s1[Index1]][s2[Index1] - 1] = max(0, finish[s1[LastOp]][s2[LastOp] - 1])
                    finish[s1[Index1]][s2[Index1] - 1] = t + start[s1[Index1]][s2[Index1] - 1]
                    ON = ON + 1
                    for j in range(ON):
                        Index1 = MA[mm[Index1]].Op[j]
                        if j == 0:
                            MA[mm[Index1]].GapT[j] = 0
                        else:
                            LastOp = MA[mm[Index1]].Op[j - 1]
                            MA[mm[Index1]].GapT[j] = start[s1[Index1]][s2[Index1] - 1] - finish[s1[LastOp]][s2[LastOp] - 1]
                        MA[mm[Index1]].MFT[j] = finish[s1[Index1]][s2[Index1] - 1]
                    mt[mm[Index1]] = MA[mm[Index1]].MFT[ON-1]
                else: #Index==-1
                    start[s1[i]][s2[i]-1]=MA[mm[i]].MFT[ON-1]
                    mt[mm[i]]=start[s1[i]][s2[i]-1]+time[f_index][s1[i]][s2[i]-1][mm[i]]
                    finish[s1[i]][s2[i] - 1]=mt[mm[i]]
                    MA[mm[i]].Op.append(i)
                    MA[mm[i]].GapT.append(0)
                    MA[mm[i]].MFT.append(mt[mm[i]])
            else: #ON=0
                mt[mm[i]] = time[f_index][s1[i]][s2[i] - 1][mm[i]]
                start[s1[i]][s2[i] - 1]=0
                finish[s1[i]][s2[i] - 1] = mt[mm[i]]
                MA[mm[i]].Op.append(i)
                MA[mm[i]].GapT.append(0)
                MA[mm[i]].MFT.append(mt[mm[i]])
        else: #s2[i]!=1
            ON = len(MA[mm[i]].Op)
            if ON>0:
                t=time[f_index][s1[i]][s2[i]-1][mm[i]]
                Index1=-1
                for j in range(ON):
                    if MA[mm[i]].GapT[j]-t>0:
                        if ON==1 or j==0:
                            tmp=finish[s1[i]][s2[i]-2]
                        else:
                            tmp = finish[s1[i]][s2[i] - 2]-MA[mm[i]].MFT[j-1]
                        if MA[mm[i]].GapT[j]-t-tmp>0:
                            Index1=j;break
                if Index1 != -1:  # insert the operation
                    Index1 = MA[mm[i]].Op[Index1]
                    tmp = s1[i]
                    for j in range(i, Index1, -1):
                        s1[j] = s1[j - 1]
                    s1[Index1] = tmp
                    tmp = s2[i]
                    for j in range(i, Index1, -1):
                        s2[j] = s2[j - 1]
                    s2[Index1] = tmp
                    tmp = mm[i]
                    for j in range(i, Index1, -1):
                        mm[j] = mm[j - 1]
                    mm[Index1] = tmp
                    for j in range(ON):
                        if MA[mm[Index1]].Op[j] >= Index1:
                            MA[mm[Index1]].Op[j] = MA[mm[Index1]].Op[j] + 1
                    for k in range(TM):
                        if k != mm[Index1]:
                            ON2 = len(MA[k].Op)
                            for h in range(ON2):
                                if MA[k].Op[h] > Index1 and MA[k].Op[h] < i:
                                    MA[k].Op[h] = MA[k].Op[h] + 1
                    MA[mm[Index1]].Op.append(Index1)
                    MA[mm[Index1]].GapT.append(0)
                    MA[mm[Index1]].MFT.append(0)
                    MA[mm[Index1]].Op.sort()  # sort ascend
                    IIndex = find_all_index(MA[mm[Index1]].Op, Index1)
                    if IIndex[0] == 0:
                        start[s1[Index1]][s2[Index1] - 1] = max(finish[s1[Index1]][s2[Index1]-2], 0)
                    else:
                        LastOp = MA[mm[Index1]].Op[IIndex[0] - 1]
                        start[s1[Index1]][s2[Index1] - 1] = max(finish[s1[Index1]][s2[Index1]-2], finish[s1[LastOp]][s2[LastOp] - 1])
                    finish[s1[Index1]][s2[Index1] - 1] = t + start[s1[Index1]][s2[Index1] - 1]
                    ON = ON + 1
                    for j in range(ON):
                        Index1 = MA[mm[Index1]].Op[j]
                        if j == 0:
                            MA[mm[Index1]].GapT[j] = 0
                        else:
                            LastOp = MA[mm[Index1]].Op[j - 1]
                            MA[mm[Index1]].GapT[j] = start[s1[Index1]][s2[Index1] - 1] - finish[s1[LastOp]][s2[LastOp] - 1]
                        MA[mm[Index1]].MFT[j] = finish[s1[Index1]][s2[Index1] - 1]
                    mt[mm[Index1]] = MA[mm[Index1]].MFT[ON-1]
                else:  # Index==-1
                    start[s1[i]][s2[i] - 1] = max(MA[mm[i]].MFT[ON-1],finish[s1[i]][s2[i]-2])
                    mt[mm[i]] = start[s1[i]][s2[i] - 1] + time[f_index][s1[i]][s2[i] - 1][mm[i]]
                    finish[s1[i]][s2[i] - 1] = mt[mm[i]]
                    MA[mm[i]].Op.append(i)
                    gap=start[s1[i]][s2[i] - 1]-MA[mm[i]].MFT[ON-1]
                    MA[mm[i]].GapT.append(gap)
                    MA[mm[i]].MFT.append(mt[mm[i]])
            else:  # ON=0
                mt[mm[i]] =finish[s1[i]][s2[i] - 2]+time[f_index][s1[i]][s2[i] - 1][mm[i]]
                start[s1[i]][s2[i] - 1] = finish[s1[i]][s2[i] - 2]
                finish[s1[i]][s2[i] - 1] = mt[mm[i]]
                MA[mm[i]].Op.append(i)
                MA[mm[i]].GapT.append(start[s1[i]][s2[i] - 1])
                MA[mm[i]].MFT.append(mt[mm[i]])
    newp=s1
    return newp

def AS2FAS(p_chrom,m_chrom,FJ,N,H,TM,time,f_index):
    SH = len(p_chrom)
    e=0
    opmax = int(max(H))
    # initial finish time matrix to record the finish time of each operation
    finish = np.zeros(shape=(N, opmax))
    start = np.zeros(shape=(N, opmax))
    mt = np.zeros(TM)
    MA=[]
    for i in range(TM):# creat a object array
        MA.append(Machine())

    s1 = p_chrom
    s2 = np.zeros(SH, dtype=int)
    p = np.zeros(N, dtype=int)
    for i in range(SH):
        p[s1[i]] = p[s1[i]] + 1
        s2[i] = p[s1[i]]
    mm = np.zeros(SH, dtype=int)
    for i in range(SH):
        t1 = s1[i]
        t2 = s2[i]
        t4 = 0
        for k in range(t1):  # sum from 0 to t1-1
            t4 = t4 + H[k]
        mm[i] = m_chrom[t4 + t2 - 1]
    #start decoding
    for i in range(SH-1,-1,-1):
        if s2[i]==H[s1[i]]:
            ON=len(MA[mm[i]].Op)
            if ON>0:
                t=time[f_index][s1[i]][s2[i]-1][mm[i]]
                Index1=-1
                for j in range(ON):
                    if MA[mm[i]].GapT[j]-t>0:
                        Index1=j;break
                if Index1!=-1: #insert the operation
                    Index1=MA[mm[i]].Op[Index1]
                    tmp=s1[i]
                    for j in range(i,Index1):
                        s1[j]=s1[j+1]
                    s1[Index1]=tmp
                    tmp=s2[i]
                    for j in range(i,Index1):
                        s2[j]=s2[j+1]
                    s2[Index1]=tmp
                    tmp = mm[i]
                    for j in range(i, Index1):
                        mm[j] = mm[j+1]
                    mm[Index1] = tmp
                    for j in range(ON):
                        if MA[mm[Index1]].Op[j] <= Index1:
                            MA[mm[Index1]].Op[j] = MA[mm[Index1]].Op[j] - 1
                    for k in range(TM):
                        if k != mm[Index1]:
                            ON2 = len(MA[k].Op)
                            for h in range(ON2):
                                if MA[k].Op[h] < Index1 and MA[k].Op[h] > i:
                                    MA[k].Op[h] = MA[k].Op[h] - 1
                    MA[mm[Index1]].Op.append(Index1)
                    MA[mm[Index1]].GapT.append(0)
                    MA[mm[Index1]].MFT.append(0)
                    MA[mm[Index1]].Op.sort()  # sort ascend
                    MA[mm[Index1]].Op=MA[mm[Index1]].Op[::-1] #sort descend
                    IIndex = find_all_index(MA[mm[Index1]].Op, Index1)
                    if IIndex[0] == 0:
                        start[s1[Index1]][s2[Index1] - 1] = 0
                    else:
                        LastOp = MA[mm[Index1]].Op[IIndex[0] - 1]
                        start[s1[Index1]][s2[Index1] - 1] = max(0, finish[s1[LastOp]][s2[LastOp] - 1])
                    finish[s1[Index1]][s2[Index1] - 1] = t + start[s1[Index1]][s2[Index1] - 1]
                    ON = ON + 1
                    for j in range(ON):
                        Index1 = MA[mm[Index1]].Op[j]
                        if j == 0:
                            MA[mm[Index1]].GapT[j] = 0
                        else:
                            LastOp = MA[mm[Index1]].Op[j - 1]
                            MA[mm[Index1]].GapT[j] = start[s1[Index1]][s2[Index1] - 1] - finish[s1[LastOp]][s2[LastOp] - 1]
                        MA[mm[Index1]].MFT[j] = finish[s1[Index1]][s2[Index1] - 1]
                    mt[mm[Index1]] = MA[mm[Index1]].MFT[ON-1]
                else: #Index==-1
                    start[s1[i]][s2[i]-1]=MA[mm[i]].MFT[ON-1]
                    mt[mm[i]]=start[s1[i]][s2[i]-1]+time[f_index][s1[i]][s2[i]-1][mm[i]]
                    finish[s1[i]][s2[i] - 1]=mt[mm[i]]
                    MA[mm[i]].Op.append(i)
                    MA[mm[i]].GapT.append(0)
                    MA[mm[i]].MFT.append(mt[mm[i]])
            else: #ON=0
                mt[mm[i]] = time[f_index][s1[i]][s2[i] - 1][mm[i]]
                start[s1[i]][s2[i] - 1]=0
                finish[s1[i]][s2[i] - 1] = mt[mm[i]]
                MA[mm[i]].Op.append(i)
                MA[mm[i]].GapT.append(0)
                MA[mm[i]].MFT.append(mt[mm[i]])
        else: #s2[i]!=1
            ON = len(MA[mm[i]].Op)
            if ON>0:
                t=time[f_index][s1[i]][s2[i]-1][mm[i]]
                Index1=-1
                for j in range(ON):
                    if MA[mm[i]].GapT[j]-t>0:
                        if ON==1 or j==0:
                            tmp=finish[s1[i]][s2[i]]
                        else:
                            tmp = finish[s1[i]][s2[i]]-MA[mm[i]].MFT[j-1]
                        if MA[mm[i]].GapT[j]-t-tmp>0:
                            Index1=j;break
                if Index1 != -1:  # insert the operation
                    Index1 = MA[mm[i]].Op[Index1]
                    tmp = s1[i]
                    for j in range(i, Index1):
                        s1[j] = s1[j + 1]
                    s1[Index1] = tmp
                    tmp = s2[i]
                    for j in range(i, Index1):
                        s2[j] = s2[j + 1]
                    s2[Index1] = tmp
                    tmp = mm[i]
                    for j in range(i, Index1):
                        mm[j] = mm[j + 1]
                    mm[Index1] = tmp
                    for j in range(ON):
                        if MA[mm[Index1]].Op[j] <= Index1:
                            MA[mm[Index1]].Op[j] = MA[mm[Index1]].Op[j] - 1
                    for k in range(TM):
                        if k != mm[Index1]:
                            ON2 = len(MA[k].Op)
                            for h in range(ON2):
                                if MA[k].Op[h] < Index1 and MA[k].Op[h] > i:
                                    MA[k].Op[h] = MA[k].Op[h] - 1
                    MA[mm[Index1]].Op.append(Index1)
                    MA[mm[Index1]].GapT.append(0)
                    MA[mm[Index1]].MFT.append(0)
                    MA[mm[Index1]].Op.sort()  # sort ascend
                    MA[mm[Index1]].Op = MA[mm[Index1]].Op[::-1]  # sort descend
                    IIndex = find_all_index(MA[mm[Index1]].Op, Index1)
                    if IIndex[0] == 0:
                        start[s1[Index1]][s2[Index1] - 1] = max(finish[s1[Index1]][s2[Index1]], 0)
                    else:
                        LastOp = MA[mm[Index1]].Op[IIndex[0] - 1]
                        start[s1[Index1]][s2[Index1] - 1] = max(finish[s1[Index1]][s2[Index1]], finish[s1[LastOp]][s2[LastOp] - 1])
                    finish[s1[Index1]][s2[Index1] - 1] = t + start[s1[Index1]][s2[Index1] - 1]
                    ON = ON + 1
                    for j in range(ON):
                        Index1 = MA[mm[Index1]].Op[j]
                        if j == 0:
                            MA[mm[Index1]].GapT[j] = start[s1[Index1]][s2[Index1]-1]
                        else:
                            LastOp = MA[mm[Index1]].Op[j - 1]
                            MA[mm[Index1]].GapT[j] = start[s1[Index1]][s2[Index1] - 1] - finish[s1[LastOp]][s2[LastOp] - 1]
                        MA[mm[Index1]].MFT[j] = finish[s1[Index1]][s2[Index1] - 1]
                    mt[mm[Index1]] = MA[mm[Index1]].MFT[ON-1]
                else:  # Index==-1
                    start[s1[i]][s2[i] - 1] = max(MA[mm[i]].MFT[ON-1],finish[s1[i]][s2[i]])
                    mt[mm[i]] = start[s1[i]][s2[i] - 1] + time[f_index][s1[i]][s2[i] - 1][mm[i]]
                    finish[s1[i]][s2[i] - 1] = mt[mm[i]]
                    MA[mm[i]].Op.append(i)
                    gap=start[s1[i]][s2[i] - 1]-MA[mm[i]].MFT[ON-1]
                    MA[mm[i]].GapT.append(gap)
                    MA[mm[i]].MFT.append(mt[mm[i]])
            else:  # ON=0
                mt[mm[i]] =finish[s1[i]][s2[i]]+time[f_index][s1[i]][s2[i] - 1][mm[i]]
                start[s1[i]][s2[i] - 1] = finish[s1[i]][s2[i]]
                finish[s1[i]][s2[i] - 1] = mt[mm[i]]
                MA[mm[i]].Op.append(i)
                MA[mm[i]].GapT.append(start[s1[i]][s2[i] - 1])
                MA[mm[i]].MFT.append(mt[mm[i]])
    newp=s1
    return newp

def EnergysavingDHFJSP(p_chrom,m_chrom,f_chrom,fitness,N,H,TM,time,SH,F):
    s1 = p_chrom
    s2 = np.zeros(SH, dtype=int)
    p = np.zeros(N, dtype=int)
    for i in range(SH):
        p[s1[i]] = p[s1[i]] + 1
        s2[i] = p[s1[i]]
    P0 = [];
    P = [];
    IP = []
    FJ = []
    for f in range(F):
        P.append([])
        IP.append([])
        FJ.append([])

    for i in range(SH):
        t1 = s1[i]
        t2 = s2[i]
        t3 = f_chrom[t1]
        P[t3].append(p_chrom[i])
        IP[t3].append(i)
    for i in range(N):
        t3 = f_chrom[i]
        FJ[t3].append(i)

    # cf = int(fitness[2])
    for f in range(F):
        P[f]=SAS2AS(P[f],m_chrom,FJ[f],N,H,TM,time,f) #complete test
        P[f] =AS2FAS(P[f], m_chrom, FJ[f], N,H, TM, time, f)
    newf=f_chrom
    newm=m_chrom
    newp = np.zeros(SH, dtype=int)
    for f in range(F):
        L = len(IP[f])
        for i in range(L):
            newp[IP[f][i]] = P[f][i]
    return newp, newm, newf