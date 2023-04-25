from dataclasses import dataclass, astuple, asdict
from pydantic import BaseModel
from dataclasses_json import dataclass_json

import numpy as np


@dataclass(frozen=True)
class TesseractResp:
    text: str
    conf: float
    resize_coeff: int
    frame: np.ndarray

    def __iter__(self):
        return iter(astuple(self))

@dataclass_json
@dataclass
class RectangleData:
    x: int
    y: int
    w: int
    h: int
    text: str

    def to_dict(self) -> dict:
        return asdict(self)

    def __iter__(self):
        return iter(astuple(self))

    def __contains__(self, rectangle_data) -> bool:
        ix, iy, iw, ih, _ = rectangle_data
        return ix > self.x and iy > self.y and iw < self.w and ih < self.h and ix + iw < self.x + self.w and iy + ih < self.y + self.h

    def __hash__(self):
        return hash((self.x, self.y))

    @staticmethod
    def empty():
        return RectangleData(0, 0, 0, 0, '')


@dataclass(frozen=True)
class PageSection:
    x: int
    y: int
    w: int
    h: int

    def __iter__(self):
        return iter(astuple(self))

    def __contains__(self, rectangle_data: RectangleData) -> bool:
        ix, iy, iw, ih, _ = rectangle_data
        return ix > self.x and iy > self.y and iw < self.w and ih < self.h and ix + iw < self.x + self.w and iy + ih < self.y + self.h

    @staticmethod
    def empty():
        return PageSection(0, 0, 0, 0)


@dataclass(frozen=True)
class ShapeLine:
    key: RectangleData
    value: RectangleData