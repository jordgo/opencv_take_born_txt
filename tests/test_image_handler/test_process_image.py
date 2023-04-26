import datetime
import json
from typing import Optional, Dict

import cv2
import pytest

import video_processing.image_handler as img_handler
import models.page_payload as payloads

body_res_full = [[{'key': {'x': 228, 'y': 199, 'w': 69, 'h': 24, 'text': 'CaselD '}, 'value': {'x': 426, 'y': 199, 'w': 153, 'h': 24, 'text': '35DB61C992554 '}}, {'key': {'x': 193, 'y': 254, 'w': 139, 'h': 29, 'text': 'Operative Side '}, 'value': {'x': 472, 'y': 255, 'w': 61, 'h': 24, 'text': 'RIGHT '}}, {'key': {'x': 195, 'y': 309, 'w': 135, 'h': 30, 'text': 'Implant Design '}, 'value': {'x': 457, 'y': 310, 'w': 91, 'h': 30, 'text': 'Legion CR '}}], [{'key': {'x': 153, 'y': 432, 'w': 219, 'h': 30, 'text': 'Pre-Operative Alignment '}, 'value': {'x': 461, 'y': 434, 'w': 83, 'h': 24, 'text': '8° Varus '}}, {'key': {'x': 179, 'y': 496, 'w': 168, 'h': 30, 'text': 'Planned Alignment '}, 'value': {'x': 463, 'y': 498, 'w': 79, 'h': 24, 'text': '1° Varus '}}, {'key': {'x': 173, 'y': 560, 'w': 179, 'h': 30, 'text': 'Achieved Alignment '}, 'value': {'x': 461, 'y': 562, 'w': 83, 'h': 24, 'text': '2° Varus '}}, {'key': {'x': 164, 'y': 626, 'w': 258, 'h': 29, 'text': 'Pre-Operative Flexion  Range '}, 'value': {'x': 440, 'y': 626, 'w': 74, 'h': 23, 'text': '13°  120° '}}, {'key': {'x': 159, 'y': 690, 'w': 268, 'h': 30, 'text': 'Post-Operative Flexion  Range '}, 'value': {'x': 444, 'y': 690, 'w': 67, 'h': 23, 'text': '7°  135° '}}, {'key': {'x': 213, 'y': 754, 'w': 99, 'h': 25, 'text': 'Femur Size '}, 'value': {'x': 493, 'y': 755, 'w': 19, 'h': 24, 'text': '4 '}}, {'key': {'x': 217, 'y': 818, 'w': 90, 'h': 25, 'text': 'Tibia Size '}, 'value': {'x': 494, 'y': 819, 'w': 18, 'h': 23, 'text': '2 '}}, {'key': {'x': 216, 'y': 882, 'w': 92, 'h': 25, 'text': 'Thickness '}, 'value': {'x': 476, 'y': 883, 'w': 54, 'h': 24, 'text': '9mm '}}]]
header_res_full = [{'x': 670, 'y': 41, 'w': 177, 'h': 61, 'text': 'PostOp '}, {'x': 854, 'y': 41, 'w': 105, 'h': 61, 'text': 'Gap '}, {'x': 965, 'y': 41, 'w': 290, 'h': 50, 'text': 'Assessment '}]
body_res_txt = ['CaselD ', '35DB61C992554 ', 'Operative Side ', 'RIGHT ', 'Implant Design ', 'Legion CR ',
                'Pre-Operative Alignment ', '8° Varus ', 'Planned Alignment ', '1° Varus ', 'Achieved Alignment ',
                '2° Varus ', 'Pre-Operative Flexion  Range ', '13°  120° ', 'Post-Operative Flexion  Range ',
                '7°  135° ', 'Femur Size ', '4 ', 'Tibia Size ', '2 ', 'Thickness ', '9mm ']
header_res_txt = ['PostOp ', 'Gap ', 'Assessment ']
header_res_txt2 = [] #['Tibia ', 'Removal ', 'Bone ']  #TODO need to define one more PageTemplate with another header size

@pytest.mark.parametrize("img_path, body_exp, header_exp", [
                         ("../imgs/image.png", body_res_txt, header_res_txt),
                         ("../imgs/image1.png", [], header_res_txt2),
                         ])
def test_process_img(img_path, body_exp, header_exp):
    frame = cv2.imread(img_path)
    is_first_frame = True
    frame_time = "00:13:02.920000"

    im_handler = img_handler.ImageHandler(frame, frame_time, is_first_frame)
    im_handler.process_img()
    body_left_side_payload_opt: Optional[payloads.PagePayload] = im_handler.page_type.body_left_side_payload
    header_payload_opt: Optional[payloads.PagePayload] = im_handler.page_type.header_payload

    _header = get_header_txt(header_payload_opt.payload)
    _body = get_body_txt(body_left_side_payload_opt.payload) if body_left_side_payload_opt else []

    # print(get_body_txt(body_left_side_payload_opt.payload))
    print(get_header_txt(header_payload_opt.payload))

    assert _body == body_exp
    assert _header == header_exp


def get_body_txt(shapes):
    texts = []
    for shape in shapes:
        for shape_line in shape:
            texts.append(shape_line["key"]["text"])
            texts.append(shape_line["value"]["text"])
    return texts


def get_header_txt(shape):
    texts = []
    for rect in shape:
        texts.append(rect["text"])
    return texts



