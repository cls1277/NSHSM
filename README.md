# A Novel Memetic Algorithm for Energy-efficient Distributed Heterogeneous Flexible Job Shop Scheduling: Case Studies in UAVs Delivery

## Instruction

### 1. Download pybind11

download pybind11 from [https://github.com/pybind/pybind11](https://github.com/pybind/pybind11)

### 2. Compile using Cmake

```
mkdir build
cd build
cmake ..
make
```

You will get binary files according to your system and Python version, such as ```LS.cpython-310-x86_64-linux-gnu.so``` , ```LS.cp39-win_amd64.pyd``` or ```LS.cpython-39-darwin.so```

### 3. Run

```
python main.py
```

## Data

Benchmark instances for distributed heterogeneous flexible job-shop scheduling problem

[https://github.com/cls1277/DHFJSP-benchmark](https://github.com/cls1277/DHFJSP-benchmark)

## PyCode

The ```pycode``` folder contains the python version of the code, but it runs slower, which is why the C++ code is implemented. But some of the code has been modified since then, **so the C++ code is newer and more comprehensive than the python code**.

If you don't know C++ at all, it is recommended to look at the python version. If you have any questions, you need to check the final implementation against the C++ version of the code.

## MatlabCode

The ```matlabcode``` folder is the MOEA-D code implemented based on MSVC, MatlabR2022b's MFX toolbox and [PlatEMO](https://github.com/BIMK/PlatEMO)

## Citation

comming soon...