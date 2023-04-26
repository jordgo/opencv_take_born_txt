import dataclasses
from dataclasses import dataclass


@dataclass
class ImgTextsDocument:
    video_name: str
    frame_time: str
    data: list
    frame_path: str
    created_time: str

    @property
    def to_dict(self):
        return dataclasses.asdict(self)

    @staticmethod
    def empty():
        return ImgTextsDocument('', '', [], '', '')

    @property
    def is_empty(self) -> bool:
        return self == self.empty()
