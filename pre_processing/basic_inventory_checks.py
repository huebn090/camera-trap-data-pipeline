""" Check images in inventory """
import os
import argparse
import logging
import time
import numpy as np
import copy
import traceback
from multiprocessing import Process, Manager
from PIL import Image

from utils.logger import set_logging
from pre_processing.utils import (
    datetime_file_creation, image_check_stats, p_pixels_above_threshold,
    p_pixels_below_threshold, export_inventory_to_csv, read_image_inventory,
    convert_ctime_to_datetime, convert_datetime_utc_to_timezone)
from utils.utils import (
    slice_generator, estimate_remaining_time)
from config.cfg import cfg


flags = cfg['pre_processing_flags']

# args = dict()
# args['root_dir'] = '/home/packerc/shared/albums/ENO/ENO_S1'
# args['output_csv'] = '/home/packerc/shared/season_captures/ENO/ENO_S1_captures_raw.csv'
# #args['output_csv'] = '/home/packerc/will5448/image_inventory_overview.csv'
# args['season_id'] = ''
# args['n_processes'] = 16


def _image_is_black(pixel_data, flags):
    black_percent = \
        flags['image_check_parameters']['all_black']['percent']
    black_thresh = \
        flags['image_check_parameters']['all_black']['thresh']
    p_pixels_black = p_pixels_below_threshold(
        pixel_data, black_thresh)
    return (p_pixels_black > black_percent)


def _image_is_white(pixel_data, flags):
    white_percent = \
        flags['image_check_parameters']['all_white']['percent']
    white_thresh = \
        flags['image_check_parameters']['all_white']['thresh']
    p_pixels_white = p_pixels_above_threshold(
        pixel_data, white_thresh)
    return (p_pixels_white > white_percent)


if __name__ == '__main__':

    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--inventory", type=str, required=True)
    parser.add_argument("--output_csv", type=str, required=True)
    parser.add_argument("--n_processes", type=int, default=4)
    parser.add_argument("--timezone", type=str, default=None)
    parser.add_argument(
        "--log_dir", type=str, default=None)
    parser.add_argument(
        "--log_filename", type=str,
        default='basic_inventory_checks')
    args = vars(parser.parse_args())

    ######################################
    # Check Input
    ######################################

    if not os.path.isfile(args['inventory']):
        raise FileNotFoundError("inventory: {} not found".format(
                                args['inventory']))

    ######################################
    # Configuration
    ######################################

    msg_width = 99

    # logging
    set_logging(args['log_dir'], args['log_filename'])

    logger = logging.getLogger(__name__)

    for k, v in args.items():
        logger.info("Argument {}: {}".format(k, v))

    # replace default timezone if timezone is specified
    if args['timezone'] is not None:
        old_tz = flags['time_formats']['default_timezone']
        flags['time_formats']['default_timezone'] = args['timezone']
        logger.info(
            "Timezone specified -- replacing timezone {} with {}".format(
                old_tz, args['timezone']))

    ######################################
    # Read Image Inventory
    ######################################

    image_inventory = read_image_inventory(
        args['inventory'],
        unique_id='image_path_original')

    # add check flags
    for image, image_data in image_inventory.items():
        image_data.update(
            {'image_check__{}'.format(k): 0
             for k in flags['image_checks']})

    ######################################
    # Process Inventory Images
    ######################################

    def process_image_batch(i, image_paths_batch, image_inventory, results):
        n_images_total = len(image_paths_batch)
        start_time = time.time()
        for img_no, image_path in enumerate(image_paths_batch):
            current_data = copy.deepcopy(image_inventory[image_path])
            # try to open the image
            try:
                img = Image.open(image_path)
            except:
                img = None
                current_data['image_check__corrupt_file'] = 1
                logger.debug(
                    "Failed to open file {}".format(
                     image_path))
            # get file creation date
            try:
                img_creation_date = datetime_file_creation(image_path)
                img_creation_date_dt = \
                    convert_ctime_to_datetime(img_creation_date)
                target_tz = flags['time_formats']['default_timezone']
                if target_tz != '':
                    img_creation_date_local = \
                        convert_datetime_utc_to_timezone(
                            img_creation_date_dt, target_tz)
                else:
                    img_creation_date_local = img_creation_date_dt
                img_creation_date_str = img_creation_date_local.strftime(
                    flags['time_formats']['output_datetime_format'])
                current_data['datetime_file_creation'] = img_creation_date_str
            except Exception:
                logger.error(
                    "Failed to read file creation date for {}".format(
                     image_path), exc_info=True)
                current_data['datetime_file_creation'] = ''
            # check for uniformly colored images
            try:
                pixel_data = np.asarray(img)
                if _image_is_black(pixel_data, flags):
                    current_data['image_check__all_black'] = 1
                if _image_is_white(pixel_data, flags):
                    current_data['image_check__all_white'] = 1
            except:
                logger.debug(
                    "Failed to check all_white/all_black for {}".format(
                     image_path))
            results[image_path] = current_data
            if (img_no % 100) == 0:
                est_t = estimate_remaining_time(
                    start_time, n_images_total, img_no)
                print("Process {:2} - Processed {}/{} images - ETA: {}".format(
                      i, img_no, n_images_total, est_t))
        print("Process {:2} - Finished".format(i))

    # Loop over all images
    image_paths_all = list(image_inventory.keys())
    n_images_total = len(image_paths_all)

    # parallelize image checking into 'n_processes'
    manager = Manager()
    results = manager.dict()
    try:
        processes_list = list()
        n_processes = min(args['n_processes'], n_images_total)
        slices = slice_generator(n_images_total, n_processes)
        for i, (start_i, end_i) in enumerate(slices):
            pr = Process(target=process_image_batch,
                         args=(i, image_paths_all[start_i:end_i],
                               image_inventory,
                               results))
            pr.start()
            processes_list.append(pr)
        for p in processes_list:
            p.join()
    except Exception:
        print(traceback.format_exc())

    # update data
    for image_path, image_data in image_inventory.items():
        image_inventory[image_path] = results[image_path]

    image_check_stats(image_inventory)

    export_inventory_to_csv(image_inventory, args['output_csv'])
