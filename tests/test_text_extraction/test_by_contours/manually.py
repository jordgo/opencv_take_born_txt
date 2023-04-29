from typing import List, Optional

import cv2

from definition import ROOT_DIR
from models.data_classes import RectangleData
from models.page_payload import PagePayload
from models.page_templates import BasePageType, get_page_type
from models.repo_documents import ImgTextsDocument, ImgTextsDocumentWithPath
from models.report_data import StrReportData
from saving.save_to_dir import saving, save_to_file
from text_extraction.by_contours import get_img_text_by_contours
from text_extraction.target_rectangles import get_rect_by_contours
from video_processing.image_handler import ImageHandler
import representative.report_selector as report_selector


#============================= manually =====================================

output_folder_filename = ROOT_DIR + '/tests/imgs/result'


def test_get_img_text_by_contours_manually(config):
    img = cv2.imread("../../imgs/html_space_issue.png")
    w, h, _ = img.shape
    all_rectangles: List[RectangleData] = get_rect_by_contours(img)
    page_type: BasePageType = get_page_type(w, h, all_rectangles, config)
    body_left_side_rectangles: List[RectangleData] = page_type.get_body_left_side_rectangles(all_rectangles)
    print(page_type, body_left_side_rectangles)
    rectangles = get_img_text_by_contours(img,
                                          body_left_side_rectangles,
                                                  # from_box_debug=2, to_box_debug=10,
                                          save_cropped_img_path_debug="imgs/result",
                                                  )
    print(rectangles)
    # saving(output_folder_filename, "test_res", html_str, img, is_html=True)  #TODO COMMENT OUT
    assert True


def test_get_rect_by_contours_manually():
    # img = cv2.imread("../../imgs/image.png")
    img = cv2.imread("../../imgs/html_space_issue.png")
    # img = cv2.imread("imgs/Thickness.png")
    rectangles = get_rect_by_contours(img, is_debug=True)
    for r_p in rectangles:
        r, (count_of_points_per_area, count_boxes) = r_p
        cv2.rectangle(img, (r.x, r.y), (r.x + r.w, r.y + r.h), (0, 255, 0), 2)
        count_text = str(count_of_points_per_area) + "-" + str(count_boxes)
        cv2.putText(img, count_text, (r.x-10, r.y-10),
                    fontFace=cv2.FONT_HERSHEY_COMPLEX,
                    fontScale=0.5,
                    color=(0, 255, 0),
                    thickness=1,
                    lineType=cv2.LINE_AA,
                    )
    #
    # page_template = BODY_WITH_LEFT_PAYLOAD
    # h, w, _ = img.shape
    # print(h,w)
    # header = page_template["header"]
    # cv2.line(img, (0, header), (w, header), (255, 0, 0), 2)
    # footer = page_template["footer"]
    # cv2.line(img, (0, h - footer), (w, h - footer), (255, 0, 0), 2)
    # right_border = page_template["right_border"]
    # cv2.line(img, (right_border, 0), (right_border, h), (255, 0, 0), 2)
    # left_border = page_template["left_border"]
    # cv2.line(img, (w - left_border, 0), (w - left_border, h), (255, 0, 0), 2)
    # body_left = page_template["body"]["left_side"]
    # cv2.line(img, (body_left, 0), (body_left, h), (255, 0, 0), 2)

    cv2.namedWindow('Test', cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Test", 1700, 900)
    cv2.imshow("Test", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    assert True

def test_get_reports(config):
    frame = cv2.imread(ROOT_DIR + "/tests/imgs/missed_pro_operaive_alingment.png")
    im_handler = ImageHandler(frame, "00:00:04", True, config)
    im_handler.process_img()

    header_payload_opt: Optional[PagePayload] = im_handler.page_type.header_payload
    header_payload = header_payload_opt if header_payload_opt else []
    body_left_side_payload_opt: Optional[PagePayload] = im_handler.page_type.body_left_side_payload
    body_left_side_payload = body_left_side_payload_opt if body_left_side_payload_opt else []

    doc = ImgTextsDocument("v_name", "00:00:01", header_payload.payload, body_left_side_payload.payload, "frame_path", "00")
    html_report = report_selector.create_report(report_selector.ReportType.HTML, doc).response
    html_report_path = output_folder_filename + f"/html_report_{doc.frame_time}.html"
    save_to_file(html_report_path, str(html_report), is_img=False)

    pdf_report_path = output_folder_filename + f"/pdf_report_{doc.frame_time}.pdf"
    saved = report_selector.create_report(report_selector.ReportType.PDF,
                                          StrReportData(str(html_report), pdf_report_path)).response

    excel_report_path = output_folder_filename + f"/excel_report.xlsx"
    saved = report_selector.create_report(report_selector.ReportType.EXCEL,
                                          ImgTextsDocumentWithPath([doc], excel_report_path)).response

    assert True