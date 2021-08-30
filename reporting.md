# Reporting

The following codes can be used to:

1. Create reports from Zooniverse aggregations
2. Create reports from Machine Learning predictions
3. Create reports for publication on LILA

A report in this context refers to a file (a csv) that contains individual species identifications for the data that was processed throug the entire data pipeline. It does not refer to ecological analyses or analytical products -- it is the basis to create such analyses.

The following codes show an example for Grumeti:

For most scripts we use the following ressources (unless indicated otherwise):
```
srun -N 1 --ntasks-per-node=4  --mem-per-cpu=8gb -t 2:00:00 -p interactive --pty bash
module load python3
cd ~/camera-trap-data-pipeline
```

The following examples were run with the following parameters (non-legacy):
```
SITE=GRU
SEASON=GRU_S2
```

Make sure to create the following folders:
```
SpeciesReports/${SITE}
SpeciesReports/${SITE}/log_files
LilaReports/${SITE}
LilaReports/${SITE}/log_files
```

## Create Zooniverse Reports

The next scripts produce reports based on Zooniverse aggregations. The full report (without any modification as listed below) contains one or more records per capture event as defined in the 'cleaned.csv' -- multiple records if multiple species were identified.

### Options to modify the Reports
Different reports can be generated based on the following options:


To export only species / exclude blanks:
```
--exclude_blanks
```

To export only captures with at least one Zooniverse annotation (otherwise each capture in the inventory will have one row in the export -- it will be mostly empty):
```
--exclude_captures_without_data
```

To export only consensus identifications (plurality algorithm):
```
--exclude_non_consensus
```

To exclude captures of humans:
```
--exclude_humans
```

To exclude zooniverse columns (retired, created, retirement_reason):
```
--exclude_zooniverse_cols
```

To exclude zooniverse url columns:
```
--exclude_zooniverse_urls
```

To exclude additional plurality algorithm columns:
```
--exclude_additional_plurality_infos
```

To exclude any other additional columns (for example subject_id, and season):
```
--exclude_cols subject_id season
```

### Complete Report

This report contains everything: blanks, consensus, non-consensus, captures without data, and humans.

```
# Create Complete Report
python3 -m reporting.create_zooniverse_report \
--season_captures_csv /home/packerc/shared/season_captures/${SITE}/cleaned/${SEASON}_cleaned.csv \
--aggregated_csv /home/packerc/shared/zooniverse/Aggregations/${SITE}/${SEASON}_aggregated_plurality_date.csv \
--output_csv /home/packerc/shared/zooniverse/SpeciesReports/${SITE}/${SEASON}_report_complete.csv \
--default_season_id ${SEASON} \
--log_dir /home/packerc/shared/zooniverse/SpeciesReports/${SITE}/log_files/ \
--log_filename ${SEASON}_create_zooniverse_report
```

Create an overview file:
```
# Create statistics file
python3 -m reporting.create_report_stats \
--report_path /home/packerc/shared/zooniverse/SpeciesReports/${SITE}/${SEASON}_report_complete.csv \
--output_csv /home/packerc/shared/zooniverse/SpeciesReports/${SITE}/${SEASON}_report_complete_overview.csv \
--log_dir /home/packerc/shared/zooniverse/SpeciesReports/${SITE}/log_files/ \
--log_filename ${SEASON}_create_report_stats
```

Note: Sometimes there are empty fields '' shown in the overview file. This is usually from captures without any aggregations (b/c not upoaded to Zooniverse).

### Consensus Species Report

This report contains only consensus species identifications and a reduced number of columns.

```
# Create Consensus Report
python3 -m reporting.create_zooniverse_report \
--season_captures_csv /home/packerc/shared/season_captures/${SITE}/cleaned/${SEASON}_cleaned.csv \
--aggregated_csv /home/packerc/shared/zooniverse/Aggregations/${SITE}/${SEASON}_aggregated_plurality_survey.csv \
--output_csv /home/packerc/shared/zooniverse/SpeciesReports/${SITE}/${SEASON}_report_consensus.csv \
--log_dir /home/packerc/shared/zooniverse/SpeciesReports/${SITE}/log_files/ \
--log_filename ${SEASON}_create_zooniverse_report \
--default_season_id ${SEASON} \
--exclude_blanks \
--exclude_humans \
--exclude_non_consensus \
--exclude_captures_without_data \
--exclude_zooniverse_cols \
--exclude_additional_plurality_infos
```

