import abc
from typing import List, Dict, Optional

from models.data_classes import PageSection, RectangleData
import models.page_payload as page_payload


class BasePageType:
    header_h_pct = 0.11
    footer_h_pct = 0.11
    right_border_w_pct = 0.05
    left_border_w_pct = 0.05

    header_payload: Optional[page_payload.RestPayload] = None
    footer_payload: Optional[page_payload.RestPayload] = None
    body_payload: Optional[page_payload.RestPayload] = None
    body_left_side_payload: Optional[page_payload.TablePayload] = None

    def set_base_sections(self, w_screen: int, h_screen: int) -> None:
        header_h = int(self.header_h_pct * h_screen)
        footer_h = int(self.footer_h_pct * h_screen)
        right_border_w  = int(self.right_border_w_pct * w_screen)
        left_border_w  = int(self.left_border_w_pct * w_screen)
        self.header_section = PageSection(left_border_w, 0, w_screen - left_border_w - right_border_w, header_h)
        self.footer_section = PageSection(left_border_w, h_screen - footer_h, w_screen - left_border_w - right_border_w, footer_h)
        self.right_border_section = PageSection(0, 0, right_border_w, h_screen)
        self.left_border_section = PageSection(w_screen - left_border_w, 0, left_border_w, h_screen)
        self.body_section = PageSection(left_border_w,
                                        header_h,
                                        w_screen - left_border_w - right_border_w,
                                        h_screen - header_h - footer_h,
                                        )

    def create_header_payload(self, rectangles: List[RectangleData]) -> Optional[page_payload.RestPayload]:
        if not self.header_payload:
            header_payload = page_payload.RestPayload(self.header_section, rectangles)
            if header_payload:
                self.header_payload = header_payload
                return header_payload
            else:
                return None
        else:
            return self.header_payload

    def create_footer_payload(self, rectangles: List[RectangleData]) -> Optional[page_payload.RestPayload]:
        if not self.footer_payload:
            footer_payload = page_payload.RestPayload(self.footer_section, rectangles)
            if footer_payload:
                self.footer_payload = footer_payload
                return footer_payload
            else:
                return None
        else:
            return self.footer_payload

    def create_body_payload(self, rectangles: List[RectangleData]) -> Optional[page_payload.RestPayload]:
        if not self.body_payload:
            body_payload = page_payload.RestPayload(self.body_section, rectangles)
            self.body_payload = body_payload
            return body_payload.payload
        else:
            return self.body_payload

    def create_body_left_side_payload(self, rectangles: List[RectangleData]) -> Optional[page_payload.RestPayload]:
        return None

    def get_header_rectangles(self, rectangles: List[RectangleData]) -> List[RectangleData]:
        return [r for r in rectangles if r in self.header_section]

    def get_footer_rectangles(self, rectangles: List[RectangleData]) -> List[RectangleData]:
        return [r for r in rectangles if r in self.footer_section]

    def get_body_left_side_rectangles(self, rectangles: List[RectangleData]) -> List[RectangleData]:
        return []


class BodyWithLeftPayload(BasePageType):
    def __init__(self, w_screen: int, h_screen: int):
        self.set_base_sections(w_screen, h_screen)
        body_left_side_w = int(self.body_section.w * 0.3)
        self.body_left_side_section = PageSection(self.body_section.x,
                                                  self.body_section.y,
                                                  body_left_side_w,
                                                  self.body_section.h,
                                                  )
        self.body_right_side_section = PageSection(self.body_left_side_section.x + self.body_left_side_section.w,
                                                   self.body_section.y,
                                                   self.body_section.w - self.body_left_side_section.w,
                                                   self.body_section.h
                                                   )

    def create_body_left_side_payload(self, rectangles: List[RectangleData]) -> Optional[page_payload.TablePayload]:
        body_left_side_payload = page_payload.TablePayload(self.body_left_side_section, rectangles)
        self.body_left_side_payload = body_left_side_payload
        return body_left_side_payload.payload

    def get_body_left_side_rectangles(self, rectangles: List[RectangleData]) -> List[RectangleData]:
        return [r for r in rectangles if r in self.body_left_side_section]


class BodyWithoutPayload(BasePageType):
    body_payload: Optional[page_payload.RestPayload] = None

    def __init__(self, w_screen: int, h_screen: int):
        self.w_screen = w_screen
        self.h_screen = h_screen
        self.set_base_sections(w_screen, h_screen)


def get_page_type(w_screen: int, h_screen: int, boxes: [RectangleData]) -> BasePageType:
    maybe_with_left_payload = BodyWithLeftPayload(w_screen, h_screen)
    left_side_rectangles = maybe_with_left_payload.create_body_left_side_payload(boxes)
    if left_side_rectangles:
        return maybe_with_left_payload
    else:
        return BodyWithoutPayload(w_screen, h_screen)
