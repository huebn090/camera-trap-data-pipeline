""" Upload Manifest to Zooniverse """
import argparse
import csv

from panoptes_client import Project, Panoptes, SubjectSet

from utils import read_config_file

# # For Testing
# args = dict()
# args['manifest'] = "/home/packerc/shared/zooniverse/Manifests/KAR/KAR_S1_manifest1.json"
# args['output_file'] = "/home/packerc/shared/zooniverse/Manifests/KAR/KAR_S1_manifest2.json"
# args['project_id'] = 7679
# #args['subject_set_id'] = '40557'
# args['subject_set_name'] = 'KAR_S1_TEST_v2'
# args['password_file'] = '~/keys/passwords.ini'


# python3 -m zooniverse_uploads.find_duplicates \
# -output_file ${HOME}/duplicates_test.csv \
# -project_id 5880 \
# -subject_set_id 71542 \
# -password_file ~/keys/passwords.ini \
# -remove_duplicates

if __name__ == "__main__":

    # Parse command line arguments
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-project_id", type=int, required=True,
        help="Zooniverse project id")

    parser.add_argument(
        "-subject_set_id", type=str, required=False, default='',
        help="Zooniverse subject set id. Specify if you want to add subjects\
              to an existing set (useful if upload crashed)")

    parser.add_argument(
        "-password_file", type=str, required=True,
        help="File that contains the Zooniverse password (.ini),\
              Example File:\
              [zooniverse]\
              username: dummy\
              password: 1234")

    parser.add_argument(
        "-output_file", type=str, required=True,
        help="Output file for duplicates (.csv)")

    parser.add_argument(
        "-remove_duplicates", action='store_true',
        help="Remove duplicate subjects")

    args = vars(parser.parse_args())

    for k, v in args.items():
        print("Argument %s: %s" % (k, v))

    # read Zooniverse credentials
    config = read_config_file(args['password_file'])

    # connect to panoptes
    Panoptes.connect(username=config['zooniverse']['username'],
                     password=config['zooniverse']['password'])

    # Get Project
    my_project = Project(args['project_id'])

    # Get or Create a subject set
    # Get a subject set
    my_set = SubjectSet().find(args['subject_set_id'])
    print("Subject set found, looking for already uploaded subjects",
          flush=True)
    # find already uploaded subjects
    ids_uploaded = dict()
    n_already_uploaded = 0
    duplicated_subject_ids = set()
    for subject in my_set.subjects:
        n_already_uploaded += 1
        if (n_already_uploaded % 100) == 0:
            print("Found %s uploaded records and counting..." %
                  n_already_uploaded, flush=True)
        roll = subject.metadata['#roll']
        site = subject.metadata['#site']
        capture = subject.metadata['#capture']
        season = subject.metadata['#season']
        capture_id = '#'.join([season, site, roll, capture])
        subject_id = subject.id
        if capture_id not in ids_uploaded:
            ids_uploaded[capture_id] = 0
        else:
            duplicated_subject_ids.add(subject_id)
            n_already_found = ids_uploaded[capture_id]
            print("Duplicate for id: %s already found %s times" %
                  (capture_id, n_already_found), flush=True)

        ids_uploaded[capture_id] += 1
        if subject_id in ('28821178', '28935939'):
            print("TEST case id %s" % subject_id)
            print("FOUND ids_uploaded %s" % ids_uploaded[capture_id])
            print("IS IN DUPLICATE: %s" % (subject_id in duplicated_subject_ids))

    print("Found %s capture ids that were uploaded more than once" %
          len(duplicated_subject_ids))

    if args['remove_duplicates']:
        n_dups = len(duplicated_subject_ids)
        print("Found %s subjects to unlink" % n_dups)
        for subject_id_to_remove in duplicated_subject_ids:
            print("Removing id %s" % subject_id_to_remove)
        subjects_to_remove_list = list(duplicated_subject_ids)
        # my_set.remove(subjects_to_remove_list)

    # Export Manifest
    with open(args['output_file'], 'w') as csvfile:
        csvwriter = csv.writer(csvfile, delimiter=',')
        # write header
        header = ['capture_id', 'n_uploads']
        csvwriter.writerow(header)
        # Write each capture event and the associated images
        for capture_id, n_uploaded in ids_uploaded.items():
            csvwriter.writerow([capture_id, n_uploaded])
