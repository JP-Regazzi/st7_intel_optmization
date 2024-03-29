import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import pandas as pd
import os

# Read data from the local_best_process_0.txt file
with open("iso3dfd-st7/data/local_best_process_0.txt", "r") as file:
    local_best_data = [list(map(float, line.strip().split(","))) for line in file]

# Read data from the parameter_evolution_process_0.txt file
with open("iso3dfd-st7/data/parameter_evolution_process_0.txt", "r") as file:
    parameter_evolution_data = [list(map(float, line.strip().split(","))) for line in file]

# Read data from the fitness_distribution_process_0.txt file
with open("iso3dfd-st7/data/fitness_distribution_process_0.txt", "r") as file:
    fitness_distribution_data = [list(map(float, line.strip().split(","))) for line in file]

# Read data from the process_data.txt file
with open("iso3dfd-st7/data/process_data.txt", "r") as file:
    process_data = [list(map(float, line.strip().split(","))) for line in file]

# Plot process data
plt.figure(figsize=(10, 6))
call_counts = [entry[1] for entry in process_data]
best_fitnesses = [entry[2] for entry in process_data]
plt.plot(call_counts, best_fitnesses, label="CMA-ES")

def moving_average(data, window_size=10):
    """Calculates moving average using a simple sliding window approach."""
    return 1.1*np.convolve(data, np.ones(window_size) / window_size, mode='valid')

files = [
    'Hill_Climbing.txt',
    'Guided_Hill_Climbing.txt',
    'Stochastic_Tunneling.txt'
]

for file in files:
    filepath = os.path.join("iso3dfd-st7/data", file)
    # Reading GFlops values
    with open(filepath, 'r') as f:
        gflops_values = moving_average([float(line.strip()) for line in f.readlines()])
    
    # Assuming each GFlops value is associated with a sequential call run for plotting
    call_runs = list(range(1, len(gflops_values) + 1))
    
    plt.plot(call_runs, gflops_values, label=file.split('.')[0].replace("_", " "))

plt.xlabel("Call Count")
plt.ylabel("GFlops")
plt.title("Performance Comparison for Different Methods")
plt.legend()
plt.show()


# Plot 3D best fitness and parameters
fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot(111, projection='3d')

x = [entry[0] for entry in local_best_data]
y = [entry[1] for entry in local_best_data]
z = [entry[2] for entry in local_best_data]
fitness = [entry[3] for entry in local_best_data]

scatter = ax.scatter(x, y, z, c=fitness, cmap='viridis', s=100)
ax.set_xlabel('Parameter 1')
ax.set_ylabel('Parameter 2')
ax.set_zlabel('Parameter 3')
ax.set_title('Best Fitness and Parameters')

plt.colorbar(scatter, label='Fitness')
plt.show()


# Read data from the parallel_coordinates_process_0.txt file
parallel_coordinates_data = pd.read_csv("iso3dfd-st7/data/parallel_coordinates_process_0.txt", header=None)

# Set the number of iterations and candidates per iteration
iterations = [0, 9, 19, 59, 249]  # Indices for iterations 1, 10, 20, and 60
candidates_per_iteration = 7

# Set the maximum limits for each axis
x_max = parallel_coordinates_data.iloc[:, 0].max()
y_max = parallel_coordinates_data.iloc[:, 1].max()
z_max = parallel_coordinates_data.iloc[:, 2].max()

# Iterate over each iteration
for i, iteration in enumerate(iterations):
    # Create a new figure for each iteration
    fig = plt.figure(figsize=(6, 6))
    ax = fig.add_subplot(111, projection='3d')

    # Extract the data for the current iteration
    start_index = iteration * candidates_per_iteration
    end_index = start_index + candidates_per_iteration
    iteration_data = parallel_coordinates_data.iloc[start_index:end_index]

    # Extract the parameter values and fitness values
    x = iteration_data.iloc[:, 0]
    y = iteration_data.iloc[:, 1]
    z = iteration_data.iloc[:, 2]
    fitness = iteration_data.iloc[:, 3]

    # Create a 3D scatter plot with color representing the fitness value
    scatter = ax.scatter(x, y, z, c=fitness, cmap='viridis', s=100)

    # Set the labels and title for the current figure
    ax.set_xlabel('Parameter 1')
    ax.set_ylabel('Parameter 2')
    ax.set_zlabel('Parameter 3')
    ax.set_title(f'Epoch {iteration + 1}')

    # Set consistent axis limits for all figures
    ax.set_xlim(0, x_max)
    ax.set_ylim(0, y_max)
    ax.set_zlim(0, z_max)

    # Add a colorbar for the current figure
    fig.colorbar(scatter, ax=ax, shrink=0.8, label='Fitness')

    # Adjust the spacing within the figure
    #plt.tight_layout()

    # Save the figure as a separate file
    plt.show()

    # Close the figure to free up memory
    plt.close(fig)