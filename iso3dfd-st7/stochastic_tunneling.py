import random
import math
from starter import run_process
from mpi4py import MPI
import argparse


def generate_starting_points(num_starting_points):
    starting_points = []

    for _ in range(num_starting_points):
        starting_point = []
        ran_block = 256
        for i in range(8):
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


def update_parameters(parameters, step_size):
    neigh_paramaters = []
    
    for i in range(3):
        parameters_aux = parameters.copy()
        if i == 0:
            parameters_aux[i+5] = parameters_aux[i+5] + 16
        else:
            parameters_aux[i+5] = parameters_aux[i+5] + step_size
        neigh_paramaters.append(parameters_aux)
    return neigh_paramaters


def simulated_annealing(initial_parameters,step_size, temperature_initial, max_iteration):
    current_parameters = initial_parameters
    temp = temperature_initial
    number_of_runs = 1
    current_gflops = run_process(current_parameters)
    
    for i in range(max_iteration):
        neigh_parameter = update_parameters(current_parameters, step_size)
        for neigh in neigh_parameter:
            neigh_gflops = run_process(neigh)
            number_of_runs += 1
            if neigh_gflops > current_gflops:
                current_parameters = neigh
                current_gflops = neigh_gflops
                break
        temp *= 0.95
   
    return current_parameters, current_gflops, number_of_runs


def modify_sbest(sbest, factor):
    modified_sbest = sbest
    for i in range(5, len(sbest)):
        if i == 5:
            modified_sbest[i] = modified_sbest[i] - 16 
        else:
            modified_sbest[i] = int(modified_sbest[i] * factor)

    print("Disturbed: ", modified_sbest)
    return modified_sbest


def stochastic_tunneling(initial_parameters, step_size, temperature_initial, max_iteration, max_k):
    current_parameters = initial_parameters
    number_of_runs = 1
    current_gflops = run_process(current_parameters)

    Sbest = current_parameters
    Ebest = current_gflops
    k = 0
    foundBetter = True
    
    while k < max_k and foundBetter:
        print("Update: ", k)
        Sprime, Eprime, temp_runs = simulated_annealing(Sbest, step_size, temperature_initial, max_iteration)
        number_of_runs += temp_runs

        if Eprime > Ebest:
            Sbest = Sprime
            Ebest = Eprime
            Sbest = modify_sbest(Sbest, 0.8)
            k += 1
            print(f"Current Maximum --- Parameters: {Sprime}, GFlops: {Eprime}")
        else:
            Sbest = Ssave
            Ebest = Esave
            foundBetter = False

        Ssave = Sprime
        Esave = Eprime
    
    return Sbest, Ebest, number_of_runs


def main(step_size, temperature_initial, max_iteration, max_k):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    num_starting_points = size

    # Split the starting points among processes
    starting_points = generate_starting_points(num_starting_points)
    chunk_size = num_starting_points // size
    if chunk_size == 0:
        chunk_size = 1
    starting_points_chunk = starting_points[rank * chunk_size: (rank + 1) * chunk_size]

    # Run stochastic_tunneling_mpi for the assigned starting points
    local_results, number_of_local_runs = [], 0
    for start_point in starting_points_chunk:
        Sbest, Ebest, number_of_runs = stochastic_tunneling(start_point, step_size, temperature_initial, max_iteration, max_k)
        local_results.append((Sbest, Ebest))
        number_of_local_runs += number_of_runs

    # Gather results from all processes
    all_results = comm.gather(local_results, root=0)
    total_number_of_runs = comm.reduce(number_of_local_runs, op=MPI.SUM, root=0)

    if rank == 0:
        # Flatten the gathered results
        flattened_results = [result for sublist in all_results for result in sublist]

        print("Flattened results:", flattened_results)  # Print the flattened results
        if not flattened_results:
            print("No results found!")  # Print a message if flattened_results is empty
        else:
            best_solution = max(flattened_results, key=lambda x: x[1])
            print("Best Global Solution:", best_solution[0], best_solution[1])
            print("Total number runs:", total_number_of_runs)
            return best_solution
        best_solution = max(flattened_results, key=lambda x: x[1])

        return best_solution

    return None


<<<<<<< HEAD

step_size = 2
temperature_initial = 1000
max_iteration = 50
max_k = 5


main(step_size, temperature_initial, max_iteration, max_k)
=======
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Stochastic Tunneling')
    parser.add_argument('--num_starters', type=int, default=3, help='Number of starting points')
    parser.add_argument('--step_size', type=int, default=2, help='Step size')
    parser.add_argument('--temperature_initial', type=int, default=1000, help='Initial temperature')
    parser.add_argument('--max_iteration', type=int, default=50, help='Maximum number of iterations')
    parser.add_argument('--max_k', type=int, default=5, help='Maximum value of k')
    args = parser.parse_args()

    main(args.num_starters, args.step_size, args.temperature_initial, args.max_iteration, args.max_k)
>>>>>>> cli
