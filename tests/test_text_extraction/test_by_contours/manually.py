import cv2

from saving.save_to_dir import saving
from text_extraction.by_contours import get_img_text_by_contours
from text_extraction.shapes_creation import get_rect_by_contours


#============================= manually =====================================
def test_get_img_text_by_contours_manually():
    img = cv2.imread("imgs/image.png")
    text_arr, html_str = get_img_text_by_contours(img,
                                                  # from_box_debug=2, to_box_debug=10, save_cropped_img_path_debug="imgs/result",
                                                  )
    output_folder_filename = 'imgs/result'
    saving(output_folder_filename, "test_res", html_str, img, is_html=True)  #TODO COMMENT OUT
    assert True


def test_get_rect_by_contours_manually():
    img = cv2.imread("imgs/image.png")
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

    cv2.namedWindow('Test', cv2.WINDOW_NORMAL)
    cv2.resizeWindow("Test", 1700, 900)
    cv2.imshow("Test", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    assert True