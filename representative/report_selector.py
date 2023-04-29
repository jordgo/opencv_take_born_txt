import abc
import enum

import models.report_data as r_data
import models.report_response as r_resp
import representative.html.html_representer_selector as html_selector
import representative.pdf.pdf_representer_selector as pdf_selector
import representative.excel.excel_representer_selector as excel_selector


class ReportType(enum.Enum):
    HTML = 1
    PDF = 2
    EXCEL = 3


class Report(abc.ABC):
    @abc.abstractmethod
    def create_report(self, data: r_data.ReportData) -> r_resp.ReportResponse:
        return NotImplemented


class HTMLReport(Report):
    def create_report(self, data: r_data.ReportData) -> r_resp.ReportResponse:
        return html_selector.select_representer(data).generate()


class PDFReport(Report):
    def create_report(self, data: r_data.ReportData) -> r_resp.ReportResponse:
        return pdf_selector.select_representer(data).generate()


class EXCELReport(Report):
    def create_report(self, data: r_data.ReportData) -> r_resp.ReportResponse:
        return excel_selector.select_representer(data).generate()



def create_report(report_type: ReportType, data: r_data.ReportData) -> r_resp.ReportResponse:
    if report_type == ReportType.HTML:
        return HTMLReport().create_report(data)
    elif report_type == ReportType.PDF:
        return PDFReport().create_report(data)
    elif report_type == ReportType.EXCEL:
        return EXCELReport().create_report(data)
    else:
        raise NotImplementedError(f"Failed to create report <{report_type}>")