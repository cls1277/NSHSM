#ifndef _FULLACTIVE_CPP
#define _FULLACTIVE_CPP

#include "mex.h"
#include <vector>
#include <tuple>
#include <algorithm>
#include <string>
#include <cmath>
#include "tools.h"
#include "popSort2.h"

std::vector<int> find_all_index(const std::vector<int> & arr, int item) {
    std::vector<int> res;
    for(int i=0; i<arr.size(); i++) {
        if(arr[i] == item) {
            res.push_back(i);
        }
    }
    return res;
}

struct Machine {
    std::vector<int> Op, GapT, MFT;
};

std::vector<int> SAS2AS(const std::vector<int> & p_chrom, const std::vector<int> & m_chrom, int N, const std::vector<int> & H, int TM, const std::vector<std::vector<std::vector<std::vector<int>>>> & time, int f_index) {
    int SH =p_chrom.size();
    int e = 0;
    int opmax = 5; // ??????????????????????
    std::vector<std::vector<int>> finish(N, std::vector<int>(opmax, 0));
    std::vector<std::vector<int>> start(N, std::vector<int>(opmax, 0));
    std::vector<int> mt(TM, 0);
    std::vector<Machine> MA(TM, Machine());
    std::vector<int> s1 = p_chrom;
    std::vector<int> s2(SH, 0);
    std::vector<int> p(N, 0);
    for(int i=0; i<SH; i++) {
        p[s1[i]]++;
        s2[i] = p[s1[i]];
    }
    std::vector<int> mm(SH, 0);
    for(int i=0; i<SH; i++) {
        int t1 = s1[i];
        int t2 = s2[i];
        int t4 = 0;
        for(int k=0; k<t1; k++) {
            t4 += H[k];
        }
        mm[i] = m_chrom[t4 + t2 - 1];
    }
    for(int i=0; i<SH; i++) {
        if(s2[i] == 1) { 
            int ON = MA[mm[i]].Op.size();
            if(ON > 0) {
                int t = time[f_index][s1[i]][s2[i]-1][mm[i]];
                int Index1 = -1;
                for(int j=0; j<ON; j++) {
                    if(MA[mm[i]].GapT[j]-t>0) {
                        Index1 = j;
                        break;
                    }
                }
                if(Index1 != -1) {
                    Index1 = MA[mm[i]].Op[Index1];
                    int tmp = s1[i];
                    for(int j=i; j>Index1; j--) {
                        s1[j] = s1[j-1];
                    }
                    s1[Index1] = tmp;
                    tmp = s2[i];
                    for(int j=i; j>Index1; j--) {
                        s2[j] = s2[j-1];
                    }
                    s2[Index1] = tmp;
                    tmp = mm[i];
                    for(int j=i; j>Index1; j--) {
                        mm[j] = mm[j-1];
                    }
                    mm[Index1] = tmp;
                    for(int j=0; j<ON; j++) {
                        if(MA[mm[Index1]].Op[j] >= Index1) {
                            MA[mm[Index1]].Op[j] = MA[mm[Index1]].Op[j] + 1;
                        }
                    }
                    for(int k=0; k<TM; k++) {
                        if(k!=mm[Index1]) {
                            int ON2 = MA[k].Op.size();
                            for(int h=0; h<ON2; h++) {
                                if(MA[k].Op[h] > Index1 && MA[k].Op[h] < i) {
                                    MA[k].Op[h]++;
                                }
                            }
                        }
                    }
                    MA[mm[Index1]].Op.push_back(Index1);
                    MA[mm[Index1]].GapT.push_back(0);
                    MA[mm[Index1]].MFT.push_back(0);
                    std::sort(MA[mm[Index1]].Op.begin(), MA[mm[Index1]].Op.end());
                    std::vector<int> IIndex = find_all_index(MA[mm[Index1]].Op, Index1);
                    if(IIndex[0] == 0) {
                        start[s1[Index1]][s2[Index1] -1] = 0;
                    } else {
                        int LastOp = MA[mm[Index1]].Op[IIndex[0] - 1];
                        start[s1[Index1]][s2[Index1] - 1] = std::max(0, finish[s1[LastOp]][s2[LastOp] - 1]);
                    }
                    finish[s1[Index1]][s2[Index1] -1] = t + start[s1[Index1]][s2[Index1] - 1];
                    ON ++;
                    for(int j=0; j<ON; j++) {
                        Index1 = MA[mm[Index1]].Op[j];
                        if(j==0) {
                            MA[mm[Index1]].GapT[j] = 0;
                        } else {
                            int LastOp = MA[mm[Index1]].Op[j-1];
                            MA[mm[Index1]].GapT[j] = start[s1[Index1]][s2[Index1] - 1] - finish[s1[LastOp]][s2[LastOp] - 1];
                        }
                        MA[mm[Index1]].MFT[j] = finish[s1[Index1]][s2[Index1] - 1];
                    }
                    mt[mm[Index1]] = MA[mm[Index1]].MFT[ON-1];
                } else {
                    start[s1[i]][s2[i]-1]=MA[mm[i]].MFT[ON-1];
                    mt[mm[i]]=start[s1[i]][s2[i]-1]+time[f_index][s1[i]][s2[i]-1][mm[i]];
                    finish[s1[i]][s2[i] - 1]=mt[mm[i]];
                    MA[mm[i]].Op.push_back(i);
                    MA[mm[i]].GapT.push_back(0);
                    MA[mm[i]].MFT.push_back(mt[mm[i]]);
                }
            } else {
                mt[mm[i]] = time[f_index][s1[i]][s2[i] - 1][mm[i]];
                start[s1[i]][s2[i] - 1]=0;
                finish[s1[i]][s2[i] - 1] = mt[mm[i]];
                MA[mm[i]].Op.push_back(i);
                MA[mm[i]].GapT.push_back(0);
                MA[mm[i]].MFT.push_back(mt[mm[i]]);
            }
        } else {
            int ON = MA[mm[i]].Op.size();
            if(ON>0) {
                int t=time[f_index][s1[i]][s2[i]-1][mm[i]];
                int Index1=-1;
                for(int j=0; j<ON; j++) {
                    if(MA[mm[i]].GapT[j]-t>0) {
                        int tmp;
                        if(ON==1 || j==0) {
                            tmp=finish[s1[i]][s2[i]-2];
                        } else {
                            tmp = finish[s1[i]][s2[i] - 2]-MA[mm[i]].MFT[j-1];
                        }
                        if(MA[mm[i]].GapT[j]-t-tmp>0) {
                            Index1=j;
                            break;
                        }
                    }
                }
                if(Index1 != -1) {
                    Index1 = MA[mm[i]].Op[Index1];
                    int tmp = s1[i];
                    for(int j=i; j>Index1; j--) {
                        s1[j] = s1[j-1];
                    }
                    s1[Index1] = tmp;
                    tmp = s2[i];
                    for(int j=i; j>Index1; j--) {
                        s2[j] = s2[j-1];
                    }
                    s2[Index1] = tmp;
                    tmp = mm[i];
                    for(int j=i; j>Index1; j--) {
                        mm[j] = mm[j-1];
                    }
                    mm[Index1] = tmp;
                    for(int j=0; j<ON; j++) {
                        if(MA[mm[Index1]].Op[j] >= Index1) {
                            MA[mm[Index1]].Op[j] = MA[mm[Index1]].Op[j] + 1;
                        }
                    }
                    for(int k=0; k<TM; k++) {
                        if(k != mm[Index1]) {
                            int ON2 = MA[k].Op.size();
                            for(int h=0; h<ON2; h++) {
                                if(MA[k].Op[h] > Index1 && MA[k].Op[h] < i) {
                                    MA[k].Op[h] = MA[k].Op[h] + 1;
                                }
                            }
                        }
                    }
                    MA[mm[Index1]].Op.push_back(Index1);
                    MA[mm[Index1]].GapT.push_back(0);
                    MA[mm[Index1]].MFT.push_back(0);
                    std::sort(MA[mm[Index1]].Op.begin(), MA[mm[Index1]].Op.end());
                    std::vector<int> IIndex = find_all_index(MA[mm[Index1]].Op, Index1);
                    if(IIndex[0] == 0) {
                        start[s1[Index1]][s2[Index1] - 1] = std::max(finish[s1[Index1]][s2[Index1]-2], 0);
                    } else {
                        int LastOp = MA[mm[Index1]].Op[IIndex[0] - 1];
                        start[s1[Index1]][s2[Index1] - 1] = std::max(finish[s1[Index1]][s2[Index1]-2], finish[s1[LastOp]][s2[LastOp] - 1]);
                    }
                    finish[s1[Index1]][s2[Index1] - 1] = t + start[s1[Index1]][s2[Index1] - 1];
                    ON = ON + 1;
                    for(int j=0; j<ON; j++) {
                        Index1 = MA[mm[Index1]].Op[j];
                        if(j==0) {
                            MA[mm[Index1]].GapT[j] = 0;
                        } else {
                            int LastOp = MA[mm[Index1]].Op[j - 1];
                            MA[mm[Index1]].GapT[j] = start[s1[Index1]][s2[Index1] - 1] - finish[s1[LastOp]][s2[LastOp] - 1];
                        }
                        MA[mm[Index1]].MFT[j] = finish[s1[Index1]][s2[Index1] - 1];
                    }
                    mt[mm[Index1]] = MA[mm[Index1]].MFT[ON-1];
                } else {
                    start[s1[i]][s2[i] - 1] = std::max(MA[mm[i]].MFT[ON-1],finish[s1[i]][s2[i]-2]);
                    mt[mm[i]] = start[s1[i]][s2[i] - 1] + time[f_index][s1[i]][s2[i] - 1][mm[i]];
                    finish[s1[i]][s2[i] - 1] = mt[mm[i]];
                    MA[mm[i]].Op.push_back(i);
                    int gap=start[s1[i]][s2[i] - 1]-MA[mm[i]].MFT[ON-1];
                    MA[mm[i]].GapT.push_back(gap);
                    MA[mm[i]].MFT.push_back(mt[mm[i]]);
                }
            }  else {
                mt[mm[i]] =finish[s1[i]][s2[i] - 2]+time[f_index][s1[i]][s2[i] - 1][mm[i]];
                start[s1[i]][s2[i] - 1] = finish[s1[i]][s2[i] - 2];
                finish[s1[i]][s2[i] - 1] = mt[mm[i]];
                MA[mm[i]].Op.push_back(i);
                MA[mm[i]].GapT.push_back(start[s1[i]][s2[i] - 1]);
                MA[mm[i]].MFT.push_back(mt[mm[i]]);
            }
        }
    }
    return s1;
}

