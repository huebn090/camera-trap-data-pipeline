# Pre-Processing Camera-Trap Images

The following codes can be used to:

1. Check File Organization
2. Check for Duplicate Images
3. Create Image Inventory
4. Perform basic checks
5. Extract Exif data
6. Re-name all images
7. Group images into captures
8. Inspect potential issues to resolve/waive them
9. Obtain a cleaned inventory of the processed camera trap images

The following examples were run with the following settings:

```
srun -N 1 --mem=64gb -t 8:00:00 -p interactive --pty bash
module load python3
cd $HOME/camera-trap-data-pipeline
git pull
SITE=EFA
SEASON=EFA_S1B1
```

It is recommended to create the following directories:
```
season_captures/${SITE}/inventory
season_captures/${SITE}/captures
season_captures/${SITE}/cleaned
season_captures/${SITE}/log_files
```


## Check Input Structure

The camera trap images to be imported need to be organized according to the following directory structure:

```
root_directory/
  site_directory/
    roll_directory/
      image_files
```

Definitions:
- Site: A specific camera/location.
- Roll: An SD card of a specific site (data from a camera check).

The naming has to adhere to these standards:
- site_directory: alphanumeric
- roll_directory: site name + _ + 'RX' where 'X' is a numeric. Example: A01_R1 (first roll of A01).
- Images: arbitrary names

```
root_directory/
  A01/
    A01_R1/
      *.JPG
```   

The check can be performed using the following script:
```
python3 -m pre_processing.check_input_structure \
--root_dir /home/packerc/shared/albums/${SITE}/${SEASON}/ \
--log_dir /home/packerc/shared/season_captures/${SITE}/log_files/ \
--log_filename ${SEASON}_check_input_structure
```

The script will print/log messages if something is invalid but not alter anything.

## Check for Duplicate Images

The following script will check for duplicate images.

```
python3 -m pre_processing.check_for_duplicates \
--root_dir /home/packerc/shared/albums/${SITE}/${SEASON}/ \
--log_dir /home/packerc/shared/season_captures/${SITE}/log_files/ \
--log_filename ${SEASON}_check_for_duplicates
```
The script will print/log duplicates if any are found but won't alter anything. Note that some corrupt files (such with 0 size) will also be recognized as duplicates.

## Create Basic Image Inventory

The following script generates an inventory of all camera trap images.

```
python3 -m pre_processing.create_image_inventory \
--root_dir /home/packerc/shared/albums/${SITE}/${SEASON}/ \
--output_csv /home/packerc/shared/season_captures/${SITE}/inventory/${SEASON}_inventory_basic.csv \
--log_dir /home/packerc/shared/season_captures/${SITE}/log_files/ \
--log_filename ${SEASON}_create_image_inventory
```

| Column   | Description |
| --------- | ----------- |
|season | season identifier
|site | site/camera identifier
|roll | roll identifier (SD card of a camera)
|image_name_original| name of original image file
|image_path_original_rel| relative path of image file
|image_path_original| full path of image file


## Create Image Inventory with Checks

The following script performs some checks on the images. It opens each image to verify its integrity and to perform pixel-based checks. The code is parallelized -- use the following options to make the most of the parallelization (it still takes roughly 1 hour per 60k images).

```
srun -N 1 --mem=64gb -t 4:00:00 -p interactive --pty bash (large batches)
module load python3
cd $HOME/camera-trap-data-pipeline
SITE=EFA
SEASON=EFA_IDI
```

Then run the code:
```
python3 -m pre_processing.basic_inventory_checks \
--inventory /home/packerc/shared/season_captures/${SITE}/inventory/${SEASON}_inventory_basic.csv \
--output_csv /home/packerc/shared/season_captures/${SITE}/inventory/${SEASON}_inventory.csv \
--log_dir /home/packerc/shared/season_captures/${SITE}/log_files/ \
--log_filename ${SEASON}_basic_inventory_checks \
--n_processes 12
```

To calculate correct file-creation dates the timezone can be specified. Default timezone is: 'Africa/Johannesburg'. This is mainly relevant if no EXIF data is available. In that case the file creation date will be used to determine image datetimes. To replace the timezone choose for example:
```
--timezone Africa/Dar_es_Salaam
```
See: https://stackoverflow.com/questions/13866926/is-there-a-list-of-pytz-timezones
Alternatively, change the default timezone in [config/cfg_default.yaml](../config/cfg_default.yaml).

