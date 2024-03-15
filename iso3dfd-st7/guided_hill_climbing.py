import random
from mpi4py import MPI
from starter import run_process_parametrized


def update_parameters(parameters, step_size):
    # Ensure the first element is divisible by 16
    parameters[0] = max(16, parameters[0] + random.randint(-step_size, step_size) * 16)
    # Update the rest of the elements in the list
    for i in range(1, len(parameters)):
        parameters[i] = max(1, parameters[i] + random.randint(-step_size, step_size))
    return parameters


def hill_climbing(initial_parameters, step_size, max_stable_runs):
    current_parameters = initial_parameters
    print(initial_parameters)
    current_gflops = run_process_parametrized(current_parameters[0], current_parameters[1], current_parameters[2])
    stable_runs = 0
    
    #Implement guided hill climbing
    covered_zones = []
    begin_zone = None
    value_zone = 0
    init_zone = True
    while True:

        # Update parameters
        neighbor_parameters = update_parameters(current_parameters, step_size)
        covered_area = False
        value = None
        for zone in covered_zones:
            begin = zone[0][0]
            end = zone[0][1]
            value = zone[1]
            if neighbor_parameters[0] >= begin[0] and neighbor_parameters[0] <= end[0] and neighbor_parameters[1] >= begin[1] and neighbor_parameters[1] <= end[1] and neighbor_parameters[2] >= begin[2] and neighbor_parameters[2] <= end[2]:
                neighbor_gflops = value
            else:
                covered_area = True
                break
        if covered_area:
            neighbor_gflops = value
        else:
            neighbor_gflops = run_process_parametrized(neighbor_parameters[0], neighbor_parameters[1], neighbor_parameters[2])

        if neighbor_gflops > current_gflops:
            if init_zone:
                begin_zone = current_parameters
                value_zone = neighbor_gflops
                init_zone = False
            current_parameters = neighbor_parameters    
            current_gflops = neighbor_gflops
            stable_runs = 0  # Reset stable runs if an improvement is found
            print(f"Parameters: {current_parameters}, GFlops: {current_gflops}")
        else:
            if begin_zone is not None:
                new_zone = [[begin_zone, current_parameters], value_zone] 
                covered_zones.append(new_zone)
                init_zone = True
            stable_runs += 1

        # If performance isn't improving, break the loop
        if stable_runs >= max_stable_runs:
            break

    return current_parameters, current_gflops


def generate_starting_points(num_starting_points):
    starting_points = []
    for i in range(1, num_starting_points+1):
        starting_point = []
        starting_point.append(random.randint(1, 4) * 16 * i)
        starting_point.append(random.randint(1, 16) * i)
        starting_point.append(random.randint(1, 16) * i)
        starting_points.append(starting_point)
    return starting_points


def main(num_starting_points, max_stable_runs, step_size):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()

    # Split the starting points among processes
    starting_points = generate_starting_points(num_starting_points)
    chunk_size = len(starting_points) // size
    starting_points_chunk = starting_points[rank * chunk_size: (rank + 1) * chunk_size]

    # Run hill climbing for the assigned starting points
    local_results = []
    for start_point in starting_points_chunk:
        print(f"starting point: {start_point}")
        local_results.append(hill_climbing(start_point, step_size, max_stable_runs))

    # Gather results from all processes
    all_results = comm.gather(local_results, root=0)

    if rank == 0:
        # Flatten the gathered results
        flattened_results = [result for sublist in all_results for result in sublist]
        best_solution = max(flattened_results, key=lambda x: x[1])
        print("Best Global Solution:", best_solution[0], best_solution[1])
        return best_solution

    return None

print("teste")
#if __name__ == "main":
print('Begin code')    
# Parameters
num_starting_points = 8
max_stable_runs = 20
step_size = 4

main(num_starting_points, max_stable_runs, step_size)
