#!/bin/bash
#SBATCH --time=4

# The line SBATCH --time=4 means: max exec time of the batch is 4 minutes
# When developping and debuging: use small test and small time limits
# After you can sublit Batch with 15, 30, 60, 120 minutes

source /etc/profile

module load py-mpi4py/3.1.4/gcc-12.3.0-openmpi
#module load ... others modules to load

# go in the right directory (where is the pgm to execute)
cd ~/tmp


echo "============= TITLE OF MY BATCH ================="

# Command to execute
# ex : 8 processes distributed on 2 nodes: 2 per socket (i.e. 4 per node)

/usr/bin/mpirun -np 8 -map-by ppr:2:socket:PE=4 -rank-by core python3 ./parallelGreedyHill.py --timer 1 --seed 42 --steps 1000

# ex to test 4 processes on one node (no communications)
#/usr/bin/mpirun -np 4 -map-by ppr:1:core:PE=1 -rank-by core python3 myappli.py args_of_my_appli


echo "===================== END ======================="