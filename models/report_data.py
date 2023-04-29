import abc
from dataclasses import dataclass


class ReportData(abc.ABC):
    pass


@dataclass
class StrReportData(ReportData):
    data: str
    path: str

