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


def check_if_text_is_new(txt1_arr, txt2_arr, THRESHOLD_OF_BOXES_LENGTH, THRESHOLD_OF_TXT_PRC, by_hash: bool) -> bool:
    """check If the text is different from the previous one"""
    ln_t1 = len(txt1_arr)
    ln_t2 = len(txt2_arr)
    diff_ln = ln_t1 - ln_t2

    if abs(diff_ln) > THRESHOLD_OF_BOXES_LENGTH:
        _logger.debug(''.join(t + ' ' for t in txt1_arr))
        _logger.debug(''.join(t + ' ' for t in txt2_arr))
        return True

    if by_hash:
        txt1_str = ''.join(txt1_arr).replace(' ', '')
        txt2_str = ''.join(txt2_arr).replace(' ', '')
        h1 = hash(txt1_str)
        h2 = hash(txt2_str)

        _logger.debug(f'{h1} Prev hash')
        _logger.debug(f'{h2} Current hash')

        _logger.debug(''.join(t + ' ' for t in txt1_arr))
        _logger.debug(''.join(t + ' ' for t in txt2_arr))

        return h1 != h2
    else:
        count = 0
        for i in range(len(txt2_arr)):
            if txt1_arr[i].lower().replace(" ", "") != txt2_arr[i].lower().replace(" ", ""):
                count += 1

        diff_prc = (count * 100) / len(txt2_arr)
        _logger.debug(f"Text diff prc={diff_prc}, threshold={THRESHOLD_OF_TXT_PRC}")
        if diff_prc > THRESHOLD_OF_TXT_PRC:
            return True

    return False
