#ifndef _POPSORT2_H
#define _POPSORT2_H

#include <vector>
#include <algorithm>
#include <tuple>
#include "tools.h"
#include <set>


std::vector<std::vector<int>> fast_non_dominated_sort(std::vector<std::tuple<int, int, int>> objectives) {
	
    int POPSIZE = objectives.size();
    std::vector<std::vector<int>> S(POPSIZE, std::vector<int>());
    std::vector<std::vector<int>> front;
    std::vector<int> n(POPSIZE, 0), rank(POPSIZE, INT32_MAX);

    std::vector<int> front0;
    for(int p=0; p<POPSIZE; p++) {
    	S[p].clear();
    	n[p] = 0;
        for(int q=0; q<POPSIZE; q++) {
    		int less=0, equal=0, greater=0; 
            int mkspp, tecp, keyp;
            std::tie(mkspp, tecp, keyp) = objectives[p];    
            int mkspq, tecq, keyq;
            std::tie(mkspq, tecq, keyq) = objectives[q];
//            if((mkspp>mkspq&&tecp>tecq)||(mkspp>=mkspq&&tecp>tecq)||(mkspp>mkspq&&tecp>=tecq)) {
//            	if(find(S[p].begin(), S[p].end(), q)==S[p].end()) {
//            		S[p].push_back(q);
//				}
//			} else if((mkspq>mkspp&&tecq>tecp)||(mkspq>=mkspp&&tecq>tecp)||(mkspq>mkspp&&tecq>=tecp)) {
//				n[p]++;
//			}
			if(mkspp>mkspq) less++;
			if(mkspp==mkspq) equal++;
			if(mkspp<mkspq) greater++;
			if(tecp>tecq) less++;
			if(tecp==tecq) equal++;
			if(tecp<tecq) greater++;
			
			if(less+equal==2&&equal!=2) {
				n[p]++;
			} else if(greater+equal==2&&equal!=2) {
				S[p].push_back(q);
			}
        }
    	if(n[p]==0) {
			rank[p]=0;
			if(find(front0.begin(), front0.end(), p)==front0.end()) {
                front0.push_back(p);
            }
		}
    }

    front.push_back(front0);
    int i = 0;
    while(front[i].size()) {
        std::vector<int> Q;
        for(int p : front[i]) {
            for(int q : S[p]) {
                n[q] --;
                if(n[q]==0) {
                    rank[q] = i + 1;
                    if(find(Q.begin(), Q.end(), q)==Q.end()) {
                        Q.push_back(q);
                    }
                }
            }
        }
        i ++;
        if(Q.size()==0) {
            break;
        }
        front.push_back(Q);
    }
    return front;
}

const double eps = 1e-9;

template<typename T>
int index_of(T a, std::vector<T> list) {
    for(int i=0; i<list.size(); i++) {
        if(std::fabs(list[i]-a)<eps) {
            return i;
        }
    }
    return -1;
}

template<typename T>
std::vector<int> sort_by_values(std::vector<int> list1, std::vector<T> values) {
//	for(auto it : list1) {
//		printf("%d ",it);
//	}
//	printf("\n");
//	for(auto it : values) {
//		std::cout<<it<<' ';
//	}
    std::vector<int> sorted_list;
    while(sorted_list.size() != list1.size()) {
        int idx = index_of(*(std::min_element(values.begin(), values.end())), values);
        if(find(list1.begin(), list1.end(), idx)!=list1.end()) {
            sorted_list.push_back(idx);
        }
        values[idx] = INT32_MAX;
    }
    return sorted_list;
}

std::vector<double> crowding_distance(std::vector<std::tuple<int, int, int>> objectives, std::vector<int> front) {
    std::vector<double> values1, values2;
    for(auto it : objectives) {
        values1.push_back(std::get<0>(it));
        values2.push_back(std::get<1>(it));
    }
//    for(auto it : values1) {
//    	std::cout<<it<<' ';
//	}
//	std::cout<<std::endl;
//	for(auto it : values2) {
//		std::cout<<it<<' ';
//	}
//	std::cout<<std::endl;
    std::vector<double> distance(front.size(), 0);
    std::vector<int> sorted1 = sort_by_values(front, values1);
    std::vector<int> sorted2 = sort_by_values(front, values2);
    
//    for(auto it : sorted1) {
//    	std::cout<<it<<' ';
//	}
//	std::cout<<std::endl;
//	for(auto it : sorted2) {
//		std::cout<<it<<' ';
//	}
//	std::cout<<std::endl;    
    
//    distance[0] = INT32_MAX;
//    distance[front.size()-1] = INT32_MAX;
    distance[0] = INT32_MAX-1;
    distance[front.size()-1] = INT32_MAX-1;
    int maxx = *(std::max_element(values1.begin(), values1.end()));
    int minn = *(std::min_element(values1.begin(), values1.end()));
    for(int k=1; k<front.size()-1; k++) {
        distance[k] = distance[k]+ (values1[sorted1[k+1]] - values2[sorted1[k-1]]) * 1.0/(maxx-minn);
    }
    maxx = *(std::max_element(values2.begin(), values2.end()));
    minn = *(std::min_element(values2.begin(), values2.end()));    
    for(int k=1; k<front.size()-1; k++) {
        distance[k] = distance[k]+ (values1[sorted2[k+1]] - values2[sorted2[k-1]]) * 1.0/(maxx-minn);
    }
    return distance;
}

