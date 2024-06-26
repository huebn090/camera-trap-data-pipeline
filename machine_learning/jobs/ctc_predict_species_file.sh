#!/bin/bash
#SBATCH -A packerc
#SBATCH --time=96:00:00
#SBATCH --mail-type=ALL
#SBATCH --ntasks=32
#SBATCH --mem=64GB
#SBATCH --job-name=predict_species
#SBATCH --mail-user=huebn090@umn.edu
#SBATCH -p amdsmall 

# Parameters Static
TO_PREDICT_PATH=${INPUT_FILE}
OUTPUT_PATH=${OUTPUT_FILE}

MODEL_ROOT_PATH=/home/packerc/shared/machine_learning/data/models/PANTHERA_SNAPSHOT_SAFARI/species/
MODEL_NAME=Xception_v1
MODEL_PATH=${MODEL_ROOT_PATH}${MODEL_NAME}/best_model.hdf5
MODEL_CLASS_MAPPING=${MODEL_ROOT_PATH}${MODEL_NAME}/label_mappings.json
MODEL_PRE_PROCESSING=${MODEL_ROOT_PATH}${MODEL_NAME}/image_processing.json

# Container
SINGULARITY_PATH=/home/packerc/shared/programs/camera-trap-classifier

# Log Parameters
echo "TO_PREDICT_PATH: $TO_PREDICT_PATH"
echo "IMAGES_ROOT: $IMAGES_ROOT"
echo "OUTPUT_PATH: $OUTPUT_PATH"

echo "MODEL_ROOT_PATH: $MODEL_ROOT_PATH"
echo "MODEL_NAME: $MODEL_NAME"
echo "MODEL_PATH: $MODEL_PATH"
echo "MODEL_CLASS_MAPPING: $MODEL_CLASS_MAPPING"
echo "MODEL_PRE_PROCESSING: $MODEL_PRE_PROCESSING"

echo "SINGULARITY_PATH: $SINGULARITY_PATH"


# modules
module load singularity
module load python3


# sleep for 2 minutes to reduce chance of conflict with 'empty' script when it
# is pulling the following docker container
#sleep 2m


# switch to singularity container path
cd $SINGULARITY_PATH
#singularity pull -F docker://will5448/camera-trap-classifier:latest-cpu

# run the script
singularity exec -B /home/packerc/shared:/home/packerc/shared ./camera-trap-classifier-latest-cpu.simg \
  ctc.predict \
    -csv_path $TO_PREDICT_PATH \
    -csv_id_col capture_id \
    -csv_images_cols image1 image2 image3 \
    -csv_images_root_path $IMAGES_ROOT \
    -export_file_type json \
    -results_file $OUTPUT_PATH \
    -model_path $MODEL_PATH \
    -class_mapping_json $MODEL_CLASS_MAPPING \
    -pre_processing_json $MODEL_PRE_PROCESSING \
    -aggregation_mode mean

chmod g+rw $OUTPUT_PATH
