import datetime
import json
from typing import Optional, Dict

import cv2

import video_processing.image_handler as img_handler
import models.page_payload as payloads


def test_process_img():
    frame = cv2.imread("../imgs/image.png")
    is_first_frame = True
    frame_time = "00:13:02.920000"

    im_handler = img_handler.ImageHandler(frame, frame_time, is_first_frame)
    im_handler.process_img()
    body_left_side_payload_opt: Optional[payloads.PagePayload] = im_handler.page_type.body_left_side_payload
    header_payload_opt: Optional[payloads.PagePayload] = im_handler.page_type.header_payload

    def _to_json(header, body, f_time: str) -> str:
        data_to_save = {
            "header": header,
            "body": body
        }

        obj_to_save = {
            "_id": 1,
            "video_name": "video_name",
            "frame_time": f_time,
            "data": data_to_save,
            "frame_path": "???",
            "created_time": str(datetime.datetime.now(tz=datetime.timezone.utc))
        }

        return json.dumps(obj_to_save)

    print(_to_json(header_payload_opt.payload, body_left_side_payload_opt.payload, frame_time))
    assert True


