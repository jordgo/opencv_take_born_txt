import datetime
import logging.config
import os
import time

import click as click
import cv2
import yaml

from comparison.comparation import get_diff_percentage_img, check_if_text_is_new
from conf.logging_conf import LOGGING_CONFIG
from saving.save_to_dir import saving
from text_extraction.by_contours import get_img_text_by_contours

logging.config.dictConfig(LOGGING_CONFIG)
_logger = logging.getLogger("app")

with open("/conf/config.yml", 'r') as file:
    config = yaml.safe_load(file)

THRESHOLD_OF_IMAGE_PRC = 5
THRESHOLD_OF_TXTBOXES_LENGTH = 5
START_AT = "00:13:02.920000"
END_AT = "00:13:03.920000"


# START_AT = "00:00:00.920000"
# END_AT = "00:00:01.920000"


@click.command()
@click.argument('filename', type=click.Path(exists=True))
@click.argument('output_folder', type=click.Path(exists=True))
def main(file_path: str, output_folder):
    fn = file_path.split("/")[-1]
    # output_folder_filename = output_folder + "/" + filename.split("/")[-1]

    # try:
    #     os.makedirs(output_folder_filename)
    # except FileExistsError:
    #     _logger.warning(f"Folder Exists. Script finished. folder_name <{output_folder_filename}>")
    #     return 0
    # else:
    #     _logger.info(f"Folder Created. folder_name <{output_folder_filename}>")

    cap = cv2.VideoCapture(file_path)
    fps = cap.get(cv2.CAP_PROP_FPS)
    _logger.info(f"fps = {fps}")

    count = 0
    is_first = True
    prev_img = None
    prev_text = []
    last_timestamp = None

    while cap.isOpened():
        count += 1  # TODO del
        # if count == 2:
        #     break

        frame_exists, frame = cap.read()
        # frame = cv2.imread("image.png") #TODO rm

        if frame_exists:
            if is_first:
                prev_img = frame

            timestamp_ms = cap.get(cv2.CAP_PROP_POS_MSEC)
            time_form = datetime.datetime.fromtimestamp(timestamp_ms / 1000.0, tz=datetime.timezone.utc) \
                .strftime("%H:%M:%S.%f")

            last_timestamp = time_form  # TODO del

            if time_form < START_AT:  # TODO del
                continue
            elif time_form > END_AT:
                break

            _logger.info("Parsing frame N {}, time={}".format(count, time_form))

            diff_percentage_img = get_diff_percentage_img(prev_img, frame)
            _logger.debug(
                f"THRESHOLD_OF_IMAGE_PRC diff={round(diff_percentage_img, 2)}%, threshold={THRESHOLD_OF_IMAGE_PRC}%, time={time_form}")
            if diff_percentage_img < THRESHOLD_OF_IMAGE_PRC and not is_first:
                continue
            prev_img = frame

            text_arr, html_str = get_img_text_by_contours(frame)
            # print(text)  #TODO del
            if not text_arr:
                _logger.info("Skip Frame, Text is Empty")
                continue

            is_new_text = check_if_text_is_new(prev_text, text_arr, THRESHOLD_OF_TXTBOXES_LENGTH)
            if is_new_text:
                _logger.debug(f"Text is new, THRESHOLD={THRESHOLD_OF_TXTBOXES_LENGTH}, time={time_form}")
            if not is_new_text and not is_first:
                continue
            prev_text = text_arr

            _logger.info("SAVING "
                         f"diff_img={round(diff_percentage_img, 2)}, threshold={THRESHOLD_OF_IMAGE_PRC}:  "
                         f"text_threshold {THRESHOLD_OF_TXTBOXES_LENGTH}  "
                         f"time={time_form}"
                         )
            try:
                saving(output_folder_filename, time_form, html_str, frame, is_html=True)
                pass
            except Exception as e:
                _logger.warning(f"Failed to save, time={time_form}, \n{e}")
                break

            if is_first:
                is_first = False
        else:
            break

    print("last_timestamp", last_timestamp)

    cap.release()
    # cv2.destroyAllWindows()


if __name__ == "__main__":
    start_time = time.time()
    main()
    _logger.info(f"Script time {(time.time() - start_time) / 1000}sec")
