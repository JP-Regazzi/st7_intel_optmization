import random
from launch import getFitness
import argparse

def hill_climbing_3d(start_x, start_y, start_z, steps=1000, step_size=0.01, verbose=0):
    current_x, current_y, current_z = start_x, start_y, start_z
    current_fitness = getFitness((current_x, current_y, current_z), verbose=verbose)
    
    for _ in range(steps):
        # Generate a list of neighboring points
        neighbors = []
        for dx in [-step_size, 0, step_size]:
            for dy in [-step_size, 0, step_size]:
                for dz in [-step_size, 0, step_size]:
                    if dx == 0 and dy == 0 and dz == 0:
                        continue  # Skip the current point itself
                    new_x, new_y, new_z = current_x, current_y + dy, current_z + dz # x stays constant
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
        else:
            # No better neighbors, so we've reached a peak
            break
    
    return current_x, current_y, current_z, current_fitness

if __name__ == "__main__":
    # Get seed by --seed argument
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", help="seed", default=42, type=int)
    parser.add_argument("--steps", help="steps", default=100, type=int)
    parser.add_argument("--stepsize", help="stepsize", default=1, type=int)
    parser.add_argument("--verbose", help="verbose", default=0, type=int)
    args = parser.parse_args()
    seed = args.seed
    verbose = args.verbose
    steps = args.steps
    stepsize = args.stepsize
    # Random starting point in (0, 100)
    random.seed(seed)
    start_x, start_y, start_z = 32, random.randrange(1, 128), random.randrange(1, 128)
    final_x, final_y, final_z, final_fitness = hill_climbing_3d(start_x, start_y, start_z, verbose)
    print(f"Final position: ({final_x}, {final_y}, {final_z}) with fitness {final_fitness}")

