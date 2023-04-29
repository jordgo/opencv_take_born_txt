import weasyprint
from weasyprint.text.fonts import FontConfiguration

import representative.report_representer as r_representer
import models.report_response as r_resp


class FromHTMLImgTextsRepresnter(r_representer.PDFReportRepresenter):
    def __init__(self, html_data: str, path_to_save: str):
        self.html_data: str = html_data
        self.path_to_save = path_to_save

    def generate(self) -> r_resp.ReportResponse:
        font_config = FontConfiguration()
        css = weasyprint.CSS(string="""
                @page { size: A4; margin: 0cm }
            """, font_config=font_config)
        resp = weasyprint.HTML(string=self.html_data).write_pdf(target=self.path_to_save,
                                                                zoom=0.5,
                                                                stylesheets=[css],
                                                                font_config=font_config,
                                                                )
        return r_resp.ReportResponse(resp)
