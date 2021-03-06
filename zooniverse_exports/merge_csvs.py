""" Merge CSVs based on common key """
import os
import logging
import argparse

from utils.logger import setup_logger
from utils.utils import merge_csvs, sort_df_by_capture_id, set_file_permission


if __name__ == '__main__':

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--base_csv", type=str, required=True)
    parser.add_argument("--to_add_csv", type=str, required=True)
    parser.add_argument("--output_csv", type=str, required=True)
    parser.add_argument("--key", type=str, required=True)
    parser.add_argument("--add_new_cols_to_right", action='store_true')

    args = vars(parser.parse_args())

    ######################################
    # Check Input
    ######################################

    if not os.path.isfile(args['base_csv']):
        raise FileNotFoundError("base_csv: {} not found".format(
                                args['base_csv']))

    if not os.path.isfile(args['to_add_csv']):
        raise FileNotFoundError("to_add_csv: {} not found".format(
                                args['to_add_csv']))

    if args['output_csv'] is None:
        args['output_csv'] = args['base_csv']

    ######################################
    # Configuration
    ######################################

    setup_logger()
    logger = logging.getLogger(__name__)

    for k, v in args.items():
        logger.info("Argument {}: {}".format(k, v))

    df = merge_csvs(
        args['base_csv'], args['to_add_csv'], args['key'],
        args['add_new_cols_to_right'])
    # sort by capture_id
    if args['key'] == 'capture_id':
        sort_df_by_capture_id(df)

    df.to_csv(args['output_csv'], index=False)

    logger.info("Wrote {} records to {}".format(
        df.shape[0], args['output_csv']))

    # change permmissions to read/write for group
    set_file_permission(args['output_csv'])
