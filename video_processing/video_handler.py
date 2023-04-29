import dataclasses
import datetime
import json
import logging.config
import time
from typing import List, Dict, Optional

import cv2

from comparison.comparation import get_diff_percentage_img, check_if_text_is_new
from conf.logging_conf import LOGGING_CONFIG
import video_processing.image_handler as img_handler
import models.page_payload as payloads
from models.data_of_process import DataOfProcess
from models.report_data import StrReportData
from repositories.img_texts_repository import ImgTextsRepository
import models.repo_documents as repo_doc
import saving.save_to_dir as save_to_dir
import representative.report_selector as report_selector


logging.config.dictConfig(LOGGING_CONFIG)
_logger = logging.getLogger("app")


class VideoHandler:
    def __init__(self, file_path, output_folder, config, img_txt_repo):
        filename = file_path.split("/")[-1].split('.')[:-1][0]
        self.filename = filename
        self.output_folder_filename = output_folder + "/" + filename
        self.cap = cv2.VideoCapture(file_path)
        self.fps: int = self.cap.get(cv2.CAP_PROP_FPS)
        self.frame_count = 0
        self.is_first_frame = True
        self.config = config
        self.img_txt_repo: ImgTextsRepository = img_txt_repo
        self.frame_path = ''
        self.img_txt_doc: repo_doc.ImgTextsDocument = repo_doc.ImgTextsDocument.empty()
        self.time_of_frame_with_txt_s = []
        self.number_of_pages_with_text = 0
        self.list_of_data_to_representative: List[repo_doc.ImgTextsDocument] = []

        save_to_dir.create_dir(self.output_folder_filename)

        _logger.info(f"fps = {self.fps}")

    def start(self,
              number_of_frames_debug: int = None,
              start_at_debug: str = None,
              end_at_debug: str = None,
              ) -> None:
        start_script_time = time.time()

        THRESHOLD_OF_IMAGE_PRC = self.config["env"]["THRESHOLD_OF_IMAGE_PRC"]
        THRESHOLD_OF_TXTBOXES_LENGTH = self.config["env"]["THRESHOLD_OF_TXTBOXES_LENGTH"]
        THRESHOLD_OF_TXT_PRC = self.config["env"]["THRESHOLD_OF_TXT_PRC"]

        prev_img = None
        prev_text = []

        while self.cap.isOpened():
            start_time = time.time()
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

                # _logger.info("Parsing frame N {}, time={}".format(self.frame_count, frame_time))

                diff_percentage_img = get_diff_percentage_img(prev_img, frame)
                if diff_percentage_img < THRESHOLD_OF_IMAGE_PRC and not self.is_first_frame:
                    self.is_first_frame = False
                    continue
                prev_img = frame

                _logger.info(f"THRESHOLD_OF_IMAGE_PRC diff={round(diff_percentage_img, 2)}%, "
                              f"threshold={THRESHOLD_OF_IMAGE_PRC}%, time={frame_time}")

                im_handler = img_handler.ImageHandler(frame, frame_time, self.is_first_frame, self.config)
                im_handler.process_img()

                header_payload_opt: Optional[payloads.PagePayload] = im_handler.page_type.header_payload
                header_payload = header_payload_opt if header_payload_opt else []
                body_left_side_payload_opt: Optional[payloads.PagePayload] = im_handler.page_type.body_left_side_payload
                body_left_side_payload = body_left_side_payload_opt if body_left_side_payload_opt else []
                self.time_of_frame_with_txt_s.append(int((time.time() - start_time)))

                if not body_left_side_payload:
                    self.is_first_frame = False
                    _logger.info("Skip Frame, Body_payload is Empty")
                    continue

                text_arr: List[str] = body_left_side_payload.get_text_arr() if body_left_side_payload else []
                filtered_text_arr = [a for a in text_arr if a.strip(' ') != '']

                if len(filtered_text_arr) < len(text_arr) * 0.5 or \
                    not filtered_text_arr or \
                    not body_left_side_payload.payload:
                    self.is_first_frame = False
                    _logger.info("Skip Frame, Text is Empty")
                    continue

                #TODO uncomment if need filter by text
                # is_new_text = check_if_text_is_new(prev_text, text_arr,
                #                                    THRESHOLD_OF_TXTBOXES_LENGTH,
                #                                    THRESHOLD_OF_TXT_PRC,
                #                                    by_hash=False)
                #
                # if not is_new_text and not self.is_first_frame:
                #     self.is_first_frame = False
                #     continue
                # prev_text = text_arr

                _logger.info(header_payload.payload)
                _logger.info(body_left_side_payload.payload)

                _logger.info("SAVING "
                             f"diff_img={round(diff_percentage_img, 2)}, threshold={THRESHOLD_OF_IMAGE_PRC}:  "
                             f"text_threshold {THRESHOLD_OF_TXTBOXES_LENGTH}  "
                             f"time={frame_time}"
                             )
                try:
                    self.frame_path = self.output_folder_filename + "/" + frame_time + ".png"
                    save_to_dir.save_to_file(self.frame_path, frame, is_img=True)
                except Exception as e:
                    _logger.warning(f"Failed to save, time={frame_time}, \n{e}")
                    break

                self.img_txt_doc.video_name = self.filename
                self.img_txt_doc.frame_time = frame_time
                self.img_txt_doc.header = header_payload.payload
                self.img_txt_doc.body = body_left_side_payload.payload
                self.img_txt_doc.frame_path = self.frame_path
                self.img_txt_doc.created_time = str(datetime.datetime.now(tz=datetime.timezone.utc))

                if not self.img_txt_doc.is_empty:
                    self.img_txt_repo.insert_one(self.img_txt_doc.to_dict)
                    self.list_of_data_to_representative.append(dataclasses.replace(self.img_txt_doc))

                self.is_first_frame = False

                self.number_of_pages_with_text += 1
            else:
                break

        #================ create process doc ====================
        # report_doc = DataOfProcess(
        #     video_name=self.filename,
        #     fps=self.fps,
        #     avg_time_of_frame_with_txt_s=(sum(self.time_of_frame_with_txt_s) / len(self.time_of_frame_with_txt_s)),
        #     number_of_pages_with_text=self.number_of_pages_with_text,
        #     script_running_time=int((time.time() - start_script_time)),
        #     start_at=start_at_debug,
        #     end_at=end_at_debug,
        #     report_created_at=str(datetime.datetime.now(tz=datetime.timezone.utc).strftime("%H:%M:%S"))
        # )
        # report_path = self.output_folder_filename + "/process_doc.txt"
        # try:
        #     save_to_dir.save_to_file(report_path, report_doc.get_str_to_save, is_img=False)
        # except Exception as e:
        #     _logger.warning(f"Failed to save report, \n{e}")

        print('====================================================')
        _logger.info("Report GENERATING...")
        for doc in self.list_of_data_to_representative:
            html_report = report_selector.create_report(report_selector.ReportType.HTML, doc).response
            html_report_path = self.output_folder_filename + f"/html_report_{doc.frame_time}.html"
            save_to_dir.save_to_file(html_report_path, str(html_report), is_img=False)

            pdf_report_path = self.output_folder_filename + f"/pdf_report_{doc.frame_time}.pdf"
            saved = report_selector.create_report(report_selector.ReportType.PDF, StrReportData(str(html_report), pdf_report_path)).response

        if self.list_of_data_to_representative:
            excel_report_path = self.output_folder_filename + f"/excel_report.xlsx"
            saved = report_selector.create_report(report_selector.ReportType.EXCEL,
                                                  repo_doc.ImgTextsDocumentWithPath(self.list_of_data_to_representative, excel_report_path)).response


        self.cap.release()

    def formatted_time(self) -> str:
        timestamp_ms = self.cap.get(cv2.CAP_PROP_POS_MSEC)
        formatted_time = datetime.datetime.fromtimestamp(timestamp_ms / 1000.0, tz=datetime.timezone.utc) \
            .strftime("%H:%M:%S.%f")
        return formatted_time
