import cv2
import numpy as np
import pytest

from decors.prdecorators import print_time_of_script
from models.data_classes import RectangleData
from representers.html_representer import create_html
from saving.save_to_dir import saving
from text_extraction.by_contours import _get_tesseract_resp, _get_results_by_tesseract_configs, _get_text_by_max_conf, \
    get_img_text_by_contours, _enlarge_image_canvas


@pytest.mark.parametrize("img_path, exp", [#("imgs/symbol1.png", "->"),
                                           # ("imgs/4.png", "4 "),
                                           # ("imgs/3.8.png", "-3.8 "),
                                           ("imgs/0varius.png", "0° Varus "),
                                           ])
def test__get_results_by_tesseract_configs(img_path, exp):

    cropped = cv2.imread(img_path)

    # cv2.namedWindow('Test', cv2.WINDOW_NORMAL)
    # cv2.resizeWindow("Test", 1700, 900)
    # cv2.imshow("Test", thresh)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    results, count = _get_results_by_tesseract_configs(cropped)
    text, conf, r_coef, frame = _get_text_by_max_conf(results) if results else ("", 0, 0, np.ndarray([]))

    print(f"11111111111111111111111 {text}, conf={conf}, count_of_pass={count}")
    assert text == exp


def test__enlarge_image_canvas():
    img = cv2.imread("imgs/4.png")
    print(img.shape)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    resp = _enlarge_image_canvas(gray)
    assert resp.shape == (32, 29)
