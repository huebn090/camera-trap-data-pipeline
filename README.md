# snapshot_safari_misc
Misc Code for Snapshot Safari.
1. Prepare Data for Upload to Zooniverse
2. Machine Learning Codes
3. Download and Aggregate Data from Zooniverse


## Pre-Requisites

For code that accesses Zooniverse via Panoptes (e.g. requires a password),
a file with Zooniverse credentials should be stored (e.g. in ~/keys/passwords.ini). It should have the following content:

```
[zooniverse]
username: my_username
password: my_password
```

Set permissions of that file by using this command:
```
chmod 600 ~/keys/passwords.ini
```

Before executing (most of) the code, you need to execute the follwing:
```
ssh lab
module load python3
cd /home/packerc/shared/scripts/snapshot_safari_misc
git pull
chmod -R g+rwx /home/packerc/shared/scripts/snapshot_safari_misc
```

If there are any problems with updating the code (git pull) just delete and clone it again:
```
rm -r -f /home/packerc/shared/scripts/snapshot_safari_misc
cd /home/packerc/shared/scripts/
git clone https://github.com/marco-willi/snapshot_safari_misc.git
chmod -R g+rwx /home/packerc/shared/scripts/snapshot_safari_misc
```

The easiest way to exectue the following codes is to copy & paste them to a text editor, change the parameters (e.g. paths) and then copy & paste that to the command line to execute them.

## Get and Extract Zooniverse Exports

Some of the scripts used for different sites can be found here: [zooniverse_exports/scripts.sh](zooniverse_exports/scripts.sh)

### Get Zooniverse Exports

Download Zooniverse exports. Requires Zooniverse account credentials and
collaborator status with the project. The project_id can be found in the project builder
in the top left corner. To create a 'fresh' export it is easiest to go on Zooniverse, to the project page,
click on 'Data Exports', and click on new 'Request new classification export'.

```
python3 -m zooniverse_exports.get_zooniverse_export \
        -password_file ~/keys/passwords.ini \
        -project_id 5155 \
        -output_file /home/packerc/shared/zooniverse/Exports/RUA/RUA_S1_classifications.csv \
        -export_type classifications \
        -new_export 0
```


### Extract Zooniverse Classifications

This extracts the relevant fields of a Zooniverse classification file
and creates a csv with one line per annotation. All classifications have to
be from the same workflow with the same workflow version. The workflow_id
can be found in the project builder when clicking on the workflow. The workflow_version
is at the same place slightly further down (e.g. something like 745.34 - use only 745).

```
python3 -m zooniverse_exports.extract_classifications \
        -classification_csv /home/packerc/shared/zooniverse/Exports/RUA/RUA_S1_classifications.csv \
        -output_csv /home/packerc/shared/zooniverse/Exports/RUA/RUA_S1_classifications_extracted.csv \
        -workflow_id 4889 \
        -workflow_version 797
```


### Aggregate Extracted Zooniverse Classifications

This aggregates the extracted Zooniverse classifications using the
plurality algorithm to get one single label per species detection for each
subject.

```
python3 -m zooniverse_exports.aggregate_extractions \
        -classifications_extracted /home/packerc/shared/zooniverse/Exports/RUA/RUA_S1_classifications_extracted.csv \
        -output_csv /home/packerc/shared/zooniverse/Exports/RUA/RUA_S1_classifications_aggregated.csv
```

### Add Meta-Data to Aggregated Classifications (work in progress..)

This function adds meta-data to aggregated classifications, like location, timestamp, and
other data currently used for input to machine learning models. This function is unfinished
and currently only works with the 'old' manifest formats.

```
python3 -m zooniverse_exports.add_meta_data_to_aggregated_class \
-classifications_aggregated /home/packerc/shared/zooniverse/Exports/GRU/GRU_S1_classifications_aggregated.csv \
-season_cleaned /home/packerc/shared/season_captures/GRU/cleaned/GRU_S1_cleaned.csv \
-output_csv /home/packerc/shared/zooniverse/Exports/GRU/GRU_S1_export.csv \
-season GRU_S1 \
-site GRU \
-manifest_files_old /home/packerc/shared/zooniverse/Manifests/GRU/GRU_S1_manifest_v1 \
-max_n_images 3
```

## Upload new Data to Zooniverse

The following steps are required to upload new data to Zooniverse including machine learning scores. The following codes show an example for processing RUA data.

### Compress Images

The code 'compress_images.pbs' compresses images and has to be ADAPTED in the following way (NOT EXECUTED):

