import random
from starter import extract_fitness, run_process
import concurrent.futures
from mpi4py import MPI

def perturb_parameters(parameters, step_size):
    # Randomly select an index to perturb
    index_to_perturb = [i for i in range(5, len(parameters)) if i !=4]
    index_to_perturb = random.choice(index_to_perturb)
    #print(index_to_perturb)

    # Perturb the selected parameter by a small step size
    if index_to_perturb != 0 and index_to_perturb != 5:
        perturbed_parameters = [
        param + step_size if i == index_to_perturb else param for i, param in enumerate(parameters)
    ]
    else:
        perturbed_parameters = [
        param + 16 if i == index_to_perturb else param for i, param in enumerate(parameters)
    ]
    return perturbed_parameters

def hill_climbing(initial_parameters, step_size, max_iterations, max_stable_runs):
    current_parameters = initial_parameters
    current_gflops = run_process(current_parameters)
    stable_runs = 0

    for iteration in range(max_iterations):
        # Perturb parameters
        neighbor_parameters = perturb_parameters(current_parameters, step_size)
        print(neighbor_parameters)
        neighbor_gflops = run_process(neighbor_parameters)

        if neighbor_gflops > current_gflops:
            current_parameters = neighbor_parameters    
            current_gflops = neighbor_gflops
            stable_runs = 0  # Reset stable runs if an improvement is found
        else:
            stable_runs += 1

        if stable_runs >= max_stable_runs:
            # If performance hasn't improved for a certa in number of runs, break the loop
            break

    return current_parameters, current_gflops

def generate_starting_points(num_starting_points, parameters_length):
    starting_points = []

    for _ in range(num_starting_points):
        starting_point = []
        ran_block = 256
        for i in range(parameters_length):
            if i == 4:
                # Fix the value at index 4 to 100
                starting_point.append(100)
            elif i == 0:
                starting_point.append(ran_block)
            elif i == 5:
                starting_point.append(random.randint(1, 11) * 16)    
            elif i == 6 or i == 7:  
                starting_point.append(random.randint(1, 16))
            elif i == 3:
                starting_point.append(32)
            else:
                starting_point.append(ran_block)

        starting_points.append(starting_point)

    return starting_points

def run_multiple_starting_points_parallel(num_starting_points, parameters_length, max_iterations, max_stable_runs, step_size):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Split the starting points among processes
    starting_points = generate_starting_points(num_starting_points, parameters_length)
    chunk_size = len(starting_points) // size
    starting_points_chunk = starting_points[rank * chunk_size: (rank + 1) * chunk_size]

    # Run hill climbing for the assigned starting points
    local_results = []
    for start_point in starting_points_chunk:
        local_results.append(hill_climbing(start_point, step_size, max_iterations, max_stable_runs))

    # Gather results from all processes
    all_results = comm.gather(local_results, root=0)

    if rank == 0:
        # Flatten the gathered results
        flattened_results = [result for sublist in all_results for result in sublist]
        best_solution = max(flattened_results, key=lambda x: x[1])
        print("Best Global Solution:", best_solution[0], best_solution[1])
        return best_solution

    return None

# Example usage
num_starting_points = 3
parameters_length = 8
max_iterations = 50
max_stable_runs = 10
step_size = 4

best_global_solution = run_multiple_starting_points_parallel(num_starting_points, parameters_length, max_iterations, max_stable_runs, step_size)
print("Best Global Solution:", best_global_solution)