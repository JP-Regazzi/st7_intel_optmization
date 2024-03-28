import sys
sys.path.append('/usr/users/st76i/st76i_4/.local/lib/python3.8/site-packages')
import cma
from mpi4py import MPI
import numpy as np
import argparse
import starter
from starter import run_process_parametrized
import warnings
from cma.evolution_strategy import InjectionWarning

warnings.simplefilter("ignore", InjectionWarning)

def objective(x, compilation):
    i, j, k = x
    i_sixteened = int(round(i / 16) * 16)
    x_scaled = i_sixteened, j, k
    return -starter.run_process_parametrized(x_scaled, compilation)

def parallel_cma_es(comm, sigma, population_size, bounds_legacy, compilation):
    rank = comm.Get_rank()
    size = comm.Get_size()

    np.random.seed(rank)

    bounds_x, bounds_y, bounds_z = (16, 256), (16, 256), (16, 256)
    bounds_list = [bounds_x, bounds_y, bounds_z]
    bounds = [[bounds_x[0], bounds_y[0], bounds_z[0]], [bounds_x[1], bounds_y[1], bounds_z[1]]]

    initial_point = [np.random.randint(b[0], b[1]) for b in bounds_list]

    process_call_count = 0

    es = cma.CMAEvolutionStrategy(initial_point, sigma, {'bounds': bounds, 'popsize':population_size})
    es.opts['bounds'] = bounds

    while not es.stop():
        candidates = es.ask()
        
        # Ensure first parameter of candidates is within the specified range
        candidates = np.clip(candidates, bounds[0], bounds[1])
        
        try:
            fitnesses = [objective(candidate, compilation) for candidate in candidates]
            process_call_count += len(candidates)
        except Exception as e:
            print(f"Process {rank} - Exception occurred during candidate evaluation: {str(e)}")
            raise

        es.tell(candidates, fitnesses)

        # Find the best solution for the current process
        local_best_fitness = np.array([np.min(fitnesses)])
        local_best_solution = candidates[np.argmin(fitnesses)]
        local_best_solution_scaled = local_best_solution.copy() 
        local_best_solution_scaled[0] = int(round(local_best_solution_scaled[0] / 16) * 16)

        print(f"Node {rank} - Current Best --- Cache parameters: {local_best_solution_scaled.astype(int)}, GFlops: {-local_best_fitness[0]}, Call Count: {process_call_count}")

        with open(f"data/local_best_process_{rank}.txt", "a") as file:
            file.write(",".join(map(str, local_best_solution_scaled.astype(int))) + f",{-local_best_fitness[0]}\n")

        with open(f"data/parameter_evolution_process_{rank}.txt", "a") as file:
            file.write(",".join(map(str, local_best_solution_scaled.astype(int))) + f",{-local_best_fitness[0]}\n")

        with open(f"data/fitness_distribution_process_{rank}.txt", "a") as file:
            file.write(",".join(map(str, -np.array(fitnesses))) + "\n")

        # Save data for parallel coordinates plot
        with open(f"data/parallel_coordinates_process_{rank}.txt", "a") as file:
            for candidate, fitness in zip(candidates, -np.array(fitnesses)):
                candidate_scaled = candidate.copy()
                file.write(",".join(map(str, np.rint(candidate_scaled).astype(int))) + f",{fitness}\n")

        # Save process number, call count, and best fitness to a txt file
        with open("data/process_data.txt", "a") as file:
            file.write(f"{rank},{process_call_count},{-local_best_fitness[0]}\n")

    if rank == 0:
        print(f"Process {rank} - Best Solution: {np.rint(local_best_solution).astype(int)}")
        print(f"Process {rank} - Best Fitness: {-local_best_fitness[0]}")
        print(f"Process {rank} - Total Calls to Cost Function: {process_call_count}")

        # Save data for call count comparison
        call_counts = comm.gather(process_call_count, root=0)
        with open("call_count_comparison.txt", "w") as file:
            for i, count in enumerate(call_counts):
                file.write(f"Process {i},{count}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='CMA-ES for iso3dfd-st7')
    parser.add_argument('--sigma', type=float, default=4, help='Sigma for CMA-ES')
    parser.add_argument('--population_size', type=int, default=4, help='Population size for CMA-ES')
    parser.add_argument('--lower_bound', type=int, default=32, help='Lower bound')
    parser.add_argument('--upper_bound', type=int, default=256, help='Upper bound')
    parser.add_argument('--compilation', type=str, default='O3', help='Compilation type')
    args = parser.parse_args()

    sigma = args.sigma
    population_size = args.population_size
    compilation = args.compilation

    bounds = np.array([[1, 16]] + [[args.lower_bound, args.upper_bound] for _ in range(2)])

    comm = MPI.COMM_WORLD

    parallel_cma_es(comm, sigma, population_size, bounds, compilation)