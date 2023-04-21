import logging

import cv2
import numpy as np


_logger = logging.getLogger("app")


def get_diff_percentage_img(img1, img2) -> float:
    if img1.shape != img2.shape:
        return 100
    res = cv2.absdiff(img1, img2)
    res = res.astype(np.uint8)
    percentage = (np.count_nonzero(res) * 100) / res.size
    return percentage


def _clear_str(s: str) -> str:
    return s.replace(" ", "").replace("\n", "")


def check_if_text_is_new(txt1_arr, txt2_arr, THRESHOLD_OF_BOXES_LENGTH) -> bool:
    """check If the text is different from the previous one"""
    ln_t1 = len(txt1_arr)
    ln_t2 = len(txt2_arr)
    diff_ln = ln_t1 - ln_t2

    if abs(diff_ln) > THRESHOLD_OF_BOXES_LENGTH:
        return True

    count = 0
    for txt in txt2_arr:
        if txt not in txt1_arr:
            count += 1
            if count > THRESHOLD_OF_BOXES_LENGTH:
                return True

    _logger.debug(''.join(t+' ' for t in txt1_arr))
    _logger.debug(''.join(t+' ' for t in txt2_arr))

    return False
