import random
from launch import getFitness
import argparse
from mpi4py import MPI
import numpy as np

"""def getFitness(cache_blocking, verbose = 0):
    x, y, z = cache_blocking
    val = x**2 + y**2 + z**2
    if verbose >= 0: print(f"Fitness: {val}")
    return val"""

def hill_climbing_3d_parallel(start_x, start_y, start_z, steps=100, step_size=1, verbose=0):
    # Initialize MPI variables
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    current_x, current_y, current_z = 16*start_x, start_y, start_z
    current_fitness = getFitness((current_x, current_y, current_z), verbose=verbose)
    
    for _ in range(steps):
        neighbors = []
        # Only generate neighbors list once (e.g., by rank 0) and then broadcast it
        if rank == 0:
            for dx in [-step_size, 0, step_size]:
                for dy in [-step_size, 0, step_size]:
                    for dz in [-step_size, 0, step_size]:
                        if dx == 0 and dy == 0 and dz == 0:
                            continue  # Skip the current point itself
                        new_x, new_y, new_z = current_x + 16*dx, current_y + dy, current_z + dz
                        neighbors.append((new_x, new_y, new_z))
        neighbors = comm.bcast(neighbors, root=0)

        # Split the list of neighbors between MPI processes
        local_neighbors = np.array_split(neighbors, size)[rank]
        
        # Evaluate local neighbors
        best_local_fitness = current_fitness
        best_local_neighbor = None
        for x, y, z in local_neighbors:
            fitness = getFitness((x, y, z), verbose=verbose)
            if fitness > best_local_fitness:
                best_local_neighbor = (x, y, z)
                best_local_fitness = fitness

        # Collect the best local results from all processes
        all_best_locals = comm.gather((best_local_fitness, best_local_neighbor), root=0)

        if rank == 0:
            # Determine the global best
            global_best_fitness = current_fitness
            global_best_neighbor = None
            for fitness, neighbor in all_best_locals:
                if fitness > global_best_fitness:
                    global_best_fitness = fitness
                    global_best_neighbor = neighbor

            # Update current position if a better neighbor was found
            if global_best_neighbor:
                current_x, current_y, current_z = global_best_neighbor
                current_fitness = global_best_fitness
        # Broadcast the new current position and fitness to all processes
        current_x, current_y, current_z, current_fitness = comm.bcast((current_x, current_y, current_z, current_fitness), root=0)

    if rank == 0:
        # Only the master process needs to return the final result
        return current_x, current_y, current_z, current_fitness
    else:
        return None  # Other processes do not need to return anything


if __name__ == "__main__":
    # Get seed by --seed argument
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", help="seed", default=42, type=int)
    parser.add_argument("--steps", help="steps", default=1000, type=int)
    parser.add_argument("--stepsize", help="stepsize", default=1, type=int)
    parser.add_argument("--verbose", help="verbose", default=0, type=int)
    args = parser.parse_args()
    seed = args.seed
    verbose = args.verbose
    steps = args.steps
    stepsize = args.stepsize
    # Random starting point in (0, 100)
    random.seed(seed)
    start_x, start_y, start_z = random.randrange(1, 11), random.randrange(1, 128), random.randrange(1, 128)
    final_x, final_y, final_z, final_fitness = hill_climbing_3d_parallel(start_x, start_y, start_z, verbose)
    print(f"Final position: ({final_x}, {final_y}, {final_z}) with fitness {final_fitness}")