For processing very large datasets (>200k images) it is recommended to run the following script via job queue via the code below. Update commands_basic_cleaning.sh with the appropriate 
site and season before running. If necessary, change the job time and requested resources in job_basic_cleaning.sh. 

```
ssh mangi
SITE=WLD
SEASON=WLD_S7
cd $HOME/camera-trap-data-pipeline

sbatch job_basic_cleaning_WLD_S6.sh

```

Check the status of the job by:
```
squeue -u username
```


| Column   | Description |
| --------- | ----------- |
|season | season identifier
|site | site/camera identifier
|roll | roll identifier (SD card of a camera)
|image_name_original| name of original image file
|image_path_original_rel| relative path of image file
|image_path_original| full path of image file
|datetime_file_creation| file creation date (default Y-m-d H:M:S)
|image_check__()| image check flag of check () -- '1' if check failed


## Extract EXIF data

The following script extracts EXIF data from all images. If this is your first time running this script, you will need to install several different packages in order to run it on MSI. 
ssh mesabi
module load python3
conda create -n python38 python=3.8
conda activate python38
source activate python38
conda install pandas matplotlib numpy pyyaml
conda install -c anaconda pytz
conda install -c jmcmurray json

# get python wrapper for exiftool
cd
git clone git://github.com/smarnach/pyexiftool.git
cd pyexiftool
python setup.py install

Before running (only the EXIF script):
conda activate python38

```
conda activate python388
python3 -m pre_processing.extract_exif_data \
--inventory /home/packerc/shared/season_captures/${SITE}/inventory/${SEASON}_inventory.csv \
--update_inventory \
--output_csv /home/packerc/shared/season_captures/${SITE}/inventory/${SEASON}_exif_data.csv \
--exiftool_path /home/packerc/shared/programs/Image-ExifTool-11.31/exiftool \
--log_dir /home/packerc/shared/season_captures/${SITE}/log_files/ \
--log_filename ${SEASON}_extract_exif_data
```

| Column   | Description |
| --------- | ----------- |
|season | season identifier
|site | site/camera identifier
|roll | roll identifier (SD card of a camera)
|image_name_original| name of original image file
|image_path_original_rel| relative path of image file
|image_path_original| full path of image file
|datetime_file_creation| file creation date (default Y-m-d H:M:S)
|image_check__()| image check flag of check () -- '1' if check failed
|datetime_exif| datetime as extrated from EXIF data (default Y-m-d H:M:S, '' if none)
|datetime| datetime_exif if available, else datetime_file_creation
|exif__()| EXIF tag () extracted from the image

For a large dataset, either request more memory resources in the interactive job or run the extract exif script as a batch. 

cd $HOME/camera-trap-data-pipeline/
SITE=WLD
SEASON=WLD_S5

INPUT_FILE=/home/packerc/shared/season_captures/${SITE}/inventory/${SEASON}_inventory.csv
OUTPUT_FILE/home/packerc/shared/season_captures/${SITE}/inventory/${SEASON}_exif_data.csv

conda activate python388
python3 -m pre_processing.extract_exif_data \
--inventory /home/packerc/shared/season_captures/${SITE}/inventory/${SEASON}_inventory.csv \
--update_inventory \
--output_csv /home/packerc/shared/season_captures/${SITE}/inventory/${SEASON}_exif_data.csv \
--exiftool_path /home/packerc/shared/programs/Image-ExifTool-11.31/exiftool \
--log_dir /home/packerc/shared/season_captures/${SITE}/log_files/ \
--log_filename ${SEASON}_extract_exif_data


## Group Images into Captures

The following script groups the images into capture events.

```
conda deactivate python388
python3 -m pre_processing.group_inventory_into_captures \
--inventory /home/packerc/shared/season_captures/${SITE}/inventory/${SEASON}_inventory.csv \
--output_csv /home/packerc/shared/season_captures/${SITE}/captures/${SEASON}_captures.csv \
--no_older_than_year 2015 \
--no_newer_than_year 2022 \
--log_dir /home/packerc/shared/season_captures/${SITE}/log_files/ \
--log_filename ${SEASON}_group_inventory_into_captures
```


