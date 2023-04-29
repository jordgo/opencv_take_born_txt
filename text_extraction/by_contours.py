import logging
import subprocess
from types import SimpleNamespace
from typing import List

import cv2
import easyocr
import numpy as np
from pytesseract import pytesseract

from decors.prdecorators import print_time_of_script
from definition import ROOT_DIR
from models.data_classes import TesseractResp, RectangleData
from saving import save_to_dir
from saving.save_to_dir import saving

_logger = logging.getLogger("app")

EASY_OCR_CONF = 0.85
CROPPED_RESIZE_COEFF = 10
TESSERACT_QUALITY = 89
TESSERACT_QUALITY_MIN = 80  # 70
TESSERACT_BLACKLIST = '©'
TESSERACT_CONF_MAIN = f'-l eng --oem 1 -c tessedit_char_blacklist={TESSERACT_BLACKLIST} --psm 3 ' \
                      f'--tessdata-dir /home/george/PycharmProjects/open_cv_take_bone_txt/utility/tessdata'  # 3 7
TESSERACT_CONF_MAIN_WAITLIST = '-l eng --oem 1 --psm 3 ' \
                               '-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789abcdefghijklmnopqrstuvwxyz.-><°' \
                               '--tessdata-dir /home/george/PycharmProjects/open_cv_take_bone_txt/utility/tessdata'  # 3 7
TESSERACT_CONF_DIGITS = f'-l eng --oem 1 -c tessedit_char_whitelist=-0123456789.->°m --psm 6 ' \
                        f'--tessdata-dir /home/george/PycharmProjects/open_cv_take_bone_txt/utility/tessdata'  # 4 6 7 8
TESSERACT_CONF_SYMBOLS = f'-l eng --oem 1 -c tessedit_char_whitelist=-> -c tessedit_char_blacklist={TESSERACT_BLACKLIST} --psm 6'
TESSERACT_CONF_IN_CIRCLE = f'-l eng --oem 1 -c tessedit_char_blacklist={TESSERACT_BLACKLIST} --psm 9'


def _enlarge_image_canvas(gray: np.ndarray) -> np.ndarray:
    """
    enlargement of the canvas for better recognition
    :param gray:np.ndarray
    :return:np.ndarray - increased
    """
    h, w = gray.shape
    add_h = int(h * 0.2)
    add_w = int(w * 0.2)
    count_of_iter = add_w if add_w > add_h else add_h
    arr_res = np.ndarray
    for i in range(count_of_iter):
        if i == 0:
            h, w = gray.shape
            if add_h > 0:
                arr_res = np.insert(gray, [0, h], 0, axis=0)
                add_h -= 1
            if add_w > 0:
                arr_res = np.insert(arr_res, [0, w], 0, axis=1)
                add_w -= 1
        else:
            h, w = arr_res.shape
            if add_h > 0:
                arr_res = np.insert(arr_res, [0, h], 0, axis=0)
                add_h -= 1
            if add_w > 0:
                arr_res = np.insert(arr_res, [0, w], 0, axis=1)
                add_w -= 1
    return arr_res


def _get_tesseract_resp(cropped: np.ndarray, resize_coeff: int, config) -> TesseractResp:
    """
    parses the cropped image with the Tesseract library
    :param cropped: np.ndarray - original cropped image
    :param resize_coeff: int - picture magnification factor
    :param config: str - Tesseract config
    :return:  TesseractResp
    """
    gray = cv2.cvtColor(cropped, cv2.COLOR_BGR2GRAY)
    resized = cv2.resize(gray, None, fy=resize_coeff, fx=resize_coeff, interpolation=cv2.INTER_LINEAR)
    # enlarged = _enlarge_image_canvas(resized)
    morph_kernel = np.ones((5, 5))
    erode_img = cv2.erode(resized, kernel=morph_kernel, iterations=1)
    dilate_img = cv2.dilate(erode_img, kernel=morph_kernel, iterations=1)
    ret, thresh = cv2.threshold(dilate_img, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY)

    # cv2.imshow("Test", thresh)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    # tesseract
    word = pytesseract.image_to_data(thresh, output_type=pytesseract.Output.DICT, config=config)
    text = ''
    conf = 0
    sum_conf = 0
    count_of_words = 0
    # print(word["text"])  #TODO DEBUG ONLY
    # print(word["conf"])
    for i in range(len(word["text"])):
        txt = word['text'][i]
        cnf = word["conf"][i]
        if txt != '':
            count_of_words += 1
            sum_conf = sum_conf + cnf
            conf = sum_conf / count_of_words
            text = text + txt + ' '

    text, conf = (text, conf) if conf > TESSERACT_QUALITY_MIN else ('', 0)
    # print('99999999999999999999999', text, conf, resize_coeff)
    return TesseractResp(text=text, conf=conf, resize_coeff=resize_coeff, frame=thresh)


