from typing import List

import numpy as np
import models.page_templates as page_templates
import text_extraction.target_rectangles as target_rectangles
import models.data_classes as data_cls
from text_extraction.by_contours import get_img_text_by_contours


class ImageHandler:
    def __init__(self, image: np.ndarray, frame_time: str, is_first: bool):
        self.original_image = image
        self.frame_time = frame_time
        self.is_first = is_first
        self.page_type = None

    def process_img(self):
        h_screen, w_screen, _ = self.original_image.shape
        all_rectangles: List[data_cls.RectangleData] = target_rectangles.get_rect_by_contours(self.original_image)
        page_type: page_templates.BasePageType = page_templates.get_page_type(w_screen, h_screen, all_rectangles)
        header_rectangles: List[data_cls.RectangleData] = page_type.get_header_rectangles(all_rectangles)
        body_left_side_rectangles: List[data_cls.RectangleData] = page_type.get_body_left_side_rectangles(all_rectangles)
        header_rectangles_with_text: List[data_cls.RectangleData] = get_img_text_by_contours(self.original_image,
                                                                                             header_rectangles,
                                                                                             )
        body_left_side_rect_with_text: List[data_cls.RectangleData] = get_img_text_by_contours(self.original_image,
                                                                                               body_left_side_rectangles,
                                                                                               )
        page_type.create_header_payload(header_rectangles_with_text)
        page_type.create_body_left_side_payload(body_left_side_rect_with_text)
        self.page_type = page_type
