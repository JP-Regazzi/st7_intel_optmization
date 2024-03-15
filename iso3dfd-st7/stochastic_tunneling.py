import random
import math
from starter import run_process_parametrized, run_process
from mpi4py import MPI

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
""" 
def update_parameters(parameters, step_size):
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
 """
def update_parameters(parameters, step_size):
    neigh_paramaters = []
    
    for i in range(3):
        #print('i::', i)
        parameters_aux = parameters.copy()
        if i == 0:
            parameters_aux[i+5] = parameters_aux[i+5] + 16
        else:
            parameters_aux[i+5] = parameters_aux[i+5] + step_size
        #print(parameters_aux)
        neigh_paramaters.append(parameters_aux)
    #print("neigh: ", neigh_paramaters)
    return neigh_paramaters



def simulated_annealing(initial_parameters,step_size, temperature_initial, max_iteration):
    current_parameters = initial_parameters
    current_gflops = run_process(current_parameters)
    
    temp = temperature_initial

    
    for i in range(max_iteration):
        neigh_parameter = update_parameters(current_parameters, step_size)
        for neigh in neigh_parameter:

            print(neigh)
            neigh_gflops = run_process(neigh)
            if neigh_gflops > current_gflops:
                current_parameters = neigh
                current_gflops = neigh_gflops
                break
        temp *= 0.95
   
    return current_parameters, current_gflops

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
    current_gflops = run_process(current_parameters)
    
    Sbest = current_parameters
    Ebest = current_gflops
    k = 0
    foundBetter = True
    
    while k < max_k and foundBetter:
        print("modificacao: ", k)
        Sprime, Eprime = simulated_annealing(Sbest, step_size, temperature_initial, max_iteration)
        
        print("Sprime, Eprime", Sprime, Eprime)
        if Eprime > Ebest:
            Sbest = Sprime
            Ebest = Eprime
            Sbest = modify_sbest(Sbest, 0.8)
            k += 1
        else:
            Sbest = Ssave
            Ebest = Esave
            foundBetter = False

        Ssave = Sprime
        Esave = Eprime
    
    return Sbest, Ebest

def main(num_starting_points, step_size, temperature_initial, max_iteration, max_k):
    comm = MPI.COMM_WORLD
    rank = comm.Get_rank()
    size = comm.Get_size()
    print("rank", rank)
    print("size", size)
    # Split the starting points among processes
    starting_points = generate_starting_points(num_starting_points)
    print("starting points:", starting_points)
    chunk_size = num_starting_points // size
    print('chunk size', chunk_size)
    if chunk_size == 0:
        chunk_size = 1;
    starting_points_chunk = starting_points[rank * chunk_size: (rank + 1) * chunk_size]
    print("starting points chunk:", starting_points_chunk)

    # Run stochastic_tunneling_mpi for the assigned starting points
    local_results = []
    for start_point in starting_points_chunk:
        print('Estou no loop')
        local_results.append(stochastic_tunneling(start_point, step_size, temperature_initial, max_iteration, max_k))

    # Gather results from all processes
    all_results = comm.gather(local_results, root=0)

    if rank == 0:
        # Flatten the gathered results
        flattened_results = [result for sublist in all_results for result in sublist]

        print("Flattened results:", flattened_results)  # Print the flattened results
        if not flattened_results:
            print("No results found!")  # Print a message if flattened_results is empty
        else:
            best_solution = max(flattened_results, key=lambda x: x[1])
            print("Best Global Solution:", best_solution[0], best_solution[1])
            return best_solution
        best_solution = max(flattened_results, key=lambda x: x[1])
        print("Best Global Solution:", best_solution[0], best_solution[1])
        return best_solution

    return None


if __name__ == '__main__':
    num_starters = 3    
    step_size = 2
    temperature_initial = 1000
    max_iteration = 50
    max_k = 5
    max_stable_runs = 25
    

    main(num_starters, step_size, temperature_initial, max_iteration, max_k)