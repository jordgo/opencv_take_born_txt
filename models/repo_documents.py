import dataclasses
from dataclasses import dataclass
from typing import List

from models.report_data import ReportData


@dataclass
class ImgTextsDocument(ReportData):
    video_name: str
    frame_time: str
    header: list
    body: list
    frame_path: str
    created_time: str

    @property
    def to_dict(self):
        return dataclasses.asdict(self)

    @staticmethod
    def empty():
        return ImgTextsDocument('', '', [], [], '', '')

    @property
    def is_empty(self) -> bool:
        return self == self.empty()

    @property
    def get_data_as_key_value(self):
        key_value = {}
        for shape in self.body:
            for shape_line in shape:
                key = shape_line['key']['text']
                value = shape_line['value']['text']
                key_value[key] = value
        return key_value


    @property
    def get_data_as_key_value_str(self):
        key_value = []
        for shape in self.body:
            for shape_line in shape:
                key = shape_line['key']['text']
                value = shape_line['value']['text']
                key_value.append(f'{key}: {value}')
        return '\n'.join(key_value)

    # @property
    # def get_data(self) -> dict:
    #     data = {
    #         "header": self.header,
    #         "body": self.body
    #     }
    #     return data


@dataclass
class ImgTextsDocumentWithPath(ReportData):
    data: List[ImgTextsDocument]
    path: str

    def __iter__(self):
        return iter(dataclasses.astuple(self))