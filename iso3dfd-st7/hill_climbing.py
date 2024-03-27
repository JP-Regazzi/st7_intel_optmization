import random
from mpi4py import MPI
from starter import run_process_parametrized
import argparse

def update_parameters(parameters, step_size):
    # Ensure the first element is divisible by 16
    parameters[0] = max(16, parameters[0] + random.randint(-step_size, step_size) * 16)
    # Update the rest of the elements in the list
    for i in range(1, len(parameters)):
        parameters[i] = max(1, parameters[i] + random.randint(-step_size, step_size))
    return parameters


def hill_climbing(initial_parameters, step_size, max_stable_runs):
    number_of_runs = 0
    stable_runs = 0

    current_parameters = initial_parameters
    i, j, k = current_parameters[0], current_parameters[1], current_parameters[2]
    current_gflops, number_of_runs = run_process_parametrized(i, j, k), number_of_runs + 1

    while True:

        # Update parameters
        neighbor_parameters = update_parameters(current_parameters, step_size)
        #neighbor_i, neighbor_j, neighbor_k = neighbor_parameters[0], neighbor_parameters[1], neighbor_parameters[2]
        neighbor_gflops, number_of_runs = run_process_parametrized(neighbor_parameters), number_of_runs + 1

        if neighbor_gflops > current_gflops:
            current_parameters = neighbor_parameters    
            current_gflops = neighbor_gflops
            stable_runs = 0  # Reset stable runs if an improvement is found
            print(f"Parameters: {current_parameters}, GFlops: {current_gflops}")
        else:
            stable_runs += 1

        # If performance isn't improving, break the loop
        if stable_runs >= max_stable_runs:
            break

    return current_parameters, current_gflops, number_of_runs


def generate_starting_points(num_starting_points):
    starting_points = []
    for i in range(1, num_starting_points+1):
        starting_point = []
        starting_point.append(random.randint(1, 4) * 16 * i)
        starting_point.append(random.randint(1, 16) * i)
        starting_point.append(random.randint(1, 16) * i)
        starting_points.append(starting_point)
    return starting_points


def main(max_stable_runs, step_size):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Split the starting points among processes
    num_starting_points = size
    starting_points = generate_starting_points(num_starting_points)
    chunk_size = len(starting_points) // size
    starting_points_chunk = starting_points[rank * chunk_size: (rank + 1) * chunk_size]

    # Run hill climbing for the assigned starting points
    local_results, number_of_local_runs = [], 0
    for start_point in starting_points_chunk:
        params, gflops, number_of_runs = hill_climbing(start_point, step_size, max_stable_runs)
        local_results.append((params, gflops))
        number_of_local_runs += number_of_runs 

    # Gather results from all processes
    all_results = comm.gather(local_results, root=0)
    total_number_of_runs = comm.reduce(number_of_local_runs, op=MPI.SUM, root=0)
    
    if rank == 0:
        # Flatten the gathered results
        flattened_results = [result for sublist in all_results for result in sublist]
        best_solution = max(flattened_results, key=lambda x: x[1])
        print("Best Global Solution:", best_solution[0], best_solution[1])
        print("Total number runs:", total_number_of_runs)
        return best_solution

    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--max_stable_runs", type=int, default=20, help="Maximum number of stable runs")
    parser.add_argument("--step_size", type=int, default=4, help="Step size for parameter update")
    args = parser.parse_args()

    main(args.max_stable_runs, args.step_size)