bool compare(int a, int b) {
    return a > b;
}

std::vector<int> AS2FAS(const std::vector<int> & p_chrom, const std::vector<int> & m_chrom, int N, const std::vector<int> & H, int TM, const std::vector<std::vector<std::vector<std::vector<int>>>> & time, int f_index) {
    int SH = p_chrom.size();
    int e=0;
    int opmax = 5;
    std::vector<std::vector<int>> finish(N, std::vector<int>(opmax, 0));
    std::vector<std::vector<int>> start(N, std::vector<int>(opmax, 0));
    std::vector<int> mt(TM, 0);
    std::vector<Machine> MA(TM, Machine());
    std::vector<int> s1 = p_chrom;
    std::vector<int> s2(SH, 0);
    std::vector<int> p(N, 0);
    for(int i=0; i<SH; i++) {
        p[s1[i]]++;
        s2[i] = p[s1[i]];
    }
    std::vector<int> mm(SH, 0);
    for(int i=0; i<SH; i++) {
        int t1 = s1[i];
        int t2 = s2[i];
        int t4 = 0;
        for(int k=0; k<t1; k++) {
            t4 += H[k];
        }
        mm[i] = m_chrom[t4 + t2 - 1];
    }
    for(int i=SH-1; i>=0; i--) {
        if(s2[i]==H[s1[i]]) {
            int ON=MA[mm[i]].Op.size();
            if(ON>0) {
                int t=time[f_index][s1[i]][s2[i]-1][mm[i]];
                int Index1=-1;
                for(int j=0; j<ON; j++) {
                    if(MA[mm[i]].GapT[j]-t>0) {
                        Index1 = j;
                        break;
                    }
                }
                if(Index1!=-1) {
                    Index1=MA[mm[i]].Op[Index1];
                    int tmp = s1[i];
                    for(int j=i; j<Index1; j++) {
                        s1[j] = s1[j+1];
                    }
                    s1[Index1] = tmp;
                    tmp = s2[i];
                    for(int j=i; j<Index1; j++) {
                        s2[j] = s2[j+1];
                    }
                    s2[Index1] = tmp;
                    tmp = mm[i];
                    for(int j=i; j<Index1; j++) {
                        mm[j] = mm[j+1];
                    }
                    mm[Index1] = tmp;
                    for(int j=0; j<ON; j++) {
                        if(MA[mm[Index1]].Op[j] <= Index1) {
                            MA[mm[Index1]].Op[j] = MA[mm[Index1]].Op[j] - 1;
                        }
                    }
                    for(int k=0; k<TM; k++) {
                        if(k != mm[Index1]) {
                            int ON2 = MA[k].Op.size();
                            for(int h=0; h<ON2; h++) {
                                if(MA[k].Op[h] < Index1 && MA[k].Op[h] > i) {
                                    MA[k].Op[h] = MA[k].Op[h] - 1;
                                }
                            }
                        }
                    }
                    MA[mm[Index1]].Op.push_back(Index1);
                    MA[mm[Index1]].GapT.push_back(0);
                    MA[mm[Index1]].MFT.push_back(0);
                    std::sort(MA[mm[Index1]].Op.begin(), MA[mm[Index1]].Op.end(), compare);
                    std::vector<int> IIndex = find_all_index(MA[mm[Index1]].Op, Index1);
                    if(IIndex[0] == 0) {
                        start[s1[Index1]][s2[Index1] - 1] = 0;
                    } else {
                        int LastOp = MA[mm[Index1]].Op[IIndex[0] - 1];
                        start[s1[Index1]][s2[Index1] - 1] = std::max(0, finish[s1[LastOp]][s2[LastOp] - 1]);
                    }
                    finish[s1[Index1]][s2[Index1] - 1] = t + start[s1[Index1]][s2[Index1] - 1];
                    ON ++;
                    for(int j=0; j<ON; j++) {
                        Index1 = MA[mm[Index1]].Op[j];
                        if(j==0) {
                            MA[mm[Index1]].GapT[j] = 0;
                        } else {
                            int LastOp = MA[mm[Index1]].Op[j - 1];
                            MA[mm[Index1]].GapT[j] = start[s1[Index1]][s2[Index1] - 1] - finish[s1[LastOp]][s2[LastOp] - 1];
                        }
                        MA[mm[Index1]].MFT[j] = finish[s1[Index1]][s2[Index1] - 1];
                    }
                    mt[mm[Index1]] = MA[mm[Index1]].MFT[ON-1];
                } else {
                    start[s1[i]][s2[i]-1]=MA[mm[i]].MFT[ON-1];
                    mt[mm[i]]=start[s1[i]][s2[i]-1]+time[f_index][s1[i]][s2[i]-1][mm[i]];
                    finish[s1[i]][s2[i] - 1]=mt[mm[i]];
                    MA[mm[i]].Op.push_back(i);
                    MA[mm[i]].GapT.push_back(0);
                    MA[mm[i]].MFT.push_back(mt[mm[i]]);
                }
            } else {
                mt[mm[i]] = time[f_index][s1[i]][s2[i] - 1][mm[i]];
                start[s1[i]][s2[i] - 1]=0;
                finish[s1[i]][s2[i] - 1] = mt[mm[i]];
                MA[mm[i]].Op.push_back(i);
                MA[mm[i]].GapT.push_back(0);
                MA[mm[i]].MFT.push_back(mt[mm[i]]);
            }
        } else {
            int ON = MA[mm[i]].Op.size();
            if(ON>0) {
                int t=time[f_index][s1[i]][s2[i]-1][mm[i]];
                int Index1=-1;
                for(int j=0; j<ON; j++) {
                    if(MA[mm[i]].GapT[j]-t>0) {
                        int tmp;
                        if(ON==1 || j==0) {
                            tmp=finish[s1[i]][s2[i]];
                        } else {
                            tmp = finish[s1[i]][s2[i]]-MA[mm[i]].MFT[j-1];
                        }
                        if(MA[mm[i]].GapT[j]-t-tmp>0) {
                            Index1=j;
                            break;
                        }
                    }
                }
                if(Index1 != -1) {
                    Index1 = MA[mm[i]].Op[Index1];
                    int tmp = s1[i];
                    for(int j=i; j<Index1; j++) {
                        s1[j] = s1[j+1];
                    }
                    s1[Index1] = tmp;
                    tmp = s2[i];
                    for(int j=i; j<Index1; j++) {
                        s2[j] = s2[j+1];
                    }
                    s2[Index1] = tmp;
                    tmp = mm[i];
                    for(int j=i; j<Index1; j++) {
                        mm[j] = mm[j+1];
                    }
                    mm[Index1] = tmp;
                    for(int j=0; j<ON; j++) {
                        if(MA[mm[Index1]].Op[j] <= Index1) {
                            MA[mm[Index1]].Op[j] = MA[mm[Index1]].Op[j] - 1;
                        }
                    }
                    for(int k=0; k<TM; k++) {
                        if(k!=mm[Index1]) {
                            int ON2 = MA[k].Op.size();
                            for(int h=0; h<ON2; h++) {
                                if(MA[k].Op[h] < Index1 && MA[k].Op[h] > i) {
                                    MA[k].Op[h] = MA[k].Op[h] - 1;
                                }
                            }
                        }
                    }
                    MA[mm[Index1]].Op.push_back(Index1);
                    MA[mm[Index1]].GapT.push_back(0);
                    MA[mm[Index1]].MFT.push_back(0);
                    std::sort(MA[mm[Index1]].Op.begin(), MA[mm[Index1]].Op.end(), compare);
                    std::vector<int> IIndex = find_all_index(MA[mm[Index1]].Op, Index1);
                    if(IIndex[0] == 0) {
                        start[s1[Index1]][s2[Index1] - 1] = std::max(finish[s1[Index1]][s2[Index1]], 0);
                    } else {
                        int LastOp = MA[mm[Index1]].Op[IIndex[0] - 1];
                        start[s1[Index1]][s2[Index1] - 1] = std::max(finish[s1[Index1]][s2[Index1]], finish[s1[LastOp]][s2[LastOp] - 1]);
                    }
                    finish[s1[Index1]][s2[Index1] - 1] = t + start[s1[Index1]][s2[Index1] - 1];
                    ON = ON + 1;
                    for(int j=0; j<ON; j++) {
                        Index1 = MA[mm[Index1]].Op[j];
                        if(j==0) {
                            MA[mm[Index1]].GapT[j] = start[s1[Index1]][s2[Index1]-1];
                        } else {
                            int LastOp = MA[mm[Index1]].Op[j - 1];
                            MA[mm[Index1]].GapT[j] = start[s1[Index1]][s2[Index1] - 1] - finish[s1[LastOp]][s2[LastOp] - 1];
                        }
                        MA[mm[Index1]].MFT[j] = finish[s1[Index1]][s2[Index1] - 1];
                    }
                    mt[mm[Index1]] = MA[mm[Index1]].MFT[ON-1];
                } else {
                    start[s1[i]][s2[i] - 1] = std::max(MA[mm[i]].MFT[ON-1],finish[s1[i]][s2[i]]);
                    mt[mm[i]] = start[s1[i]][s2[i] - 1] + time[f_index][s1[i]][s2[i] - 1][mm[i]];
                    finish[s1[i]][s2[i] - 1] = mt[mm[i]];
                    MA[mm[i]].Op.push_back(i);
                    int gap=start[s1[i]][s2[i] - 1]-MA[mm[i]].MFT[ON-1];
                    MA[mm[i]].GapT.push_back(gap);
                    MA[mm[i]].MFT.push_back(mt[mm[i]]);
                }
            } else {
                mt[mm[i]] =finish[s1[i]][s2[i]]+time[f_index][s1[i]][s2[i] - 1][mm[i]];
                start[s1[i]][s2[i] - 1] = finish[s1[i]][s2[i]];
                finish[s1[i]][s2[i] - 1] = mt[mm[i]];
                MA[mm[i]].Op.push_back(i);
                MA[mm[i]].GapT.push_back(start[s1[i]][s2[i] - 1]);
                MA[mm[i]].MFT.push_back(mt[mm[i]]);
            }
        }
    }
    return s1;
}

