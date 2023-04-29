import representative.pdf.pdf_img_texts_representer as img_texts_representer
import representative.report_representer as r_representer
from models.report_data import StrReportData


def select_representer(html_data: StrReportData) -> r_representer.PDFReportRepresenter:
    return img_texts_representer.FromHTMLImgTextsRepresnter(html_data.data, html_data.path)