```
# Create statistics file
python3 -m reporting.create_report_stats \
--report_path /home/packerc/shared/zooniverse/SpeciesReports/${SITE}/${SEASON}_report_consensus.csv \
--output_csv /home/packerc/shared/zooniverse/SpeciesReports/${SITE}/${SEASON}_report_consensus_overview.csv \
--log_dir /home/packerc/shared/zooniverse/SpeciesReports/${SITE}/log_files/ \
--log_filename ${SEASON}_create_report_stats


# Create Consensus Report for survey workflow only
#First, run export and aggregations using workflow and version

python3 -m reporting.create_zooniverse_report \
--season_captures_csv /home/packerc/shared/season_captures/${SITE}/cleaned/${SEASON}_cleaned.csv \
--aggregated_csv /home/packerc/shared/zooniverse/Aggregations/${SITE}/${SEASON}_aggregated_plurality_survey.csv \
--output_csv /home/packerc/shared/zooniverse/SpeciesReports/${SITE}/${SEASON}_report_consensus_survey.csv \
--log_dir /home/packerc/shared/zooniverse/SpeciesReports/${SITE}/log_files/ \
--log_filename ${SEASON}_create_zooniverse_report \
--default_season_id ${SEASON} \
--exclude_blanks \
--exclude_humans \
--exclude_non_consensus \
--exclude_captures_without_data \
--exclude_zooniverse_cols \
--exclude_additional_plurality_infos

# Create statistics file for survey consensus
python3 -m reporting.create_report_stats \
--report_path /home/packerc/shared/zooniverse/SpeciesReports/${SITE}/${SEASON}_report_consensus_survey.csv \
--output_csv /home/packerc/shared/zooniverse/SpeciesReports/${SITE}/${SEASON}_report_consensus_survey_overview.csv \
--log_dir /home/packerc/shared/zooniverse/SpeciesReports/${SITE}/log_files/ \
--log_filename ${SEASON}_create_report_stats
```

```
# Create a small sample report
python3 -m reporting.sample_report \
--report_csv /home/packerc/shared/zooniverse/SpeciesReports/${SITE}/${SEASON}_report_complete.csv \
--output_csv /home/packerc/shared/zooniverse/SpeciesReports/${SITE}/${SEASON}_consensus_samples.csv \
--sample_size 2000 \
--log_dir /home/packerc/shared/zooniverse/SpeciesReports/${SITE}/log_files/ \
--log_filename ${SEASON}_sample_report
```

```
#Samples for gold standard datasets
python3 -m reporting.sample_report \
--report_csv /home/packerc/shared/gold_standard/${SITE}/${SEASON}_consensus_mod.csv \
--output_csv /home/packerc/shared/gold_standard/${SITE}/${SEASON}_GoldStandard_samples.csv \
--sample_size 2000 \
--log_dir /home/packerc/shared/gold_standard/${SITE}/log_files/ \
--log_filename ${SEASON}_sample_report


# Create statistics file for sample report
python3 -m reporting.create_report_stats \
--report_path /home/packerc/shared/gold_standard/${SITE}/${SEASON}_GoldStandard_samples.csv \
--output_csv /home/packerc/shared/gold_standard/${SITE}/${SEASON}_GoldStandard_overview.csv \
--log_dir /home/packerc/shared/gold_standard/${SITE}/log_files/ \
--log_filename ${SEASON}_create_report_stats_GS

```

### Image Inventory (Optional)

Create an image inventory containing paths for all images of all captures in a report. For example:

```
python3 -m reporting.create_image_inventory \
--season_captures_csv /home/packerc/shared/season_captures/${SITE}/cleaned/${SEASON}_cleaned.csv \
--report_csv /home/packerc/shared/zooniverse/SpeciesReports/${SITE}/${SEASON}_report_consensus.csv \
--output_csv /home/packerc/shared/zooniverse/SpeciesReports/${SITE}/${SEASON}_report_consensus_image_inventory.csv \
--log_dir /home/packerc/shared/zooniverse/SpeciesReports/${SITE}/log_files/ \
--log_filename ${SEASON}_create_image_inventory
```

| Columns   | Description |
| --------- | ----------- |
|capture_id | internal identifier of the capture
|image_rank_in_capture| rank/order of the image in the capture
|image_path_rel| relative path of the image

If urls are available, it is possible to add them using the following code:

```
python3 -m reporting.create_image_inventory \
--season_captures_csv /home/packerc/shared/season_captures/${SITE}/cleaned/${SEASON}_cleaned.csv \
--report_csv /home/packerc/shared/zooniverse/SpeciesReports/${SITE}/${SEASON}_report_consensus_survey.csv \
--output_csv /home/packerc/shared/zooniverse/SpeciesReports/${SITE}/${SEASON}_report_MSI.csv \
--add_url \
--url_prefix https://s3.msi.umn.edu/snapshotsafari/${SITE} \
--log_dir /home/packerc/shared/zooniverse/SpeciesReports/${SITE}/log_files/ \
--log_filename ${SEASON}_create_image_inventory
```

