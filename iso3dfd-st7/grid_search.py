from mpi4py import MPI
import numpy as np
import starter


def parallel_grid_search(comm, grid_values_i, grid_values_j, grid_values_k):
    # Get MPI node attributes
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Divide the grid among MPI processes
    start_i = rank * (len(grid_values_i) // size)
    end_i = (rank + 1) * (len(grid_values_i) // size)

    # Define starting variables
    current_maximum_local, best_points_local = 0, (0, 0, 0)

    # Iterate through the local part of the grid
    for i in grid_values_i[start_i:end_i]:
        for j in grid_values_j:
            for k in grid_values_k:
                temp_result = starter.run_process_parametrized([i, j, k])
                if temp_result > current_maximum_local:
                    current_maximum_local = temp_result
                    best_points_local = (i, j, k)
        print(f"Current Maximum  ---  GFlops: {current_maximum_local}, Cache parameters: {best_points_local}")

    # Gather the best points from all processes to rank 0
    best_points_global = comm.gather(best_points_local, root=0)
    current_maximum_global = comm.gather(current_maximum_local, root=0)

    # Rank 0 prints the global best points
    if rank == 0:
        global_best_index = np.argmax(current_maximum_global)
        print("Best Points:", best_points_global[global_best_index])
        print("Current Maximum:", current_maximum_global[global_best_index])
        print("Total number of runs:", len(grid_values_i)*len(grid_values_j)*len(grid_values_k))



comm = MPI.COMM_WORLD

grid_values_i = range(32, 256, 32)
grid_values_j = range(32, 256, 32)
grid_values_k = range(32, 256, 32)

parallel_grid_search(comm, grid_values_i, grid_values_j, grid_values_k)
