#!/bin/bash
#SBATCH -A packerc
#SBATCH --time=96:00:00
#SBATCH --mail-type=ALL
#SBATCH --ntasks=32
#SBATCH --mem=64GB
#SBATCH --job-name=upload_manifest
#SBATCH --mail-user=huebn090@umn.edu
#SBATCH -p amdsmall 

module load python3
cd $HOME/camera-trap-data-pipeline/

if [[ -z "${SUBJECT_SET_ID}" ]]; then
  python3 -m zooniverse_uploads.upload_manifest \
  --manifest /home/packerc/shared/zooniverse/Manifests/${SITE}/${SEASON}__${BATCH}__manifest.json \
  --project_id $PROJECT_ID \
  --log_dir /home/packerc/shared/zooniverse/Manifests/${SITE}/log_files/ \
  --log_filename ${SEASON}_upload_manifest \
  --password_file ~/keys/passwords.ini \
  --image_root_path /home/packerc/shared/albums/${SITE}/
else
  python3 -m zooniverse_uploads.upload_manifest \
  --manifest /home/packerc/shared/zooniverse/Manifests/${SITE}/${SEASON}__${BATCH}__manifest.json \
  --project_id $PROJECT_ID \
  --subject_set_id $SUBJECT_SET_ID \
  --log_dir /home/packerc/shared/zooniverse/Manifests/${SITE}/log_files/ \
  --log_filename ${SEASON}_upload_manifest \
  --password_file ~/keys/passwords.ini \
  --image_root_path /home/packerc/shared/albums/${SITE}/
fi
