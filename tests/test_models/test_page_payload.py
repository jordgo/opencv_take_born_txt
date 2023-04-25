import pytest

import models.data_classes as dt_cls
from models.page_payload import TablePayload


empty_rect = dt_cls.RectangleData.empty()
tmp_payload1 = {dt_cls.RectangleData(10, 20, 40, 10, ''): empty_rect,
                dt_cls.RectangleData(10, 30, 40, 10, ''): empty_rect,
                dt_cls.RectangleData(10, 40, 40, 10, ''): empty_rect,
                dt_cls.RectangleData(10, 50, 40, 10, ''): empty_rect,
                }
tmp_payload2 = {dt_cls.RectangleData(10, 40, 40, 10, ''): empty_rect,
                dt_cls.RectangleData(10, 20, 40, 10, ''): empty_rect,
                dt_cls.RectangleData(10, 30, 40, 10, ''): empty_rect,
                dt_cls.RectangleData(10, 50, 40, 10, ''): empty_rect,
                }
@pytest.mark.parametrize("tmp_payload, exp", [
    (tmp_payload1, 10),
    (tmp_payload2, 10),
    ({}, 0),
])
def test__get_avg_spacing_btw_lines(tmp_payload, exp):
    res = TablePayload._get_avg_spacing_btw_lines(tmp_payload)
    assert res == exp


tmp_payload1 = {dt_cls.RectangleData(10, 20, 40, 10, ''): empty_rect,
                dt_cls.RectangleData(10, 30, 40, 10, ''): empty_rect,
                dt_cls.RectangleData(10, 80, 40, 10, ''): empty_rect,
                dt_cls.RectangleData(10, 90, 40, 10, ''): empty_rect,
                }

tmp_payload2 = {dt_cls.RectangleData(10, 80, 40, 10, ''): empty_rect,
                dt_cls.RectangleData(10, 20, 40, 10, ''): empty_rect,
                dt_cls.RectangleData(10, 30, 40, 10, ''): empty_rect,
                dt_cls.RectangleData(10, 90, 40, 10, ''): empty_rect,
                }
exp1 = [{dt_cls.RectangleData(10, 20, 40, 10, ''): empty_rect,
        dt_cls.RectangleData(10, 30, 40, 10, ''): empty_rect,
        },
        {dt_cls.RectangleData(10, 80, 40, 10, ''): empty_rect,
         dt_cls.RectangleData(10, 90, 40, 10, ''): empty_rect,
        }]
exp2 = [{dt_cls.RectangleData(10, 20, 40, 10, ''): empty_rect,},
        {dt_cls.RectangleData(10, 30, 40, 10, ''): empty_rect,},
        {dt_cls.RectangleData(10, 80, 40, 10, ''): empty_rect,},
        {dt_cls.RectangleData(10, 90, 40, 10, ''): empty_rect,},
        ]
@pytest.mark.parametrize("tmp_payload, avg_spacing_btw_lines, exp", [
    (tmp_payload1, 10, exp1),
    (tmp_payload1, 0, exp2),
    (tmp_payload2, 10, exp1),
    ({}, 10, []),
    ({}, 0, []),
])
def test__split_into_shapes(tmp_payload, avg_spacing_btw_lines, exp):
    res = TablePayload._split_into_shapes(tmp_payload, avg_spacing_btw_lines)
    assert res == exp
