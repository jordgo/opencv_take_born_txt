import cv2
import numpy as np
import pytest

from models.data_classes import RectangleData
from text_extraction.target_rectangles import get_rect_by_contours, _get_lines, _get_count_of_points_per_area


@pytest.mark.parametrize("img_path, exp", [("imgs/4.png", [RectangleData(0, 1, 18, 22, '')]),
                                           ])
def test_get_rect_by_contours(img_path, exp):
    img = cv2.imread(img_path)
    resp = get_rect_by_contours(img)
    assert resp == exp


def test__get_lines():
    img = cv2.imread("../../imgs/4.png")
    resp = _get_lines(img)
    assert np.array_equal(resp, img * 0)


cnt1 = [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1]]  # 11
cnt2 = [[1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1],
        [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1], [1, 1]
        ]  # 20
cntStab = []
@pytest.mark.parametrize("outer_rect, inner_rets, exp",
                         [(RectangleData(10, 20, 30, 40, ''), [(RectangleData(0, 1, 18, 22, ''), cnt1),
                                                               (RectangleData(11, 21, 18, 22, ''), cnt2),
                                                               ], 166),
                          (RectangleData(10, 20, 30, 40, ''), [(RectangleData(11, 21, 18, 22, ''), cnt1),
                                                               (RectangleData(11, 21, 18, 22, ''), cnt2),
                                                               ], 258),
                          (RectangleData(10, 20, 30, 40, ''), [(RectangleData(11, 21, 18, 22, ''), cnt1),
                                                               (RectangleData(11, 21, 18, 60, ''), cnt2),
                                                               ], 91),
                          (RectangleData(10, 20, 30, 40, ''), [(RectangleData(11, 21, 60, 22, ''), cnt1),
                                                               (RectangleData(11, 21, 18, 60, ''), cnt2),
                                                               ], 0),
                          (RectangleData(10, 20, 30, 40, ''), [(RectangleData(500, 500, 18, 22, ''), cnt1),
                                                               (RectangleData(500, 500, 18, 22, ''), cnt2),
                                                               ], 0),
                          (RectangleData(10, 20, 30, 40, ''), [(RectangleData(11, 500, 18, 22, ''), cnt1),
                                                               (RectangleData(500, 21, 18, 22, ''), cnt2),
                                                               ], 0),
                          ])
def test__get_count_of_points_per_area(outer_rect, inner_rets, exp):
    count_of_points_per_area, count = _get_count_of_points_per_area(outer_rect, inner_rets)
    assert count_of_points_per_area == exp
