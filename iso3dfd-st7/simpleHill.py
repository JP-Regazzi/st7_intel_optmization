import random
from launch import getFitness
import argparse
import time

LOCAL_DEBUG = False

def getFitnessDebug(cache_blocking, verbose = 0):
    x, y, z = cache_blocking
    val = x**2 + y**2 + z**2
    if verbose > 0: print(f"Fitness: {val}")
    return val

def hill_climbing_3d(start_x, start_y, start_z, steps=1000, step_size=1, verbose=0):
    current_x, current_y, current_z = start_x*16, start_y, start_z
    current_fitness = getFitness((current_x, current_y, current_z), verbose=verbose)
    
    # Initialize arrays to store the explored values
    explored_values = [(current_y, current_z, current_fitness)]
    
    for _ in range(steps):
        # Generate a list of neighboring points
        neighbors = []
        for dx in [-step_size, 0, step_size]:
            for dy in [-step_size, 0, step_size]:
                for dz in [-step_size, 0, step_size]:
                    if dx == 0 and dy == 0 and dz == 0:
                        continue  # Skip the current point itself
                    new_x, new_y, new_z = current_x + 16*dx, current_y + dy, current_z + dz # x stays constant
                    neighbors.append((new_x, new_y, new_z))
        
        # Evaluate all neighbors and move to the best one
        best_neighbor = None
        best_fitness = current_fitness
        for x, y, z in neighbors:
            fitness = getFitness((x, y, z), verbose=verbose)
            if fitness > best_fitness:
                best_neighbor = (x, y, z)
                best_fitness = fitness
        
        # If there's a better neighbor, move to it
        if best_neighbor:
            current_x, current_y, current_z = best_neighbor
            current_fitness = best_fitness
            
            # Store the explored values
            explored_values.append((current_y, current_z, current_fitness))
        else:
            # No better neighbors, so we've reached a peak
            break
    
    return current_x, current_y, current_z, current_fitness, explored_values

if __name__ == "__main__":
    # Get seed by --seed argument
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", help="seed", default=42, type=int)
    parser.add_argument("--steps", help="steps", default=1, type=int)
    parser.add_argument("--stepsize", help="stepsize", default=1, type=int)
    parser.add_argument("--verbose", help="verbose", default=0, type=int)
    parser.add_argument("--timer", help="timer", default=False, type=bool)
    args = parser.parse_args()
    seed = args.seed
    verbose = args.verbose
    steps = args.steps
    stepsize = args.stepsize
    timer = args.timer
    if timer:
        start = time.time()
    random.seed(seed)
    if LOCAL_DEBUG:
        getFitness = getFitnessDebug
    start_x, start_y, start_z = random.randrange(1, 11), random.randrange(1, 128), random.randrange(1, 128)
    final_x, final_y, final_z, final_fitness, explored_values = hill_climbing_3d(start_x, start_y, start_z, steps, stepsize, verbose)
    print(f"Final position: ({final_x}, {final_y}, {final_z}) with fitness {final_fitness}")
    if timer:
        end = time.time()
        print(f"Time elapsed: {end-start}")
    
    # Save the explored values in a text file
    with open('explored_values.txt', 'w') as file:
        file.write("Y,Z,Fitness\n")
        for y, z, fitness in explored_values:
            file.write(f"{y},{z},{fitness}\n")