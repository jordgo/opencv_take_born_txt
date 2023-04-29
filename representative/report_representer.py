import abc

import models.report_response as r_resp


class ReportRepresenter(abc.ABC):
    pass
    # @abc.abstractmethod
    # def generate(self) -> r_resp.ReportResponse:
    #     return NotImplemented


class HTMLReportRepresenter(ReportRepresenter):
    @abc.abstractmethod
    def generate(self) -> r_resp.ReportResponse:
        return NotImplemented


class PDFReportRepresenter(ReportRepresenter):
    @abc.abstractmethod
    def generate(self) -> r_resp.ReportResponse:
        return NotImplemented


class EXCELReportRepresenter(ReportRepresenter):
    @abc.abstractmethod
    def generate(self) -> r_resp.ReportResponse:
        return NotImplemented