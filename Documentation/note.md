ssh -l st76i_4 chome.metz.supelec.fr

srun -N 1 --exclusive --reservation=ST76I5 --pty bash

On Kyle or chome enter the command (in the directory where is the Batch Script): 

`sbatch -N 2 -n 64 -p cpu_prod --qos=8nodespu BatchScript2nodes`

 -n : 32xN
 -p cpu_prod : use the partition "for production jobs"
 --qos=8nodespu : max 8 nodes for one batch


dans batch2Node.sh changer le 4 en haut (minutes)

`squeue` pour voir l'etat des batch lancés
`cat slurm-XXX` pour voir l'output de mon code
`scancel <job-id>`

# TODO :
Visualisation heatmap for grid search and parallel hill

srun –N 1 --exclusive –p cpu_tp --pty bash


Métrique importante : nombre de calls à la fonction de coût
Cache heat
Reference for the theoretical nb of cache
Integrate compiler parameters
isValid(params) function to check the parameters are not out of bounds

29/03
final defense
online demonstration (with only one program)
take time to finalize, have nice slides, final PDF report, 30 pages
do we use the hardware to its full advantage ?
https://arxiv.org/pdf/1902.00448.pdf
https://en.wikipedia.org/wiki/CMA-ES
https://arxiv.org/pdf/2210.10199.pdf
https://arxiv.org/pdf/1604.00772.pdf

 20/03
 REPORT
 Prepare results ready to be shown (slurm.out)
 Make graphs
 Add the name of the method in the prints
Add default args to the CLI