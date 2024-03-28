from skopt import gp_minimize
import numpy as np
from starter import run_process_parametrized_args, compile
from mpi4py import MPI

# Define the function to be optimized
def objective_function(x):
    # Example objective function (you can replace this with your own function)
    return np.sin(x[0]) + np.cos(x[1]) + np.sin(x[2])

# Define a function to enforce that the first dimension is a multiple of 16
def adjust_first_dimension(x):
    x[0] = int(np.round(x[0] / 16)) * 16
    return x

def generate_starting_points(num_starting_points):
    starting_points = []
    for i in range(1, num_starting_points+1):
        starting_point = []
        starting_point.append(random.randint(1, 4) * 16 * i)
        starting_point.append(random.randint(1, 16) * i)
        starting_point.append(random.randint(1, 16) * i)
        starting_points.append(starting_point)
    return starting_points


#starting_points = generate_starting_points(num_starting_points)
#chunk_size = len(starting_points) // size

#starting_points_chunk = starting_points[rank * chunk_size: (rank + 1) * chunk_size]



comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

res = (256-16)/4

# Define the search space
space = [(1, 16), (16 + 60*(rank), 16+60*(rank+1)), (16 + 60*(rank), 16+60*(rank+1))]  # 3D domain ranges from 0 to 10 in each dimension

# Perform Bayesian optimization
result = gp_minimize(run_process_parametrized_args, space,n_calls=100, random_state=42)


# Print the optimal point and corresponding function value
if rank == 0:
    print("Optimal point:", result.x)
    print("Optimal function value:", result.fun)



