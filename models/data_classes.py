from dataclasses import dataclass, astuple

import numpy as np


@dataclass(frozen=True)
class TesseractResp:
    text: str
    conf: float
    resize_coeff: int
    frame: np.ndarray

    def __iter__(self):
        return iter(astuple(self))


@dataclass
class RectangleData:
    x: int
    y: int
    w: int
    h: int
    text: str

    def __iter__(self):
        return iter(astuple(self))