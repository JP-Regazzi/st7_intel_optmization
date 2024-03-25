from mpi4py import MPI
import numpy as np
import cma
import starter

call_count = 0

def parallel_cma_es(comm, initial_point, sigma, population_size, bounds):
    global call_count

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

    while not es.stop():
        # Generate new candidate solutions within the subspace
        candidates = es.ask()
        candidates = np.array(candidates)
        # Round the first parameter to the nearest multiple of 16
        candidates[:, 0] = np.round(candidates[:, 0] / 16) * 16

        try:
            # Evaluate candidate solutions (converting the parameters to integers first)
            fitnesses = [starter.run_process_parametrized(np.rint(candidate).astype(int)) for candidate in candidates]
            call_count += len(candidates)
        except Exception as e:
            print(f"Process {rank} - Exception occurred during candidate evaluation: {str(e)}")
            raise

        # Convert maximization to minimization
        fitnesses = [-fitness for fitness in fitnesses]

        # Update the CMA-ES optimizer with the fitness values
        es.tell(candidates, fitnesses)

        # Print the current best solution for each process
        print(f"Process {rank} - Current Best --- Cache parameters: {np.rint(es.result[0]).astype(int)}, GFlops: {-es.result[1]}")

    best_solutions = comm.gather((np.rint(es.result[0]).astype(int), -es.result[1]), root=0)

    if rank == 0:
        global_best_solution = max(best_solutions, key=lambda x: x[1])

        print("Global Best Points:", global_best_solution[0])
        print("Global Best Fitness:", global_best_solution[1])
        print("Total Calls to Cost Function:", call_count)


comm = MPI.COMM_WORLD

initial_point = np.array([128, 128, 128])
sigma = 32
population_size = 16
bounds = [[32, 256]]  # Lower and upper bounds for all parameters

parallel_cma_es(comm, initial_point, sigma, population_size, bounds)