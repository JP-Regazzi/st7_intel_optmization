import random
import math
from starter import run_process_parametrized, run_process


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


def simulated_annealing(initial_parameters,step_size, temperature_initial, max_iteration):
    current_parameters = initial_parameters
    current_gflops = run_process(current_parameters)
    
    temp = temperature_initial

    
    for i in range(max_iteration):
        neigh_parameter = update_parameters(current_parameters, step_size)
        print(neigh_parameter)
        neigh_gflops = run_process(neigh_parameter)
        if neigh_gflops > current_gflops:
            current_parameters = neigh_parameter  
            current_gflops = neigh_gflops
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
            Sbest = modify_sbest(Sbest, 0.80)
            k += 1
        else:
            Sbest = Sprime
            Ebest = Eprime
            foundBetter = False
    
    return Sbest, Ebest

if __name__ == '__main__':
    num_starters = 1
    step_size = 4
    temperature_initial = 1000
    max_iteration = 10
    max_k = 5
    starting_points = generate_starting_points(num_starters)
    for point in starting_points:
        print('points: ', point)
        best_paramenter, best_gflops = stochastic_tunneling(point, step_size, temperature_initial, max_iteration, max_k)

    print("best solution is:", best_paramenter, best_gflops)