#!/usr/bin/env bash
#
# Default number of steps
N_steps=1000

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -steps|--steps) N_steps="$2"; shift ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done
echo "Running with steps: $N_steps"

echo "Greedy Hill"
python simpleHill.py --timer 1 --seed 42 --steps $N_steps 
echo "*******************************************"
echo "Parallel Greedy Hill"
mpirun -n 2 python ./parallelGreedyHill.py --timer 1 --seed 42 --steps $N_steps 
