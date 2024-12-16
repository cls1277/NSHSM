cmake_minimum_required(VERSION 3.22)
set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED True)
set(CMAKE_CXX_EXTENSIONS OFF)

project(LS)

add_subdirectory(extern/pybind11)
pybind11_add_module(LS localSearch.cpp)
