import os
import subprocess
import sys
import re
from starter import extract_fitness, run_process
import random

def perturb_parameters(parameters, step_size):
    # Perturb all parameters by a small step size, except the one you want to keep constant (index 4).
    perturbed_parameters = [param + step_size if i != 4 else param for i, param in enumerate(parameters)]
    return perturbed_parameters

def hill_climbing(initial_parameters, step_size, max_iterations, max_stable_runs):
    current_parameters = initial_parameters
    current_gflops = run_process()
    stable_runs = 0

    for iteration in range(max_iterations):
        # Perturb parameters
        neighbor_parameters = perturb_parameters(current_parameters, step_size)
        neighbor_gflops = run_process()

        if neighbor_gflops > current_gflops:
            current_parameters = neighbor_parameters
            current_gflops = neighbor_gflops
            stable_runs = 0  # Reset stable runs if an improvement is found
        else:
            stable_runs += 1

        if stable_runs >= max_stable_runs:
            # If performance hasn't improved for a certain number of runs, break the loop
            break

    return current_parameters, current_gflops

if __name__ == '__main__':
    initial_parameters = [128, 128, 128, 16, 100, 8, 8, 8]  # Adjust as needed
    iterations = 50
    step_size = 16  

    best, gflops=  hill_climbing(initial_parameters,step_size, iterations, 10)
    print("the best paramerters are:", best, gflops)