import subprocess
import argparse
import re

NB_OF_PB = 256

def extract_fitness(text):
    pattern = r'(\d+(\.\d+)?)\s*GFlops'
    fitness = re.search(pattern, text).group()
    result = re.search(r'(\d+\.\d+)', fitness).group()
    return result

def getFitness(cache_blocking, n_items=100, n_threads=32, verbose=0):
    """
    :param int n_threads
    :param int n_items
    :param (int*int*int) cache_blocking
    """
    msg = f"Parameters: \n\t- Number of threads: {n_threads} \n\t- Number of items: {n_items} \n\t- Cache blocking: {cache_blocking}"
    cmd = f"bin/iso3dfd_dev13_cpu_avx2.exe {NB_OF_PB} {NB_OF_PB} {NB_OF_PB} {n_threads} {n_items} {cache_blocking[0]} {cache_blocking[1]} {cache_blocking[2]}"
    if verbose == 2:
        print(f"Executed command: {cmd}")
        print(msg)
    res = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
    output = str(res.stdout,'utf-8')
    fitness = extract_fitness(output)
    if verbose >= 0: print(f"Fitness: {fitness}")
    return float(fitness)

def cmdLineParsing():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cache", nargs="+", default=[32,32,32], type=int)
    parser.add_argument("--items", help="N_items", default=100, type=int)
    parser.add_argument("--threads", default=32, type=int)
    parser.add_argument("--verbose", default=0, type=int)
    args = parser.parse_args()
    n_items = args.items
    n_threads = args.threads
    cache_blocking = tuple(args.cache)
    verbose = args.verbose
    return (cache_blocking, n_items, n_threads, verbose)

if __name__ == "__main__":
    print("Deployment")
    args = cmdLineParsing()
    print(args)
    getFitness(*args)
