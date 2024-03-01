import subprocess
import argparse
import uuid
import os
import re

NB_OF_PB = 256
DEFAULT_SIZE = 4096

def extract_fitness(text):
    pattern = r'(\d+(\.\d+)?)\s*GFlops'
    fitness = re.search(pattern, text).group()
    return fitness

def deploySUBP(cache_blocking, n_items=100, n_threads=32):
    """
    :param int n_threads
    :param int n_items
    :param (int*int*int) cache_blocking
    """
    msg = f"Parameters: \n\t- Number of threads: {n_threads} \n\t- Number of items: {n_items} \n\t- Cache blocking: {cache_blocking}"
    print(msg)
    cmd = f"bin/iso3dfd_dev13_cpu_avx2.exe {NB_OF_PB} {NB_OF_PB} {NB_OF_PB} {n_threads} {n_items} {cache_blocking[0]} {cache_blocking[1]} {cache_blocking[2]}"
    print(f"Executed command: {cmd}")
    print("**********")
    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    output = str(res.stdout,'utf-8')
    fitness = extract_fitness(output)
    print(f"Fitness:{fitness}")

def cmdLineParsing():
    parser = argparse.ArgumentParser()
    parser.add_argument("--items", help="N_items", default=100, type=int)
    parser.add_argument("--cache", nargs="+", default=[32,32,32], type=int)
    parser.add_argument("--threads", default=32, type=int)
    args = parser.parse_args()
    n_items = args.items
    n_threads = args.threads
    cache_blocking = tuple(args.cache)
    return (n_items, cache_blocking, n_threads)

print("Deployment")
args = cmdLineParsing()
deploySUBP(*args)
