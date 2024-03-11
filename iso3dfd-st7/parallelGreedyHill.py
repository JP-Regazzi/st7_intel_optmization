import random
import argparse
import time
from mpi4py import MPI
import numpy as np
from launch import getFitness

def get_fitness_debug(cache_blocking, verbose=0):
    x, y, z = cache_blocking
    val = x**2 + y**2 + z**2
    if verbose > 0:
        print(f"Fitness: {val}")
    return val

def hill_climbing_3d_parallel(start_x, start_y, start_z, steps=100, step_size=1, verbose=0):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Convert start positions to their actual values based on their rank
    current_x, current_y, current_z = 16*start_x, start_y, start_z
    current_fitness = get_fitness_debug((current_x, current_y, current_z), verbose=verbose)

    for _ in range(steps):
        if rank == 0:
            neighbors = [(current_x + 16*dx, current_y + dy, current_z + dz) 
                         for dx in [-step_size, 0, step_size]
                         for dy in [-step_size, 0, step_size]
                         for dz in [-step_size, 0, step_size]
                         if not (dx == 0 and dy == 0 and dz == 0)]
        else:
            neighbors = None

        neighbors = comm.bcast(neighbors, root=0)
        local_neighbors = np.array_split(neighbors, size)[rank]

        best_local_fitness = current_fitness
        best_local_neighbor = (current_x, current_y, current_z)
        for x, y, z in local_neighbors:
            fitness = getFitness((x, y, z), verbose=verbose)
            if fitness > best_local_fitness:
                best_local_neighbor = (x, y, z)
                best_local_fitness = fitness

        all_best_locals = comm.gather((best_local_fitness, best_local_neighbor), root=0)

        if rank == 0:
            global_best_neighbor = max(all_best_locals, key=lambda item: item[0])[1]
            if global_best_neighbor != (current_x, current_y, current_z):
                current_x, current_y, current_z = global_best_neighbor
                current_fitness = getFitness(global_best_neighbor, verbose=verbose)
                
        current_x, current_y, current_z, current_fitness = comm.bcast((current_x, current_y, current_z, current_fitness), root=0)

    if rank == 0:
        return current_x, current_y, current_z, current_fitness
    else:
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", help="Random seed for reproducibility", default=42, type=int)
    parser.add_argument("--steps", help="Number of steps for hill climbing", default=100, type=int)
    parser.add_argument("--stepsize", help="Step size for hill climbing", default=1, type=int)
    parser.add_argument("--verbose", help="Verbosity level", default=0, type=int)
    parser.add_argument("--timer", help="Time execution", default=1, type=int)
    args = parser.parse_args()

    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    random.seed(args.seed)
    start_x, start_y, start_z = random.randrange(1, 11), random.randrange(1, 128), random.randrange(1, 128)

    if rank == 0 and args.timer:
        start = time.time()

    final_result = hill_climbing_3d_parallel(start_x, start_y, start_z, args.steps, args.stepsize, args.verbose)
    
    if rank == 0:
        final_x, final_y, final_z, final_fitness = final_result
        print(f"Final position: ({final_x}, {final_y}, {final_z}) with fitness {final_fitness}")
        
        if args.timer:
            end = time.time()
            print("Time elapsed:", end - start)
