#!/bin/bash

export SITE=SER
export SEASON=SER_S15F
echo "This is where you are in the file system ${pwd}, we need to move to the directory that the python script requires"
PYTHONPATH="${PYTHONPATH}:/panfs/roc/groups/5/packerc/huebn090/camera-trap-data-pipeline"
export PYTHONPATH
cd "/panfs/roc/groups/5/packerc/huebn090/camera-trap-data-pipeline"
echo "Current dir:"
pwd
echo "If you want to install a specific package, you can do it in this file (i.e. python -m pip install <package> --user). Or, you can run (module load singularity), then (singularity run -H $(pwd) camera-trap-classifier-latest-cpu.simg), then (i.e. python -m pip install <package> --user)"
# python -m pip install pillow --user
echo "Running script..."
echo "trying faulty import"
python -c "from r.r.r import r"
echo "now trying actual import"
python -c "from utils.utils import set_file_permission" && echo "import successful"
echo "now trying to run main script"
python -m pre_processing.basic_inventory_checks \
--inventory /home/packerc/shared/season_captures/${SITE}/inventory/${SEASON}_inventory_basic.csv \
--output_csv /home/packerc/shared/season_captures/${SITE}/inventory/${SEASON}_inventory.csv \
--log_dir /home/packerc/shared/season_captures/${SITE}/log_files/ \
--log_filename ${SEASON}_basic_inventory_checks \
--n_processes 32
