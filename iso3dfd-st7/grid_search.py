from mpi4py import MPI
import numpy as np
import starter


def parallel_grid_search(comm, grid_values_i, grid_values_j, grid_values_k):
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Divide the grid values among MPI processes
    part_size_i = len(grid_values_i) // size
    part_size_j = len(grid_values_j) // size
    part_size_k = len(grid_values_k) // size

    start_i = rank * part_size_i
    end_i = (rank + 1) * part_size_i
    start_j = rank * part_size_j
    end_j = (rank + 1) * part_size_j
    start_k = rank * part_size_k
    end_k = (rank + 1) * part_size_k

    best_points_local = (1, 1, 1)
    current_maximum_local = 9999999

    # Iterate through the local part of the grid
    for i in grid_values_i[start_i:end_i]:
        for j in grid_values_j[start_j:end_j]:
            for k in grid_values_k[start_k:end_k]:
                temp_result = starter.run_process_parametrized(i, j, k)
                if temp_result > current_maximum_local:
                    current_maximum_local = temp_result
                    best_points_local = (i, j, k)

    # Gather the best points from all processes to rank 0
    best_points_global = comm.gather(best_points_local, root=0)
    current_maximum_global = comm.gather(current_maximum_local, root=0)

    # Rank 0 prints the global best points
    if rank == 0:
        global_best_index = np.argmax(current_maximum_global)
        print("Best Points (Global):", best_points_global[global_best_index])
        print("Current Maximum (Global):", current_maximum_global[global_best_index])


if __name__ == "__main__":
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()

    grid_values_i = range(32, 256, 32)
    grid_values_j = range(32, 256, 32)
    grid_values_k = range(32, 256, 32)

    parallel_grid_search(comm, grid_values_i, grid_values_j, grid_values_k)
