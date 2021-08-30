#!/bin/bash
#SBATCH -A packerc
#SBATCH --time=96:00:00
#SBATCH --mail-type=ALL
#SBATCH --ntasks=32
#SBATCH --mem=64GB
#SBATCH --job-name=jobs
#SBATCH --mail-user=huebn090@umn.edu
#SBATCH -p amdsmall                                            

export commands_file_path=/panfs/roc/groups/5/packerc/huebn090/camera-trap-data-pipeline/commands_basic_cleaning.sh
export HOME_DIR=/panfs/roc/groups/5/packerc/
pwd
module load singularity
singularity exec -H $HOME_DIR -i /panfs/roc/groups/5/packerc/huebn090/camera-trap-classifier-latest-cpu.simg pwd && echo "The two lines above must match" && echo "Things between the && are conditional commands (i.e. only execute if prior commands are successful)" && $commands_file_path
