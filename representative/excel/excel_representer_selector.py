import representative.excel.excel_img_texts_representer as img_texts_representer
import representative.report_representer as r_representer
from models.repo_documents import ImgTextsDocumentWithPath


def select_representer(data: ImgTextsDocumentWithPath) -> r_representer.EXCELReportRepresenter:
    return img_texts_representer.FromHTMLImgTextsRepresnter(data)



