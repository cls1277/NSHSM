#include <iostream>
#include <algorithm>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <pybind11/stl.h>
#include <string>
#include "readData.h"
#include "tools.h"
#include "initPop.h"
#include "evolution.h"
#include "popSort2.h"
#include "fullActive.h"
#include "localSearch2.h"
#include <sstream> 
// #include <direct.h>
#include <filesystem>

namespace fs = std::filesystem;

namespace py = pybind11;

void run(int POPSIZE, double PC, double PM, double PK, int count, std::string DATASET, std::string EXPERIMENT) {
	srand(time(NULL)); 
    Dset_info dset_data;
	std::vector<cand_info> cand_data = read_data(DATASET, dset_data.FACTORIES, dset_data.JOBS);
    dset_data.MACHINES = 5;
    int ITERTHRE = 200 * (5 * dset_data.JOBS);
    int iter = ITERTHRE;
    std::vector<Individual> pop = init_pop(POPSIZE, dset_data, cand_data, iter);
    double det = 0; int detc = 0;
    while(iter > 0) {
    	int iter_ = iter; std::vector<Individual> pop_new = crossover(pop, dset_data, cand_data, iter, PC);
        iter = iter_; mutation(pop_new, dset_data, cand_data, iter, PM);
        int len = -1; std::vector<Individual> pop_fa = pop_sort(pop, pop_new, len);
        full_active(pop_fa, len, dset_data, cand_data, iter);
        std::vector<Individual> pop_son = local_search(pop_fa, dset_data, cand_data, iter, det, detc, PK);
        pop = pop_sort(pop, pop_son, len);
        printf("%s on %s, %d-th iteration, %.2lf%%\n",EXPERIMENT.c_str(), DATASET.c_str(), count, (ITERTHRE-iter)*100.0/ITERTHRE);
    }
    // for(Individual x : pop) {
	// 	printf("%d %d\n", std::get<0>(x.objectives), std::get<1>(x.objectives));
	// } 

    std::string folderPath = "result";
    // 创建 result 目录
    if (!fs::exists(folderPath)) {
        fs::create_directory(folderPath);
    }

    // 创建 result/EXPERIMENT 目录
    folderPath = "result/" + EXPERIMENT;
    if (!fs::exists(folderPath)) {
        fs::create_directory(folderPath);
    }

    // 创建 result/EXPERIMENT/DATASET 目录
    folderPath = "result/" + EXPERIMENT + '/' + DATASET;
    if (!fs::exists(folderPath)) {
        fs::create_directory(folderPath);
    }

    std::stringstream stream; stream << count;
    std::string count_string; stream >> count_string;
	std::ofstream outfile; std::string filename = folderPath+"/res"+count_string+".txt";
	outfile.open(filename, std::ios::out | std::ios::trunc );
	 
    for(const Individual & x : pop) {
//		printf("%d %d\n", get<0>(x.objectives), get<1>(x.objectives));
		outfile<<std::get<0>(x.objectives)<<' '<<std::get<1>(x.objectives)<<std::endl;
	}
//    outfile << det / detc << std::endl;

/*    std::ofstream outfile2; std::string filename2 = folderPath+"/pop"+count_string+".txt";
	outfile2.open(filename2, std::ios::out | std::ios::trunc );
	 
    for(const Individual & x : pop) {
//		printf("%d %d\n", get<0>(x.objectives), get<1>(x.objectives));
        for(int y : x.factories) {
            outfile2<<y<<' ';
        }
        outfile2<<std::endl;
        for(int y : x.machines) {
            outfile2<<y<<' ';
        }
        outfile2<<std::endl;
        for(int y : x.schedules) {
            outfile2<<y<<' ';
        }
        outfile2<<std::endl<<std::endl;
	}*/
}

PYBIND11_MODULE(LS, m) {
    m.doc() = "local search";
    m.def("run", &run, "run function");
}
