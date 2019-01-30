""" Integrate Aggregated Predictions into Manifest """
import json
import os
import argparse

from utils import (
    export_dict_to_json_with_newlines, file_path_splitter, file_path_generator)

# # For Testing
# args = dict()
# args['manifest'] = "/home/packerc/shared/zooniverse/Manifests/KAR/KAR_S1_manifest.json"
# args['predictions_empty'] = "/home/packerc/shared/zooniverse/Manifests/KAR/KAR_S1_predictions_empty_or_not.json"
# args['predictions_species'] = "/home/packerc/shared/zooniverse/Manifests/KAR/KAR_S1_predictions_species.json"
# args['output_file'] = "/home/packerc/shared/zooniverse/Manifests/KAR/KAR_S1_manifest1.json"

if __name__ == "__main__":

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--manifest", type=str, required=True,
        help="Path to manifest file (.json)")
    parser.add_argument(
        "--predictions_empty", type=str, default=None,
        help="Path to the file with predictions from the empty model \
              (.json). Default is to generate the name based on the manifest.")
    parser.add_argument(
        "--predictions_species", type=str, default=None,
        help="Path to the file with predictions from the species model \
              (.json). Default is to generate the name based on the manifest.")
    parser.add_argument(
        "--output_file", type=str, default=None,
        help="Output file to write new manifest to (.json). \
              Default is to overwrite the manifest.")

    args = vars(parser.parse_args())

    for k, v in args.items():
        print("Argument %s: %s" % (k, v))

    # Check Inputs
    if not os.path.exists(args['manifest']):
        raise FileNotFoundError("manifest: %s not found" %
                                args['manifest'])

    if args['output_file'] is None:
        args['output_file'] = args['manifest']
        print("Updating %s with machine scores" % args['output_file'])

    file_name_parts = file_path_splitter(args['manifest'])
    if args['predictions_empty'] is None:
        args['predictions_empty'] = file_path_generator(
            dir=os.path.dirname(args['manifest']),
            id=file_name_parts['id'],
            name='predictions_empty_or_not',
            batch=file_name_parts['batch'],
            file_delim=file_name_parts['file_delim'],
            file_ext='json'
        )
        print("Reading empty predictions from %s" % args['predictions_empty'])
    if args['predictions_species'] is None:
        args['predictions_species'] = file_path_generator(
            dir=os.path.dirname(args['manifest']),
            id=file_name_parts['id'],
            name='predictions_species',
            batch=file_name_parts['batch'],
            file_delim=file_name_parts['file_delim'],
            file_ext='json'
        )
        print("Reading species predictions from %s" %
              args['predictions_species'])

    if not os.path.exists(args['predictions_species']):
        raise FileNotFoundError("predictions: %s not found" %
                                args['predictions_species'])

    if not os.path.exists(args['predictions_empty']):
        raise FileNotFoundError("predictions: %s not found" %
                                args['predictions_empty'])

    # import manifest
    with open(args['manifest'], 'r') as f:
        mani = json.load(f)

    # import predictions
    with open(args['predictions_species'], 'r') as f:
        preds_species = json.load(f)

    with open(args['predictions_empty'], 'r') as f:
        preds_empty = json.load(f)

    def _add_prediction_data(preds, meta_data):
        """ Add Prediction Data to Meta-Data """
        top_preds = preds["predictions_top"]
        top_conf = preds["confidences_top"]

        # Add Top label Text
        for pred_label, pred_value in top_preds.items():
            meta_key = '#machine_prediction_%s' % pred_label
            meta_data[meta_key] = pred_value

        # Add Top label Confidence
        for pred_label, pred_value in top_conf.items():
            meta_key = '#machine_confidence_%s' % pred_label
            meta_data[meta_key] = pred_value

    captures_with_preds = 0
    n_total = len(mani.keys())

    # Extract predictions and add to manifest
    for capture_id, data in mani.items():
        # set ml to False per default
        data['info']['machine_learning'] = False
        meta_data = data['upload_metadata']

        # get predictions empty
        if capture_id in preds_empty:
            current_preds = preds_empty[capture_id]
            _add_prediction_data(current_preds, meta_data)
            # adjust status
            data['info']['machine_learning'] = True

        # add species predictions
        if capture_id in preds_species:
            current_preds = preds_species[capture_id]
            _add_prediction_data(current_preds, meta_data)
            # adjust status
            data['info']['machine_learning'] = True

        if data['info']['machine_learning']:
            captures_with_preds += 1

    # statistic
    print("Added predictions to %s / %s captures" %
          (captures_with_preds, n_total))

    # Export Manifest
    export_dict_to_json_with_newlines(mani, args['output_file'])

    # change permmissions to read/write for group
    os.chmod(args['output_file'], 0o660)