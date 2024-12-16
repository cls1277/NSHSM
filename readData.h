#ifndef _READDATA_H
#define _READDATA_H

#include "json/json.h"
#include <iostream>
#include <fstream>
#include "jsoncpp.cpp"
#include <vector>
#include "tools.h"

std::vector<cand_info> read_data(std::string dataset, int & FACTORIES, int & JOBS) {
   std::vector<cand_info> cand_data;
   cand_data.push_back(cand_info());
    Json::Reader reader;
	Json::Value root;
	std::ifstream in("../DHFJSP-benchmark/instances.json", std::ios::binary);
    if(reader.parse(in, root)) {
        for(int i=0; i<root.size(); i++) {
            std::string name = root[i]["name"].asString();
            if(name == dataset) {
                JOBS = root[i]["JOBS"].asInt();
                FACTORIES = root[i]["FACTORIES"].asInt();
                std::string PATH = "../DHFJSP-benchmark/" + root[i]["path"].asString();

                std::ifstream file(PATH, std::ios::in);
                
                int num;
                for(int i=1; i<=3; i++) {
                	file >> num;	
				}
                for(int i=0; i<FACTORIES; i++) {
                    for(int j=0; j<JOBS; j++) {
                        int fac, job, ope; file >> fac >> job >> ope;
                        fac--; job--;
                        for(int k=1; k<=ope; k++) {
                            int op; file >> op; op--;
                            int node = get_node(job, op);
                            
                            file >> num;

                            std::vector<int> machines, times;
                            for(int l=1; l<=num; l++) {
                                int machine, time; file >> machine >> time;
                                machine--;
                                machines.push_back(machine);
                                times.push_back(time);
                            }
                            if(cand_data.size() <= node) {
                                cand_info x;
                                x.machines = machines;
                                x.times.push_back(times);
                                cand_data.push_back(x);
                            } else {
                                cand_data[node].times.push_back(times);
                            }
                        }
                    }
                }
                return cand_data;
            }
        }
	}
    return cand_data;
}

#endif
