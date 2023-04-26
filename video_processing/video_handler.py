import datetime
import json
import logging.config
from typing import List, Dict, Optional
import saving.save_to_dir as save_to_dir

import cv2

from comparison.comparation import get_diff_percentage_img, check_if_text_is_new
from conf.logging_conf import LOGGING_CONFIG
import video_processing.image_handler as img_handler
import models.page_payload as payloads
from repositories.img_texts_repository import ImgTextsRepository
import models.repo_documents as repo_doc


logging.config.dictConfig(LOGGING_CONFIG)
_logger = logging.getLogger("app")


class VideoHandler:
    def __init__(self, file_path, output_folder, config, img_txt_repo):
        filename = file_path.split("/")[-1].split('.')[:-1][0]
        self.filename = filename
        self.output_folder_filename = output_folder + "/" + filename
        self.cap = cv2.VideoCapture(file_path)
        self.frame_count = 0
        self.is_first_frame = True
        self.config = config
        self.img_txt_repo: ImgTextsRepository = img_txt_repo
        self.frame_path = ''
        self.img_txt_doc: repo_doc.ImgTextsDocument = repo_doc.ImgTextsDocument.empty()

        save_to_dir.create_dir(self.output_folder_filename)

        fps = self.cap.get(cv2.CAP_PROP_FPS)
        _logger.info(f"fps = {fps}")

    def start(self,
              number_of_frames_debug: int = None,
              start_at_debug: str = None,
              end_at_debug: str = None,
              ) -> None:
        THRESHOLD_OF_IMAGE_PRC = self.config["env"]["THRESHOLD_OF_IMAGE_PRC"]
        THRESHOLD_OF_TXTBOXES_LENGTH = self.config["env"]["THRESHOLD_OF_TXTBOXES_LENGTH"]
        THRESHOLD_OF_TXT_PRC = self.config["env"]["THRESHOLD_OF_TXT_PRC"]

        prev_img = None
        prev_text = []

        while self.cap.isOpened():
            self.frame_count += 1
            if number_of_frames_debug and self.frame_count > number_of_frames_debug:
                break

            frame_exists, frame = self.cap.read()

            if frame_exists:
                frame_time = self.formatted_time()

                if self.is_first_frame:
                    prev_img = frame

                # DEBUG
                if frame_time < start_at_debug:
                    continue
                elif frame_time > end_at_debug:
                    break

                _logger.info("Parsing frame N {}, time={}".format(self.frame_count, frame_time))

                diff_percentage_img = get_diff_percentage_img(prev_img, frame)
                _logger.debug(
                    f"THRESHOLD_OF_IMAGE_PRC diff={round(diff_percentage_img, 2)}%, threshold={THRESHOLD_OF_IMAGE_PRC}%, time={frame_time}")
                if diff_percentage_img < THRESHOLD_OF_IMAGE_PRC and not self.is_first_frame:
                    self.is_first_frame = False
                    continue
                prev_img = frame

                im_handler = img_handler.ImageHandler(frame, frame_time, self.is_first_frame)
                im_handler.process_img()

                # header_payload_opt = im_handler.page_type.header_payload
                # header_payload = header_payload_opt if header_payload_opt else []
                body_left_side_payload_opt: Optional[payloads.PagePayload] = im_handler.page_type.body_left_side_payload
                body_left_side_payload = body_left_side_payload_opt if body_left_side_payload_opt else []

                if not body_left_side_payload:
                    self.is_first_frame = False
                    _logger.info("Skip Frame, Body_payload is Empty")
                    continue

                text_arr: List[str] = body_left_side_payload.get_text_arr() if body_left_side_payload else []

                if not text_arr:
                    self.is_first_frame = False
                    _logger.info("Skip Frame, Text is Empty")
                    continue

                is_new_text = check_if_text_is_new(prev_text, text_arr,
                                                   THRESHOLD_OF_TXTBOXES_LENGTH,
                                                   THRESHOLD_OF_TXT_PRC,
                                                   by_hash=False)

                if not is_new_text and not self.is_first_frame:
                    self.is_first_frame = False
                    continue
                prev_text = text_arr

                _logger.info("SAVING "
                             f"diff_img={round(diff_percentage_img, 2)}, threshold={THRESHOLD_OF_IMAGE_PRC}:  "
                             f"text_threshold {THRESHOLD_OF_TXTBOXES_LENGTH}  "
                             f"time={frame_time}"
                             )
                try:
                    self.frame_path = self.output_folder_filename + "/" + frame_time + ".png"
                    save_to_dir.save_to_file(self.frame_path, frame, is_img=True)
                    pass
                except Exception as e:
                    _logger.warning(f"Failed to save, time={frame_time}, \n{e}")
                    break

                self.img_txt_doc.video_name = self.filename
                self.img_txt_doc.frame_time = frame_time
                self.img_txt_doc.data = body_left_side_payload.payload
                self.img_txt_doc.frame_path = self.frame_path
                self.img_txt_doc.created_time = str(datetime.datetime.now(tz=datetime.timezone.utc))

                if not self.img_txt_doc.is_empty:
                    self.img_txt_repo.insert_one(self.img_txt_doc.to_dict)

                self.is_first_frame = False

            else:
                break

        self.cap.release()
        # create_report

    def formatted_time(self) -> str:
        timestamp_ms = self.cap.get(cv2.CAP_PROP_POS_MSEC)
        formatted_time = datetime.datetime.fromtimestamp(timestamp_ms / 1000.0, tz=datetime.timezone.utc) \
            .strftime("%H:%M:%S.%f")
        return formatted_time