| Column   | Description |
| --------- | ----------- |
|capture_id | identifier of the capture the image belongs to
|season | season identifier
|site | site/camera identifier
|roll | roll identifier (SD card of a camera)
|image_name_original| name of original image file
|image_path_original_rel| relative path of image file
|image_path_original| full path of image file
|datetime_file_creation| file creation date (default Y-m-d H:M:S)
|image_check__()| image check flag of check () -- '1' if check failed
|datetime_exif| datetime as extrated from EXIF data (default Y-m-d H:M:S, '' if none)
|exif__()| EXIF tag () extracted from the image
|capture | capture number (e.g. '1' for the first capture in a specific roll)
|image_rank_in_capture| (temporal) rank of image in a capture
|image_rank_in_roll| (temporal) rank of image in a roll
|image_name | image name after re-naming
|image_path_rel| relative (to season root) image path after re-naming
|image_path | full path of re-named image  
|seconds_to_next_image_taken| seconds to the next image taken
|seconds_to_last_image_taken| seconds to the last/previous image taken
|days_to_last_image_taken| days to the last/previous image taken
|days_to_next_image_taken| days to the next image taken



## Rename all images

The following script renames the images.

```
python3 -m pre_processing.rename_images \
--inventory /home/packerc/shared/season_captures/${SITE}/captures/${SEASON}_captures.csv \
--log_dir /home/packerc/shared/season_captures/${SITE}/log_files/ \
--log_filename ${SEASON}_rename_images
```

## Generate Action List

The following script generates an action list that recommends actions and allows for adding more actions.

```
python3 -m pre_processing.create_action_list \
--captures /home/packerc/shared/season_captures/${SITE}/captures/${SEASON}_captures.csv \
--action_list_csv /home/packerc/shared/season_captures/${SITE}/captures/${SEASON}_action_list.csv \
--log_dir /home/packerc/shared/season_captures/${SITE}/log_files/ \
--log_filename ${SEASON}_create_action_list \
--plot_timelines
```

The option '--plot_timelines' creates a pdf in the '--action_list_csv' directory with timelines for each roll showing the number of photos per day. This can be used to identify potential issues.

### Define Actions

1. Download the file 'action_list.csv'
2. The file is pre-populated with suggested actions that are being applied to the 'action_from_image'.
3. The following 'action_to_take' values are allowed:

action_to_take | meaning
------------ | -------------
delete | the selected images will be deleted (example: corrupt files)
invalidate | remove the image from further processing (but do not delete) -- this is for images that can't be used for ecological analyses (example: images that have bad quality / images with humans / excess images) -- per default such images are not uploaded to Zoniverse and not included in reports
timechange | the time of the selected images will be changed (see below)
ok | do nothing
mark_no_upload | flag/mark images as not to upload (example: images with sensitive species not intended for publication) -- per default such images are included in reports
mark_datetime_uncertain | flag/mark images if datetime is uncertain (example: images with only vague datetime info) -- per default such images are not included in reports but are uploaded to Zooniverse

4. To add new actions simply create a new row in the csv. Multiple actions can be specified for a single image if necessary (with the excpetion of timechanges).

WARNING: be careful in using the correct datetime format for the columns 'datetime_current' and 'datetime_new' (YYYY-MM-DD HH:MM:SS) when specifying timechanges. Opening the file in Excel may change this format.

# If you need to open a CSV file in Excel without changing the date-time stamps, here's how to do it:

Open a new Excel sheet, select the Data tab, then click 'From Text' in the Get External Data group.
Browse to the CSV file and select 'Import'.
In step 1 of the Import Wizard choose 'Delimited' as the original data type. Click 'Next'.
In step 2 of the Import Wizard choose Comma as the delimiter (deselect the Tab check box) and click 'Next'.
In step 3 of the Import Wizard, you tell Excel not to change your formats. With the first column in the Data Preview selected, scroll across to the last column and select it while holding the SHIFT key (all columns should now be selected).  Then select 'Text' as the Column Data Format and click 'Finish'. 
Click OK to insert the data into cell A1.

Do NOT use find and replace or the date-time stamp will be incorrect--type all corrections. #

5. The following options allow for selecting images for actions:

column(s) to specify | meaning
------------ | -------------
action_site | perform an action on an entire site
action_site / action_roll | perform an action on an entire roll
action_from_image / action_to_image | perform an action on a range of images (or one if identical)

Examples:

