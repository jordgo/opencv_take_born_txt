import abc

import models.report_response as r_resp
import models.report_data as r_data
import models.repo_documents as repo_doc
import representative.html.html_img_texts_representer as img_texts_representer
import representative.report_representer as r_representer


def select_representer(data: r_data.ReportData) -> r_representer.HTMLReportRepresenter:
    if isinstance(data, repo_doc.ImgTextsDocument):
        return img_texts_representer.ImgTextsRepresnter(data)
    else:
        raise NotImplementedError(f"Report type <{type(data)}> not implemented")