std::vector<int> EnergysavingDHFJSP(const Individual & ind, int N, int TM, const std::vector<std::vector<std::vector<std::vector<int>>>> & time, int SH, int F) {
    std::vector<int> H(N, 5);
    std::vector<int> s1(ind.schedules);
    std::vector<int> s2(SH, 0);
    std::vector<int> p(N, 0);
    for(int i=0; i<SH; i++) {
        p[s1[i]] = p[s1[i]] + 1;
        s2[i] = p[s1[i]];
    }
    std::vector<int> P0;
    std::vector<std::vector<int>> P(F, std::vector<int>()), IP(F, std::vector<int>());
    for(int i=0; i<SH; i++) {
        int t1 = s1[i];
        int t2 = s2[i];
        int t3 = ind.factories[t1];
        P[t3].push_back(ind.schedules[i]);
        IP[t3].push_back(i);
    }
    for(int f=0; f<F; f++) {
        P[f]=SAS2AS(P[f],ind.machines,N,H,TM,time,f);
       P[f] =AS2FAS(P[f], ind.machines, N,H, TM, time, f);
    }
    std::vector<int> newp(SH, 0);
    for(int f=0; f<F; f++) {
        int L = IP[f].size();
        for(int i=0; i<L; i++) {
            newp[IP[f][i]] = P[f][i];
        }
    }
    return newp;
}