std::vector<Individual> pop_sort(const std::vector<Individual> & pop1, const std::vector<Individual> & pop2, int & len) {
    int POPSIZE = pop1.size();
    std::vector<Individual> pop12;
    std::set<std::pair<int,int>> st;
    std::vector<std::tuple<int, int, int>> objectives;
    for(Individual ind : pop1) {
    	std::pair<int,int> now_obj = std::make_pair(std::get<0>(ind.objectives), std::get<1>(ind.objectives));
        if(st.find(now_obj) == st.end()) {
        	st.insert(now_obj);
            pop12.push_back(ind);
        }
    }
    for(Individual ind : pop2) {
    	std::pair<int,int> now_obj = std::make_pair(std::get<0>(ind.objectives), std::get<1>(ind.objectives));
        if(st.find(now_obj) == st.end()) {
        	st.insert(now_obj);
            pop12.push_back(ind);
        }
    }
    
    std::sort(pop12.begin(), pop12.end());
    for(auto it : pop12) {
    	objectives.push_back(it.objectives);
//		objectives.push_back(std::make_tuple((-1)*std::get<0>(it.objectives), (-1)*std::get<1>(it.objectives), (-1)*std::get<2>(it.objectives)));
	}
	
//	std::cout<<"objectives"<<std::endl;
//	std::cout<<objectives.size()<<std::endl;
//	for(auto it : objectives) {
//		std::cout<<std::get<0>(it)<<' '<<std::get<1>(it)<<std::endl;
//	}
//	std::cout<<"----"<<std::endl;
    
    std::vector<std::vector<int>> non_dominated_sorted_solution2 = fast_non_dominated_sort(objectives);
//    for(auto it : non_dominated_sorted_solution2) {
//    	for(auto it1 : it) {
//    		std::cout<<it1<<' ';
//		}
//		std::cout<<std::endl;
//	}
    
    std::vector<std::vector<double>> crowding_distance_values2;
    for(int i=0; i<non_dominated_sorted_solution2.size(); i++) {
        crowding_distance_values2.push_back(crowding_distance(objectives, non_dominated_sorted_solution2[i]));
    }

    std::vector<int> new_solution;

    len = std::min(POPSIZE, int(non_dominated_sorted_solution2[0].size()));
    
    for(int i=0; i<non_dominated_sorted_solution2.size(); i++) {
        std::vector<int> non_dominated_sorted_solution2_1;
        for(int j=0; j<non_dominated_sorted_solution2[i].size(); j++) {
            non_dominated_sorted_solution2_1.push_back(index_of(non_dominated_sorted_solution2[i][j],non_dominated_sorted_solution2[i]));
        }
//        for(auto it : non_dominated_sorted_solution2_1) {
//        	std::cout<<it<<' ';
//		}
//		std::cout<<std::endl;
//		for(auto it : crowding_distance_values2[i]) {
//			std::cout<<it<<' ';
//		}
//		std::cout<<std::endl;
        std::vector<int> front22 = sort_by_values(non_dominated_sorted_solution2_1, crowding_distance_values2[i]);
//        for(auto it : front22) {
//        	std::cout<<it<<' ';
//		}
//		std::cout<<std::endl;
        std::vector<int> front;
        for(int j=0; j<non_dominated_sorted_solution2[i].size(); j++) {
            front.push_back(non_dominated_sorted_solution2[i][front22[j]]);
        }
        std::reverse(front.begin(), front.end());
//        for(auto it : front) {
//        	std::cout<<it<<' ';
//		}
//		std::cout<<std::endl;
        for(int value  : front) {
            new_solution.push_back(value);
            if(new_solution.size()==POPSIZE) {
                break;
            }
        }
        if(new_solution.size()==POPSIZE) {
            break;
        }
    }
    std::vector<Individual> solution;
    for(int i : new_solution) {
        solution.push_back(pop12[i]);
    }
    return solution;
}

#endif
