#!/bin/bash
#SBATCH -t 24:00:00
#SBATCH -n 4
#SBATCH -p small
#SBATCH --mem=60GB
#SBATCH --mail-type=ALL
#SBATCH --mail-user=huebn090@umn.edu
#SBATCH --job-name=basic_inventory_check
#SBATCH -o basic_inventory_check_LEC_S1.log
#SBATCH -e basic_inventory_check_LEC_S1.log

module load python3

cd $HOME/camera-trap-data-pipeline


python3 -m pre_processing.basic_inventory_checks \
--inventory /home/packerc/shared/season_captures/${SITE}/inventory/${SEASON}_inventory_basic.csv \
--output_csv /home/packerc/shared/season_captures/${SITE}/inventory/${SEASON}_inventory.csv \
--n_processes 32 \
--log_dir /home/packerc/shared/season_captures/${SITE}/log_files/ \
--log_filename ${SEASON}_basic_inventory_checks