std::vector<Individual> full_active(std::vector<Individual> & pop, const Dset_info & dset_data, const std::vector<cand_info> & cand_data) {
    int POPSIZE = pop.size();
    std::vector<Individual> pop12;
    std::set<std::pair<int,int>> st;
    std::vector<std::tuple<int, int, int>> objectives;
    for(Individual ind : pop) {
    	std::pair<int,int> now_obj = std::make_pair(std::get<0>(ind.objectives), std::get<1>(ind.objectives));
        if(st.find(now_obj) == st.end()) {
        	st.insert(now_obj);
            pop12.push_back(ind);
        }
    }
    
    std::sort(pop12.begin(), pop12.end());
    for(auto it : pop12) {
    	objectives.push_back(it.objectives);
        // printf("%d %d\n",std::get<0>(it.objectives), std::get<1>(it.objectives));
	}
    
    std::vector<std::vector<int>> non_dominated_sorted_solution2 = fast_non_dominated_sort(objectives);

    int len = std::min(POPSIZE, int(non_dominated_sorted_solution2[0].size()));
    
    int N = dset_data.JOBS;
    int F = dset_data.FACTORIES;
    int TM = dset_data.MACHINES;
	int SH = dset_data.JOBS * 5;
	std::vector<std::vector<std::vector<std::vector<int>>>> time(F,
        std::vector<std::vector<std::vector<int>>>(N,
            std::vector<std::vector<int>>(5,
                std::vector<int>(TM, 0)
            )
        )
    );

    for(int f=0; f<F; f++) {
		for(int j=0; j<N; j++) {
			for(int o=0; o<5; o++) {
				int node = get_node(j, o);
				for(int it=0; it<cand_data[node].machines.size(); it++) {
					time[f][j][o][cand_data[node].machines[it]] = cand_data[node].times[f][it];
				}
			}
		}
	}

    std::vector<Individual> pop_new;

	for(int i=0; i<len; i++) {
		Individual & ind = pop12[i];
        std::vector<int> newp = EnergysavingDHFJSP(ind, N, TM, time, SH, F);
        pop_new.push_back({ind.factories, ind.machines, newp, std::make_tuple(0, 0, 0)});
        // std::tuple<int, int, int> new_obj = evaluate(ind.factories, ind.machines, newp, dset_data, cand_data, iter);
        // int n = nds(ind.objectives, new_obj);
        // if(n==2 || (n==0 && rand()%2==0)) {
        //     ind.schedules = newp;
        //     ind.objectives = new_obj;
        // }
    }
    return pop_new;
}