```
module load python3

cd /home/packerc/shared/scripts/snapshot_safari_misc

python3 -m image_compression.compress_images \
-cleaned_captures_csv /home/packerc/shared/season_captures/RUA/cleaned/RUA_S1_cleaned.csv \
-output_image_dir  /home/packerc/shared/zooniverse/ToUpload/RUA_will5448/RUA_S1_Compressed \
-root_image_path /home/packerc/shared/albums/RUA/
```

After that we create the folders and submit the job:
```
mkdir /home/packerc/shared/zooniverse/ToUpload/RUA_will5448/RUA_S1_Compressed
cd /home/packerc/shared/scripts/snapshot_safari_misc/image_compression
qsub compress_images.pbs
```

This job can run for a long time, i.e. many hours.

### Generate Manifest

This generates a manifest from the cleaned season captures csv.

```
python3 -m zooniverse_uploads.generate_manifest \
-cleaned_captures_csv /home/packerc/shared/season_captures/RUA/cleaned/RUA_S1_cleaned.csv \
-compressed_image_dir /home/packerc/shared/zooniverse/ToUpload/RUA/RUA_S1_Compressed/ \
-output_manifest_dir /home/packerc/shared/zooniverse/Manifests/RUA/ \
-manifest_prefix RUA_S1 \
-attribution 'University of Minnesota Lion Center + SnapshotSafari + Ruaha Carnivore Project + Tanzania + Ruaha National Park' \
-license 'SnapshotSafari + Ruaha Carnivore Project'
```


### OPTIONAL (hack) - Remove specific capture events from the manifest

This code is only required if data has already been uploaded using the old process in order to remove already uploaded capture events.

```
python3 -m zooniverse_uploads.remove_records_from_manifest \
-manifest /home/packerc/shared/zooniverse/Manifests/RUA/RUA_S1_manifest.json \
-old_manifest_to_remove /home/packerc/shared/zooniverse/Manifests/RUA/RUA_S1_A1_manifest_v1 \
-season RUA_S1
```

### Create Prediction Info File for Machine Lerning Model

This code creates a 'prediction file' that is the input to the model for classifying the images.

```
python3 -m zooniverse_uploads.create_predict_file_from_manifest \
-manifest /home/packerc/shared/zooniverse/Manifests/RUA/RUA_S1_manifest.json \
-prediction_file /home/packerc/shared/machine_learning/data/info_files/RUA/RUA_S1/RUA_S1_manifest.csv
```

### Generate new Predictions

The following steps describe how to run the machine learning models. Note that the files 'predict_species.pbs' and 'predict_empty.pbs' have to be adapted.

```
cd /home/packerc/shared/scripts/snapshot_safari_misc/machine_learning
# ADAPT predict_species.pbs
# ADAPT predict_empty.pbs

ssh mesabi
qsub predict_species.pbs
qsub predict_empty.pbs
```

### Aggregte Predictions

This code aggregates the individual image classifications on capture event level.

```
python3 -m zooniverse_uploads.import_and_aggregate_predictions \
-manifest /home/packerc/shared/zooniverse/Manifests/RUA/RUA_S1_manifest.json \
-empty_predictions /home/packerc/shared/machine_learning/data/predictions/empty_or_not/RUA/RUA_S1/predictions_run_manifest_20180628.json \
-species_predictions /home/packerc/shared/machine_learning/data/predictions/species/RUA/RUA_S1/predictions_run_manifest_20180628.json \
-output_file /home/packerc/shared/zooniverse/Manifests/RUA/RUA_S1_preds_aggregated.json
```

### Merge Predictions into Manifest

This code merges the aggregated predictions into the manifest.

```
python3 -m zooniverse_uploads.merge_predictions_with_manifest \
-manifest /home/packerc/shared/zooniverse/Manifests/RUA/RUA_S1_manifest.json \
-predictions /home/packerc/shared/zooniverse/Manifests/RUA/RUA_S1_preds_aggregated.json \
-output_file /home/packerc/shared/zooniverse/Manifests/RUA/RUA_S1_manifest1.json
```

### Upload Manifest

This code uploads the manifest to Zooniverse. Note that the Zooniverse credentials have to be available in '~/keys/passwords.ini' and that it is better to use the .qsub version of this code due to the long potential run-time.
```
cd /home/packerc/shared/machine_learning/will5448/code/snapshot_safari_misc
python3 -m zooniverse_uploads.upload_manifest \
-manifest /home/packerc/shared/zooniverse/Manifests/RUA/RUA_S1_manifest1.json \
-output_file /home/packerc/shared/zooniverse/Manifests/RUA/RUA_S1_manifest2.json \
-project_id 5155 \
-subject_set_name RUA_S1_machine_learning_v1 \
-password_file ~/keys/passwords.ini
```

This code can run for a long time, i.e. multiple days.
