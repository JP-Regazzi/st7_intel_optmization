import random
from launch import fitness
import argparse

def hill_climbing_3d(start_x, start_y, start_z, steps=1000, step_size=0.01):
    current_x, current_y, current_z = start_x, start_y, start_z
    current_fitness = fitness(current_x, current_y, current_z)
    
    for _ in range(steps):
        # Generate a list of neighboring points
        neighbors = []
        for dx in [-step_size, 0, step_size]:
            for dy in [-step_size, 0, step_size]:
                for dz in [-step_size, 0, step_size]:
                    if dx == 0 and dy == 0 and dz == 0:
                        continue  # Skip the current point itself
                    new_x, new_y, new_z = current_x + dx, current_y + dy, current_z + dz
                    neighbors.append((new_x, new_y, new_z))
        
        # Evaluate all neighbors and move to the best one
        best_neighbor = None
        best_fitness = current_fitness
        for x, y, z in neighbors:
            fitness = fitness(x, y, z)
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
    parser.add_argument("--stepsize", help="stepsize", default=0.1, type=int)
    args = parser.parse_args()
    seed = args.seed
    # Random starting point in (0, 100)
    random.seed(seed)
    start_x, start_y, start_z = random.uniform(0, 100), random.uniform(0, 100), random.uniform(0, 100)
    final_x, final_y, final_z, final_fitness = hill_climbing_3d(start_x, start_y, start_z)
    print(f"Final position: ({final_x}, {final_y}, {final_z}) with fitness {final_fitness}")

