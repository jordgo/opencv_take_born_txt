import abc
import dataclasses

import models.data_classes as data_cls
from typing import List, Tuple, Dict


class PagePayload(abc.ABC):
    payload = []
    rectangles: List[data_cls.RectangleData] = []

    def get_text_arr(self) -> List[str]:
        return [r.text for r in self.rectangles]


class RestPayload(PagePayload):
    def __init__(self,
                 page_section: data_cls.PageSection,
                 rectangle_datas: List[data_cls.RectangleData]):
        rect_filtered = [r for r in rectangle_datas if r in page_section]
        self.rectangles = rect_filtered
        self.payload = [r.to_dict() for r in rect_filtered]


class TablePayload(PagePayload):
    def __init__(self, page_section: data_cls.PageSection, rectangle_datas: List[data_cls.RectangleData]):
        # self.tmp_payload = {}
        self.page_section: data_cls.PageSection = page_section
        rectangles_filtered = [r for r in rectangle_datas if r in page_section]
        self.rectangle_datas: List[data_cls.RectangleData] = rectangles_filtered
        self.rectangles = rectangles_filtered
        self._set_payload()

    def _get_key_and_value_boxes(self) -> Tuple[List[data_cls.RectangleData], List[data_cls.RectangleData]]:
        half_w_of_section = self.page_section.w / 2
        maybe_keys: List[data_cls.RectangleData] = [r for r in self.rectangle_datas if r.x < half_w_of_section]
        if maybe_keys:
            box_with_max_width: data_cls.RectangleData = max(maybe_keys, key=lambda r:r.w)
            divider = box_with_max_width.x + box_with_max_width.w

            def key_predicate(r: data_cls.RectangleData):
                return box_with_max_width.x <= r.x <= divider and r.w <= box_with_max_width.w

            key_boxes: List[data_cls.RectangleData] = [r for r in self.rectangle_datas if key_predicate(r)]
            value_boxes: List[data_cls.RectangleData] = [r for r in self.rectangle_datas if r.x > divider]
            return key_boxes, value_boxes
        else:
            return [], []

    @staticmethod
    def _create_common_payload_shape(key_boxes: List[data_cls.RectangleData],
                                     value_boxes: List[data_cls.RectangleData],
                                     ) -> Dict[data_cls.RectangleData, data_cls.RectangleData]:
        tmp_payload = {}
        prev_key = None
        prev_value = None
        sorted_key_boxes = sorted(key_boxes, key=lambda obj: obj.y)
        for k_box in sorted_key_boxes:
            bottom_line = k_box.y - k_box.h
            top_line = k_box.y + k_box.h

            v_box: data_cls.RectangleData = None
            for value in value_boxes:
                if bottom_line < value.y < top_line:
                    if not v_box:
                        v_box = value
                    else:
                        v_box = dataclasses.replace(v_box, w = v_box.w + value.w, text=f'{v_box.text} {value.text}')

            if v_box and v_box != prev_value:
                prev_key = k_box
                prev_value = v_box
                tmp_payload[k_box] = v_box
            elif v_box and v_box == prev_value:
                new_k_box = dataclasses.replace(prev_key, y=v_box.y, w=prev_key.w+k_box.w, text=f'{prev_key.text} {k_box.text}')
                tmp_payload.pop(prev_key)
                tmp_payload[new_k_box] = v_box
            else:
                continue
        return tmp_payload

    @staticmethod
    def _get_avg_spacing_btw_lines(lines_dict_ordered: Dict[data_cls.RectangleData, data_cls.RectangleData]) -> float:
        lines: List[data_cls.RectangleData] = list(lines_dict_ordered)
        lines_ordered = sorted(lines, key=lambda obj: obj.y)
        sum_spacing_btw_lines = 0
        len_tmp_payload = len(lines_dict_ordered)
        for i in range(len_tmp_payload):
            if i + 1 < len_tmp_payload:
                sum_spacing_btw_lines += lines_ordered[i + 1].y - lines_ordered[i].y

        avg_spacing_btw_lines = sum_spacing_btw_lines / (len_tmp_payload - 1)
        return avg_spacing_btw_lines

    @staticmethod
    def _split_into_shapes(tmp_payload: Dict[data_cls.RectangleData, data_cls.RectangleData],
                           avg_spacing_btw_lines: float
                           ) -> List[List[dict]]:
        # def _add_todict_as_dict(upd_dict: dict,
        #                         key: data_cls.RectangleData,
        #                         value: data_cls.RectangleData) -> Dict[dict, dict]:
        #     k = dataclasses.asdict(key)
        #     v = dataclasses.asdict(value)
        #     upd_dict[k] = v
        #     return upd_dict

        if tmp_payload:
            keys_ordered: List[data_cls.RectangleData] = sorted(tmp_payload, key=lambda obj:obj.y)
            y_spacing_threshold = avg_spacing_btw_lines #+ avg_spacing_btw_lines * 0.3
            shapes = []
            current_shape = []
            prev_y = 0
            for k in keys_ordered:
                v = tmp_payload[k]
                if not current_shape:
                    current_shape.append({"key": k.to_dict(), "value": v.to_dict()})
                elif k.y - prev_y > y_spacing_threshold:
                    shapes.append(current_shape)
                    current_shape = [{"key": k.to_dict(), "value": v.to_dict()}]
                else:
                    current_shape.append({"key": k.to_dict(), "value": v.to_dict()})
                prev_y = k.y

            shapes.append(current_shape)
            return shapes
        else:
            return []

    def _set_payload(self) -> None:
        key_boxes, value_boxes = self._get_key_and_value_boxes()
        if key_boxes and value_boxes:
            tmp_payload = self._create_common_payload_shape(key_boxes, value_boxes)
            avg_spacing_btw_lines = self._get_avg_spacing_btw_lines(tmp_payload)
            shapes = self._split_into_shapes(tmp_payload, avg_spacing_btw_lines)
            self.payload = shapes