action_site	| action_roll | action_from_image |	action_to_image	| action_to_take |action_to_take_reason | datetime_current |	datetime_new
:---|:---|:--- | :---| :---| :---|:---|:---
 A01| | |		|delete	|camera_produced_unrecognizable_images	||
 A01| 2| |		|timechange	|camera clock off by minus one day	| 2000-01-01 00:00:00| 2000-01-02 00:00:00		
 | | |ENO_S1__B02_R1_IMAG1012.JPG	| ENO_S1__B02_R1_IMAG1012.JPG	|invalidate	|all_white		||
 | | |ENO_S1__B02_R1_IMAG0054.JPG	| ENO_S1__B02_R1_IMAG0054.JPG	|invalidate	|all_black||
 | | |ENO_S1__B02_R1_IMAG0990.JPG	|ENO_S1__B02_R1_IMAG0999.JPG	|delete	|human	||
 | | |ENO_S1__B03_R1_IMAG0100.JPG	|ENO_S1__B03_R1_IMAG0103.JPG	|mark_no_upload	|rhino	||

6. For each row specify: 'action_to_take' and 'action_to_take_reason'
7. For 'timechange' in 'action_to_take' specify 'datetime_current' and 'datetime_new'. This will apply the difference (!) between these two dates to all selected images. For example: 'datetime_current'='2000-01-01 00:00:00' and 'datetime_new'=2000-01-01 00:05:00 will shift the time by +5 minutes.

8. All rows with 'action_to_take' equal 'inspect' must be resolved and replaced with values as specified above.
9. Upload the modified csv and proceed.

### Experimental: Find specific (sensitive) images

Sometimes certain images (e.g. sensitive rhino images) need to be excluded from publication, however, need to be processed along with all the other images. In a scenario where we have identified such images (before the pre-processing) we would copy these to a separate directory but leave the originals in place to process them. We can now find these images again by using the following script to mark them via action_list as 'mark_no_upload'. The script finds any images stored in a directory (with any number of images and sub-directories) and searches for their twins as referenced in the 'captures.csv' file. Note that the following script has not been tested thoroughly and is not yet part of the standard process -- there is currently no standard 'images_to_match_path'.

```
python3 -m pre_processing.find_images_in_captures \
--captures /home/packerc/shared/season_captures/${SITE}/captures/${SEASON}_captures.csv \
--images_to_match_path /home/packerc/shared/... \
--output_csv /home/packerc/shared/season_captures/${SITE}/captures/${SEASON}_sensitive_images.csv
```


## Parse Action Items

This code unpacks the defined actions, performs some checks and generates a list with action items. One row per action / image.

```
python3 -m pre_processing.generate_actions \
--captures /home/packerc/shared/season_captures/${SITE}/captures/${SEASON}_captures.csv \
--action_list /home/packerc/shared/season_captures/${SITE}/captures/${SEASON}_action_list.csv \
--actions_to_perform_csv /home/packerc/shared/season_captures/${SITE}/captures/${SEASON}_actions_to_perform.csv \
--log_dir /home/packerc/shared/season_captures/${SITE}/log_files/ \
--log_filename ${SEASON}_generate_actions
```
This file can be checked to ensure if everything is correct.

| Column   | Description |
| --------- | ----------- |
|image | image name
|action| action to take
|reason| reason for the action to take
|shift_time_by_seconds| number of seconds to shift time by


## Apply Actions

This code applies the actions. It updates the captures file and deletes specific images if requested.

```
python3 -m pre_processing.apply_actions \
--captures /home/packerc/shared/season_captures/${SITE}/captures/${SEASON}_captures.csv \
--actions_to_perform /home/packerc/shared/season_captures/${SITE}/captures/${SEASON}_actions_to_perform.csv \
--log_dir /home/packerc/shared/season_captures/${SITE}/log_files/ \
--log_filename ${SEASON}_apply_actions
```


| Column   | Description |
| --------- | ----------- |
| .... | previous columns in captures file
|action_taken| the action that was applied to the image, separated by '#' if multiple
|action_taken_reason| the reason for the action that was applied to the image, separated by '#' if multiple
|image_is_invalid| flag if image was invalidated (1, '' otherwise)
|image_was_deleted| flag if image was deleted (1, '' otherwise)
|image_no_upload| flag if image was marked for no upload (1, '' otherwise)
|image_datetime_uncertain| flag if image was marked for uncertain datetime (1, '' otherwise)


## Generate Updated Captures

