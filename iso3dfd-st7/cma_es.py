import sys
sys.path.append('/usr/users/st76i/st76i_4/.local/lib/python3.8/site-packages')
import cma
from mpi4py import MPI
import numpy as np
import argparse
import starter

def parallel_cma_es(comm, initial_point, sigma, population_size, bounds):
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Divide the parameter space among MPI processes
    subspace_bounds = (
        np.array([bounds[0][0] + rank * (bounds[0][1] - bounds[0][0]) / size] * len(initial_point)),
        np.array([bounds[0][0] + (rank + 1) * (bounds[0][1] - bounds[0][0]) / size] * len(initial_point))
    )

    # Initialize the CMA-ES optimizer for each process
    es = cma.CMAEvolutionStrategy(initial_point, sigma, {'popsize': population_size, 'BoundaryHandler': cma.BoundTransform})
    es.opts['bounds'] = subspace_bounds

    process_call_count = 0

    while not es.stop():
        # Generate new candidate solutions within the subspace
        candidates = es.ask()
        candidates = np.array(candidates)
        # Round the first parameter to the nearest multiple of 16
        candidates[:, 0] = np.round(candidates[:, 0] / 16) * 16

        try:
            # Evaluate candidate solutions (converting the parameters to integers first)
            fitnesses = [starter.run_process_parametrized(np.rint(candidate).astype(int)) for candidate in candidates]
            process_call_count += len(candidates)
        except Exception as e:
            print(f"Process {rank} - Exception occurred during candidate evaluation: {str(e)}")
            raise

        # Convert maximization to minimization
        fitnesses = [-fitness for fitness in fitnesses]

        # Update the CMA-ES optimizer with the fitness values
        es.tell(candidates, fitnesses)

        # Print the current best solution and call count for each process
        print(f"Process {rank} - Current Best --- Cache parameters: {np.rint(es.result[0]).astype(int)}, GFlops: {-es.result[1]}, Call Count: {process_call_count}")

        # Save data for convergence plot
        if rank == 0:
            with open("data/convergence_data.txt", "a") as file:
                file.write(f"{es.countiter},{-es.result[1]}\n")

        # Save data for parameter evolution
        with open(f"data/parameter_evolution_process_{rank}.txt", "a") as file:
            file.write(",".join(map(str, np.rint(es.result[0]).astype(int))) + f",{-es.result[1]}\n")

        # Save data for fitness distribution
        with open(f"data/fitness_distribution_process_{rank}.txt", "a") as file:
            file.write(",".join(map(str, fitnesses)) + "\n")

        # Save data for parallel coordinates plot
        with open(f"data/parallel_coordinates_process_{rank}.txt", "a") as file:
            for candidate, fitness in zip(candidates, fitnesses):
                file.write(",".join(map(str, np.rint(candidate).astype(int))) + f",{-fitness}\n")

        # Gather call counts from all processes and save the global call count
        call_counts = comm.gather(process_call_count, root=0)
        if rank == 0:
            global_call_count = sum(call_counts)
            with open("data/global_call_count.txt", "a") as file:
                file.write(f"{es.countiter},{global_call_count}\n")
        comm.Barrier()

    best_solutions = comm.gather((np.rint(es.result[0]).astype(int), -es.result[1], process_call_count), root=0)

    if rank == 0:
        global_best_solution = max(best_solutions, key=lambda x: x[1])
        global_call_count = sum(solution[2] for solution in best_solutions)

        print("Global Best Points:", global_best_solution[0])
        print("Global Best Fitness:", global_best_solution[1])
        print("Total Calls to Cost Function:", global_call_count)

        # Save data for call count comparison
        with open("call_count_comparison.txt", "w") as file:
            for i, solution in enumerate(best_solutions):
                file.write(f"Process {i},{solution[2]}\n")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='CMA-ES for iso3dfd-st7')
    parser.add_argument('--sigma', type=float, default=4, help='Sigma for CMA-ES')
    parser.add_argument('--population_size', type=int, default=16, help='Population size for CMA-ES')
    args = parser.parse_args()

    sigma = args.sigma
    population_size = args.population_size

    bounds = [[32, 256]]  # Lower and upper bounds for all parameters
    initial_point = np.random.randint(bounds[0][0], bounds[0][1], size=3)

    comm = MPI.COMM_WORLD

    parallel_cma_es(comm, initial_point, sigma, population_size, bounds)