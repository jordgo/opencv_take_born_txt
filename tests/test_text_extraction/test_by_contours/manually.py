import cv2

from models.page_templates import BODY_WITH_LEFT_PAYLOAD
from saving.save_to_dir import saving
from text_extraction.by_contours import get_img_text_by_contours
from text_extraction.target_rectangles import get_rect_by_contours


#============================= manually =====================================
def test_get_img_text_by_contours_manually():
    img = cv2.imread("../../imgs/image.png")
    text_arr, html_str = get_img_text_by_contours(img,
                                                  # from_box_debug=2, to_box_debug=10, save_cropped_img_path_debug="imgs/result",
                                                  )
    output_folder_filename = '../../imgs/result'
    saving(output_folder_filename, "test_res", html_str, img, is_html=True)  #TODO COMMENT OUT
    assert True


def test_get_rect_by_contours_manually():
    img = cv2.imread("../../imgs/image.png")
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

    page_template = BODY_WITH_LEFT_PAYLOAD
    h, w, _ = img.shape
    print(h,w)
    header = page_template["header"]
    cv2.line(img, (0, header), (w, header), (255, 0, 0), 2)
    footer = page_template["footer"]
    cv2.line(img, (0, h - footer), (w, h - footer), (255, 0, 0), 2)
    right_border = page_template["right_border"]
    cv2.line(img, (right_border, 0), (right_border, h), (255, 0, 0), 2)
    left_border = page_template["left_border"]
    cv2.line(img, (w - left_border, 0), (w - left_border, h), (255, 0, 0), 2)
    body_left = page_template["body"]["left_side"]
    cv2.line(img, (body_left, 0), (body_left, h), (255, 0, 0), 2)

    cv2.namedWindow('Test', cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Test", 1700, 900)
    cv2.imshow("Test", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    assert True