This code generates an updated captures file after applying actions. This is mainly to remove deleted images and to re-group images into captures if timechanges were specified.

```
python3 -m pre_processing.update_captures \
--captures /home/packerc/shared/season_captures/${SITE}/captures/${SEASON}_captures.csv \
--captures_updated /home/packerc/shared/season_captures/${SITE}/captures/${SEASON}_captures_updated.csv \
--log_dir /home/packerc/shared/season_captures/${SITE}/log_files/ \
--log_filename ${SEASON}_update_captures
```


## Finalize (create cleaned captures) or Iterate (go back to creating action list)

To check whether there are further issues run the following code. The code creates a new action list. If the list is empty, there are no further actions to take an we can proceed to the next step and create the cleaned csv. If there are further issues, we go back to the 'Generate Action List' section and proceed from there.
```
python3 -m pre_processing.create_action_list \
--captures /home/packerc/shared/season_captures/${SITE}/captures/${SEASON}_captures_updated.csv \
--action_list_csv /home/packerc/shared/season_captures/${SITE}/captures/${SEASON}_action_list2.csv \
--log_dir /home/packerc/shared/season_captures/${SITE}/log_files/ \
--log_filename ${SEASON}_create_action_list
```

If the previous code showed no further issues a final cleaned captures file is created:
```
python3 -m pre_processing.create_captures_cleaned \
--captures /home/packerc/shared/season_captures/${SITE}/captures/${SEASON}_captures_updated.csv \
--captures_cleaned /home/packerc/shared/season_captures/${SITE}/cleaned/${SEASON}_cleaned.csv \
--log_dir /home/packerc/shared/season_captures/${SITE}/log_files/ \
--log_filename ${SEASON}_create_captures_cleaned
```



## Columns of Cleaned Captures (Default)


| Column   | Description |
| --------- | ----------- |
|capture_id | identifier of the capture the image belongs to
|season | season identifier
|site | site/camera identifier
|roll | roll identifier (SD card of a camera)
|capture | capture number (e.g. '1' for the first capture in a specific roll)
|image_rank_in_capture| (temporal) rank of image in a capture
|image_name | image name after re-naming
|image_path_rel| relative (from season root) image path after re-naming
|datetime| datetime of image (default Y-m-d H:M:S) -- after any datetime corrections applied
|datetime_exif| datetime as extrated from EXIF data (default Y-m-d H:M:S, '' if none)
|datetime_file_creation| file creation date (default Y-m-d H:M:S)
|image_is_invalid| flag if image was invalidated (1, '' otherwise)
|image_was_deleted| flag if image was deleted (1, '' otherwise)
|image_no_upload| flag if image was marked for no upload (1, '' otherwise)
|image_datetime_uncertain| flag if image was marked for uncertain datetime (1, '' otherwise)
|action_taken| the action that was applied to the image, separated by '#' if multiple
|action_taken_reason| the reason for the action that was applied to the image, separated by '#' if multiple


## Additional / Altered Columns of Legacy Cleaned Captures Files

There are several seasons that were processed using older scripts. To standardize the files as much as possible the columns are identical, however, some are always empty. A few columns are extra, to preserve historical information. The following columns may be different/affected:

| Columns   | Description |
| --------- | ----------- |
|datetime| datetime of image (default Y-m-d H:M:S) -- often this is derived from the file creation date instead of the EXIF data
|datetime_exif| datetime as extrated from EXIF data, not always available, sometimes unclear if origin is in fact from the EXIF data
|datetime_file_creation| file creation date  (default Y-m-d H:M:S, '' if not available)
|image_is_invalid| flag if image was invalidated (1, '' otherwise) -- derived from 'invalid' column (values 1,2,3)
|image_datetime_uncertain| flag if image was marked for uncertain datetime (1, '' otherwise) -- derived from 'invalid' column (values 1,2,3)
|invalid| legacy column referring to timestamp status ('0' = no issue, '1' = 'Not recoverable', '2'= 'Fix is hard', '3'='Fix is hard but timestamp likely close')
|include| flag if image has flag 'invalid' equal '0'
|image_was_deleted| dummy flag for consistency with newer data -- is always ''
|image_no_upload| dummy flag for consistency with newer data -- is always ''
|action_taken| dummy col for consistency with newer data -- is always ''
|action_taken_reason| dummy col for consistency with newer data -- is always ''
