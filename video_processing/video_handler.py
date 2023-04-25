import datetime
import json
import logging.config
from typing import List, Dict, Optional

import yaml

import cv2

from comparison.comparation import get_diff_percentage_img, check_if_text_is_new
from conf.logging_conf import LOGGING_CONFIG
import video_processing.image_handler as img_handler
import models.page_payload as payloads


logging.config.dictConfig(LOGGING_CONFIG)
_logger = logging.getLogger("app")


class VideoHandler:
    def __init__(self, file_path, config):
        self.filename = file_path.split("/")[-1]
        self.cap = cv2.VideoCapture(file_path)
        self.frame_count = 0
        self.is_first_frame = True
        self.config = config

        fps = self.cap.get(cv2.CAP_PROP_FPS)
        _logger.info(f"fps = {fps}")

    def start(self,
              number_of_frames_debug: int = None,
              start_at_debug: str = None,
              end_at_debug: str = None,
              ) -> None:
        THRESHOLD_OF_IMAGE_PRC = self.config["env"]["THRESHOLD_OF_IMAGE_PRC"]
        THRESHOLD_OF_TXTBOXES_LENGTH = self.config["env"]["THRESHOLD_OF_TXTBOXES_LENGTH"]
        prev_img = None
        prev_text = []

        while self.cap.isOpened():
            self.frame_count += 1
            if number_of_frames_debug and self.frame_count > number_of_frames_debug:
                break

            frame_exists, frame = self.cap.read()

            if frame_exists:
                frame_time = self.formatted_time()

                if frame_time < start_at_debug:  # DEBUG
                    continue
                elif frame_time > end_at_debug:
                    break

                _logger.info("Parsing frame N {}, time={}".format(self.frame_count, frame_time))

                diff_percentage_img = get_diff_percentage_img(prev_img, frame)
                _logger.debug(
                    f"THRESHOLD_OF_IMAGE_PRC diff={round(diff_percentage_img, 2)}%, threshold={THRESHOLD_OF_IMAGE_PRC}%, time={frame_time}")
                if diff_percentage_img < THRESHOLD_OF_IMAGE_PRC and not self.is_first_frame:
                    continue
                prev_img = frame

                image_handler = img_handler.ImageHandler(frame, frame_time, self.is_first_frame)
                image_handler.process_img()

                header_payload_opt: Optional[payloads.PagePayload] = image_handler.page_type.header_paylod
                header_payload = header_payload_opt if header_payload_opt else []
                body_left_side_payload_opt: Optional[payloads.PagePayload] = image_handler.page_type.body_left_side_payload
                body_left_side_payload = body_left_side_payload_opt if body_left_side_payload_opt else []
                text_arr: List[str] = body_left_side_payload.get_text_arr() if body_left_side_payload else []

                if not text_arr:
                    _logger.info("Skip Frame, Text is Empty")
                    continue

                is_new_text = check_if_text_is_new(prev_text, text_arr, THRESHOLD_OF_TXTBOXES_LENGTH)
                if is_new_text:
                    _logger.debug(f"Text is new, THRESHOLD={THRESHOLD_OF_TXTBOXES_LENGTH}, time={frame_time}")
                if not is_new_text and not self.is_first_frame:
                    continue
                prev_text = text_arr

                obj_to_save = self._to_json(header_payload.payload, body_left_side_payload.payload, frame_time)

                print(json.dumps(obj_to_save))


                self.is_first_frame = False

            else:
                break


    def formatted_time(self) -> str:
        timestamp_ms = self.cap.get(cv2.CAP_PROP_POS_MSEC)
        formatted_time = datetime.datetime.fromtimestamp(timestamp_ms / 1000.0, tz=datetime.timezone.utc) \
            .strftime("%H:%M:%S.%f")
        return formatted_time

    def _to_json(self, header: Dict[str], body: Dict[str], frame_time: str) -> str:
        data_to_save = {
            "header": header,
            "body": body
        }

        obj_to_save = {
            "_id": 1,
            "video_name": self.filename,
            "frame_time": frame_time,
            "data": data_to_save,
            "frame_path": "???",
            "created_time": datetime.datetime.now(tz=datetime.timezone.utc)
        }

        return json.dumps(obj_to_save)