void mexFunction(int nlhs, mxArray *plhs[], int nrhs, const mxArray *prhs[]){
    const mwSize *Dims0 = mxGetDimensions(prhs[0]);
    double *inData0 = mxGetPr(prhs[0]);
    int POPSIZE = int(inData0[0]), FACTORIES = int(inData0[1]), JOBS = int(inData0[2]);
    
    const mwSize *Dims2 = mxGetDimensions(prhs[2]);

    double *inData1 = mxGetPr(prhs[1]);
    double *inData2 = mxGetPr(prhs[2]);
    std::vector<cand_info> cand_data;
    cand_data.push_back(cand_info());

    int cnt1 = 0, cnt2 = 0;
    for(mwSize node=0; node<Dims2[2]; node++) {
        std::vector<int> machines;
        std::vector<std::vector<int>> times;
        for(mwSize mac=0; mac<Dims2[0]; mac++) {
            if(int(inData1[cnt1])==1) {
                machines.push_back(mac);
            }
            cnt1++;
        }

        for(mwSize fac=0; fac<Dims2[1]; fac++) {
            std::vector<int> times_;
            for(mwSize mac=0; mac<Dims2[0]; mac++) {
                if(int(inData1[node*Dims2[0]+mac])==1) {
                    times_.push_back(inData2[cnt2]);
                }
                cnt2++;
            }
            times.push_back(times_);
        }

        cand_data.push_back({machines, times});
    }

    Dset_info dset_data({FACTORIES, 5, JOBS});

    const mwSize *Dims3 = mxGetDimensions(prhs[3]);
    double *inData3 = mxGetPr(prhs[3]);
    int cnt3 = 0;
    std::vector<Individual> pop;
    for(int j=0; j<Dims3[1]; j++) {
        Individual ind;
        for(int k=0; k<Dims3[0]; k++) {
            if(k<dset_data.JOBS) {
                ind.factories.push_back(int(inData3[cnt3]));
            } else if(k<dset_data.JOBS+dset_data.JOBS*5) {
                ind.machines.push_back(int(inData3[cnt3]));
            } else {
                ind.schedules.push_back(int(inData3[cnt3]));
            }
            cnt3++;
        }
        ind.objectives = std::make_tuple(0, 0, 0);
        pop.push_back(ind);
    }

    const mwSize *Dims5 = mxGetDimensions(prhs[4]);
    double *inData5 = mxGetPr(prhs[4]);
    int cnt5 = 0;
    for(int j=0; j<Dims5[1]; j++) {
        int obj1, obj2;
        for(int k=0; k<Dims5[0]/2; k++) {
            obj1 = int(inData5[cnt5]); cnt5++;
            obj2 = int(inData5[cnt5]); cnt5++;
        }
        pop[j].objectives = std::make_tuple(obj1, obj2, 0);
    }

    std::vector<Individual> new_pop = full_active(pop, dset_data, cand_data);
    POPSIZE = new_pop.size();

    std::vector<std::vector<int>> inData4;
    for(Individual ind : new_pop) {
        std::vector<int> temp;
        for(auto it : ind.factories) temp.push_back(it);
        for(auto it : ind.machines) temp.push_back(it);
        for(auto it : ind.schedules) temp.push_back(it);
        inData4.push_back(temp);
    }

    int D = JOBS + 5 * JOBS + 5 * JOBS;
    plhs[0] = mxCreateDoubleMatrix(POPSIZE, D, mxREAL);
    double *outData = mxGetPr(plhs[0]);
    int cnt4 = 0;
    for(int i=0; i<D; i++) {
        for(int j=0; j<POPSIZE; j++) {
            outData[cnt4] = double(inData4[j][i]);
            cnt4++;
        }
    }
}

#endif
