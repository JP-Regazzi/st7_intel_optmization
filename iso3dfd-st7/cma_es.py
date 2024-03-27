import sys
sys.path.append('/usr/users/st76i/st76i_4/.local/lib/python3.8/site-packages')
import cma
from mpi4py import MPI
import numpy as np
import argparse
import starter
import warnings
from cma.evolution_strategy import InjectionWarning

warnings.simplefilter("ignore", InjectionWarning)

def parallel_cma_es(comm, sigma, population_size, bounds):
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Set a unique random seed for each process
    np.random.seed(rank)

    # Vectorize the starter.run_process_parametrized function
    run_process_parametrized_vec = np.vectorize(starter.run_process_parametrized, signature='(n)->()')

    # Generate 8 random initial points within the bounds for each process
    initial_points = np.random.rand(8, len(bounds)) * (bounds[:, 1] - bounds[:, 0]) + bounds[:, 0]
    initial_points = np.round(initial_points / 16) * 16  # Round all parameters to the nearest multiple of 16

    process_call_count = 0

    for initial_point in initial_points:
        es = cma.CMAEvolutionStrategy(initial_point, sigma, {'popsize': population_size, 'BoundaryHandler': cma.BoundTransform})
        es.opts['bounds'] = bounds

        while not es.stop():
            # Generate new candidate solutions within the whole space
            candidates = es.ask()
            candidates = np.clip(candidates, bounds[:, 0], bounds[:, 1])

            # Round all parameters to the nearest multiple of 16
            candidates = np.round(candidates / 16) * 16
            try:
                # Evaluate candidate solutions (converting the parameters to integers first)
                fitnesses = run_process_parametrized_vec(np.rint(candidates).astype(int))
                process_call_count += len(candidates)
            except Exception as e:
                print(f"Process {rank} - Exception occurred during candidate evaluation: {str(e)}")
                raise

            # Update the CMA-ES optimizer with the fitness values
            es.tell(candidates, -fitnesses)

            # Find the best solution for the current process
            local_best_fitness = np.array([np.max(fitnesses)])
            local_best_solution = candidates[np.argmax(fitnesses)]

            # Print the current best solution and call count for each process
            print(f"Process {rank} - Current Best --- Cache parameters: {np.rint(local_best_solution).astype(int)}, GFlops: {local_best_fitness[0]}, Call Count: {process_call_count}")

            # Save data for local best solution and fitness
            with open(f"data/local_best_process_{rank}.txt", "a") as file:
                file.write(",".join(map(str, np.rint(local_best_solution).astype(int))) + f",{local_best_fitness[0]}\n")

            # Save data for parameter evolution
            with open(f"data/parameter_evolution_process_{rank}.txt", "a") as file:
                file.write(",".join(map(str, np.rint(local_best_solution).astype(int))) + f",{local_best_fitness[0]}\n")

            # Save data for fitness distribution
            with open(f"data/fitness_distribution_process_{rank}.txt", "a") as file:
                file.write(",".join(map(str, fitnesses)) + "\n")

            # Save data for parallel coordinates plot
            with open(f"data/parallel_coordinates_process_{rank}.txt", "a") as file:
                for candidate, fitness in zip(candidates, fitnesses):
                    file.write(",".join(map(str, np.rint(candidate).astype(int))) + f",{fitness}\n")

    # Gather call counts from all processes and save the global call count
    global_call_count = np.array([0])
    comm.Allreduce(np.array([process_call_count]), global_call_count, op=MPI.SUM)
    if rank == 0:
        with open("data/global_call_count.txt", "a") as file:
            file.write(f"{es.countiter},{global_call_count[0]}\n")
    comm.Barrier()

    if rank == 0:
        print(f"Process {rank} - Best Solution: {np.rint(local_best_solution).astype(int)}")
        print(f"Process {rank} - Best Fitness: {local_best_fitness[0]}")
        print(f"Process {rank} - Total Calls to Cost Function: {process_call_count}")

        # Save data for call count comparison
        call_counts = comm.gather(process_call_count, root=0)
        with open("call_count_comparison.txt", "w") as file:
            for i, count in enumerate(call_counts):
                file.write(f"Process {i},{count}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='CMA-ES for iso3dfd-st7')
    parser.add_argument('--sigma', type=float, default=8, help='Sigma for CMA-ES')
    parser.add_argument('--population_size', type=int, default=4, help='Population size for CMA-ES')
    parser.add_argument('--lower_bound', type=int, default=32, help='Lower bound for parameters')
    parser.add_argument('--upper_bound', type=int, default=256, help='Upper bound for parameters')
    args = parser.parse_args()

    sigma = args.sigma
    population_size = args.population_size

    bounds = np.array([[args.lower_bound, args.upper_bound] for _ in range(3)])  # Lower and upper bounds for all parameters

    comm = MPI.COMM_WORLD

    parallel_cma_es(comm, sigma, population_size, bounds)