### Report Output Fields


| Columns   | Description |
| --------- | ----------- |
|capture_id | internal identifier of the capture
|season | season id of the capture
|site| site/camera id of the capture
|roll| roll number of the capture
|capture| capture number of the roll
|capture_date_local | local date (YYYY-MM-DD) of the capture
|capture_time_local | local time (HH:MM:SS) of the capture
|subject_id | Zooniverse subject_id (unique id of a capture)
|zooniverse_retirement_reason | Zooniverse retirement reason (empty if none/not retired)
|zooniverse_created_at | Zooniverse datetime of when the capture was uploaded
|zooniverse_retired_at | Zooniverse datetime of when the capture was retired (empty if not)
|zooniverse_url_*| Zooniverse image links of the capture (if uploaded else empty)
|question__* | Aggregated question answers, fractions, labels or counts (_max, _median, _min refer to the aggregation of the volunteer answers)
|n_users_identified_this_species | Number of users that identified 'question__species'
|p_users_identified_this_species | Proportion of users that identified 'question__species' among users who identified at least one species for this capture
|n_species_ids_per_user_median | Median number of different species identified among users who identified at least one species for this capture
|n_species_ids_per_user_max | Max number of different species identified among any users who identified at least one species for this capture
|n_users_saw_a_species| Number of users who saw/id'd at least one species.
|n_users_saw_no_species| Number of users who saw/id'd no species.
|p_users_saw_a_species| Proportion of users who saw/id'd a species.
|pielous_evenness_index| The Pielou Evenness Index or 0 for unanimous vote
|n_users_classified_this_subject | Number of users that classified this subject
|species_is_plurality_consensus | Flag (=1) indicating a plurality consensus for this species -- a value of 0 indicates a minority vote (meaning a different species is more likely but is reported to investigate uncertain cases)

## Machine Learning Reports

See here: [Machine Learning](../docs/machine_learning.md)


## LILA Reports

Reports for publication on http://lila.science/datasets

### Create LILA Report

```
python3 -m reporting.create_zooniverse_report \
--season_captures_csv /home/packerc/shared/season_captures/${SITE}/cleaned/${SEASON}_cleaned.csv \
--aggregated_csv /home/packerc/shared/zooniverse/Aggregations/${SITE}/${SEASON}_aggregated_plurality.csv \
--output_csv /home/packerc/shared/zooniverse/LilaReports/${SITE}/${SEASON}_report_lila.csv \
--log_dir /home/packerc/shared/zooniverse/LilaReports/${SITE}/log_files/ \
--log_filename ${SEASON}_create_zooniverse_report \
--default_season_id ${SEASON} \
--exclude_non_consensus \
--exclude_captures_without_data \
--exclude_zooniverse_cols \
--exclude_additional_plurality_infos \
--exclude_zooniverse_urls
```

Statistics:

```
python3 -m reporting.create_report_stats \
--report_path /home/packerc/shared/zooniverse/LilaReports/${SITE}/${SEASON}_report_lila.csv \
--output_csv /home/packerc/shared/zooniverse/LilaReports/${SITE}/${SEASON}_report_lila_overview.csv \
--log_dir /home/packerc/shared/zooniverse/LilaReports/${SITE}/log_files/ \
--log_filename ${SEASON}_create_report_stats
```

### Image Inventory

Create an image inventory containing paths from all images of all captures in the report:

```
python3 -m reporting.create_image_inventory \
--season_captures_csv /home/packerc/shared/season_captures/${SITE}/cleaned/${SEASON}_cleaned.csv \
--report_csv /home/packerc/shared/zooniverse/LilaReports/${SITE}/${SEASON}_report_lila.csv \
--output_csv /home/packerc/shared/zooniverse/LilaReports/${SITE}/${SEASON}_report_lila_image_inventory.csv \
--log_dir /home/packerc/shared/zooniverse/LilaReports/${SITE}/log_files/ \
--log_filename ${SEASON}_create_image_inventory
```

| Columns   | Description |
| --------- | ----------- |
|capture_id | internal identifier of the capture
|image_rank_in_capture| rank/order of the image in the capture
|image_path_rel| relative path of the image

### Transfer Images

Note: Pre-requisite is that rclone was configured correctly to access the target disk.

Transfer Images to LILA via qsub:

```
ssh mangi
cd $HOME/camera-trap-data-pipeline/reporting/jobs

SITE=RUA
SEASON=RUA_S1

qsub -v SITE=${SITE},SEASON=${SEASON} transfer_to_lila.pbs
```

This job syncronizes the images. If the job aborts or terminates early simply re-run it and it will pick up where it left off.
