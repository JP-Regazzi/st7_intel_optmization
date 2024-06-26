import os
import subprocess
import sys
import re

COMPILE_COMMAND = 'make Olevel=-O3 simd=avx2 last'
INTEL_MODULE_LOAD = 'module load intel-oneapi-compilers/2023.1.0/gcc-11.4.0'

def parse_arguments():
    arguments = sys.argv[1:]
    return arguments

def extract_fitness(text):
    pattern = r'(\d+(\.\d+)?)\s*GFlops' 
    fitness = re.search(pattern, text).group()
    return fitness

def compile():
    os.system(INTEL_MODULE_LOAD)
    os.system(COMPILE_COMMAND)

def run_process(parameters):
    command = ['bin/iso3dfd_dev13_cpu_avx2.exe']
    
    # Extend the command with the provided parameters
    command.extend(map(str, parameters))
    result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
    result = result.stdout 
    gflops = float(extract_fitness(result)[:5])

    #print(f"GFlops: {gflops}")
    return gflops

def run_process_parametrized(cache_parameters, compilation="O3"):
    # compilation is either O3 or Ofast
    command = [f'bin/iso3dfd_dev13_cpu_avx2_{compilation}.exe']
    parameters = ["256", "256", "256", "32", "100", f"{cache_parameters[0]}", f"{cache_parameters[1]}", f"{cache_parameters[2]}"]
    command.extend(parameters)

    result = subprocess.run(command, stdout=subprocess.PIPE, text=True)
    result = result.stdout 

    gflops = float(extract_fitness(result)[:5])

    #print(f"Parameters: {parameters} GFlops: {gflops}")
    return gflops

if __name__ == '__main__':

    compile()
    run_process()