def _get_text_by_max_conf(results) -> TesseractResp:
    """
    gets the text at maximum confidence
    :param results: list[TesseractResp]
    :return: TesseractResp
    """
    max_conf = max([r.conf for r in results])
    tesseract_resp = [r for r in results if r.conf == max_conf][0]
    return tesseract_resp


def _get_results(config: str, cropped: np.ndarray) -> tuple:
    """
    gets data for each image zoom
    :param config: str - tesseract config
    :param cropped: np.ndarray - original cropped image
    :return: tuple(list[TesseractResp], int) - with count of pass
    """
    results = []
    count = 0
    for resize_coeff in range(2, 10, 2):
        count += 1
        tesseract_resp = _get_tesseract_resp(cropped, resize_coeff, config)
        results.append(tesseract_resp)
        if tesseract_resp.conf > TESSERACT_QUALITY:
            break
    return results, count


def _parse_with_easy_ocr(cropped: np.ndarray) -> tuple:
    reader = easyocr.Reader(['en'])
    result1 = reader.readtext(cropped, detail=1)
    filtered_result1 = [t for t in result1 if t[2] > EASY_OCR_CONF]
    concat_res = ' '.join([t[1] for t in filtered_result1])
    resp = TesseractResp(concat_res, 90, 2, cropped)
    return [resp], 1


def _get_results_by_tesseract_configs(cropped: np.ndarray) -> tuple:
    """
    If the result is not found, changes the tesseract configuration
    :param cropped: np.ndarray - original cropped image
    :return: tuple(list[TesseractResp], int) - with sum of count of pass
    """
    results, count1 = _get_results(TESSERACT_CONF_MAIN, cropped)

    count2 = 0
    if _get_text_by_max_conf(results).conf == 0:
        results, count2 = _get_results(TESSERACT_CONF_DIGITS, cropped)

    count3 = 0
    if _get_text_by_max_conf(results).conf == 0:
        results, count3 = _parse_with_easy_ocr(cropped)

    count = count1 + count2 + count3

    # if get_text_by_max_conf(results)[1] == 0:
    #     results = get_results(TESSERACT_CONF_SYMBOLS)

    return results, count


def _loop_through_rectangles(img: np.ndarray,
                             rectangles,
                             from_box_debug: int = None,
                             to_box_debug: int = None,
                             save_cropped_img_path_debug: str = None,
                             ) -> [RectangleData]:
    """
    cuts out areas from original image, gets text from areas
    :param img:np.ndarray - original frame
    :param rectangles:list[RectangleData] - without text
    :param from_box_debug: int - DEBUG ONLY
    :param to_box_debug: int - DEBUG ONLY
    :param save_cropped_img_path_debug: str - DEBUG ONLY - saving cropped img to ./test/test_text_extraction/test_by_contours/imgs/result
    :return:list[RectangleData] - with text
    """
    rectangles_txt = []
    count = 0
    for r in reversed(rectangles):
        count += 1
        if from_box_debug and count < from_box_debug:
            continue
        if to_box_debug and count > to_box_debug:
            break
        cropped: np.ndarray = img[r.y:r.y + r.h, r.x:r.x + r.w]
        results, count_of_pass = _get_results_by_tesseract_configs(cropped)
        text, conf, r_coef, frame = _get_text_by_max_conf(results) if results else ("", 0, 0, np.ndarray([]))

        #DEBUG
        if save_cropped_img_path_debug:
            # _logger.debug(f"11111111111111111111111 {text}, conf={conf}, count_of_pass={count_of_pass}")
            saving(ROOT_DIR + '/tests/imgs/result', f"{count}_{text}", text, frame, False)

        if text != '':
            r.text = text
            rectangles_txt.append(r)

    return rectangles_txt


@print_time_of_script
def get_img_text_by_contours(orig_img: np.ndarray,
                             rectangles: List[RectangleData],
                             from_box_debug: int = None,
                             to_box_debug: int = None,
                             save_cropped_img_path_debug: str = None,
                             ) -> List[RectangleData]:
    """
    Gets arr[string] and html using tesseract
    :param orig_img:np.ndarray original image
    :param rectangles: List[RectangleData] - rectangles without text
    :param from_box_debug: int - DEBUG ONLY
    :param to_box_debug: int - DEBUG ONLY
    :param save_cropped_img_path_debug: str - DEBUG ONLY - saving cropped img to ./tes/test_text_extraction/test_by_contours/imgs/result
    :return: List[RectangleData] - rectangles with text
    """
    tesseract_path = subprocess.run(['which', 'tesseract'], stdout=subprocess.PIPE) \
        .stdout.decode('utf-8').replace('\n', '')
    pytesseract.tesseract_cmd = tesseract_path

    # rectangles = get_rect_by_contours(orig_img)
    rectangles_with_txt = _loop_through_rectangles(orig_img, rectangles, from_box_debug, to_box_debug, save_cropped_img_path_debug)

    # text_arr = [o.text for o in rectangles_with_txt]
    # html_str = create_html(rectangles_with_txt)

    return rectangles_with_txt
