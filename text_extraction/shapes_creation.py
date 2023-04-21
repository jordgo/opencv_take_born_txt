import cv2
import numpy as np

from models.data_classes import RectangleData


MORPH_KERNEL_SIZE = 10
THRESHOLD_CONTOURS_POINTS = 1000


def _get_lines(gray: np.ndarray) -> np.ndarray:
    """getting the lines of a drawing for later deletion"""
    blur_gray = cv2.GaussianBlur(gray, (5, 5), 0)
    # io.imagesc(blur_gray)
    edges = cv2.Canny((blur_gray * 255).astype(np.uint8), 10, 200, apertureSize=5)
    rho = 1  # distance resolution in pixels of the Hough grid
    theta = np.pi / 180  # angular resolution in radians of the Hough grid
    threshold = 15  # minimum number of votes (intersections in Hough grid cell)
    min_line_length = 100  # minimum number of pixels making up a line
    max_line_gap = 3  # maximum gap in pixels between connectable line segments
    line_image = np.copy(gray) * 0  # creating a blank to draw lines on

    # Run Hough on edge detected image
    # Output "lines" is an array containing endpoints of detected line segments
    lines = cv2.HoughLinesP(edges, rho, theta, threshold, np.array([]),
                            min_line_length, max_line_gap)

    lines = lines if (lines is not None) and lines.size != 0 else []
    for line in lines:
        for x1, y1, x2, y2 in line:
            cv2.line(line_image, (x1, y1), (x2, y2), (255, 255, 255), 5)

    return line_image


def _is_black_bg(gray: np.ndarray) -> bool:
    """
    define dark or light background
    :param gray: np.ndarray
    :return: bool - True if is black
    """
    h, w = gray.shape
    cropped = gray[0:int(h * 0.1), 0:int(w * 0.1)]
    f_gray = cropped.flatten()
    c_count = {"0": 0, "255": 0}
    for i in range(len(f_gray)):
        if f_gray[i] > 127:
            c_count["255"] += 1
        else:
            c_count["0"] += 1
    return c_count["0"] > c_count["255"]


def _get_boxes_cnt(contours: [[int, int]]) -> [(RectangleData, [[int, int]])]:
    rect_with_cnt = []
    for cnt in contours:
        x, y, w, h = cv2.boundingRect(cnt)
        r = RectangleData(x=x, y=y, w=w, h=h, text='')
        rect_with_cnt.append((r, cnt))
    return rect_with_cnt


def _get_count_of_points_per_area(outer_rect: RectangleData,
                                  inner_rect_cnt: [(RectangleData, [[int, int]])],
                                  ) -> (int, int):
    """
    determines the number of contour points per area of the word
    :param outer_rect: RectangleData - outer rectangle containing the whole word
    :param inner_rect_cnt: [(RectangleData, [[int, int]])] - inner rectangles with letters
    :return: (int, int) - number of contour points per unit area of the outer rectangle - number of inner-boxes DEBUGONLY
    """
    x, y, w, h, _ = outer_rect

    inner_cnt_sizes = []
    for rect, cnt in inner_rect_cnt:
        ix, iy, iw, ih, _ = rect
        if ix > x and iy > y and iw < w and ih < h and ix + iw < x + w and iy + ih < y + h:
            inner_cnt_sizes.append(len(cnt))

    count_of_points_per_area = sum(inner_cnt_sizes) / (w * h)
    return int(count_of_points_per_area * 10000), len(inner_cnt_sizes)


def get_rect_by_contours(orig_img: np.ndarray, is_debug: bool = False) -> [RectangleData]:
    """
    getting rectangles containing text contours
    :param orig_img: original image
    :param is_debug: bool - DEBUG ONLY
    :return:list[RectangleData] - without text
    """
    gray = cv2.cvtColor(orig_img, cv2.COLOR_BGR2GRAY)
    is_black_bg = _is_black_bg(gray)
    bg_color = [0, 0, 0] if is_black_bg else [255, 255, 255]

    thresh_binary_param = cv2.THRESH_BINARY if is_black_bg else cv2.THRESH_BINARY_INV
    ret, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | thresh_binary_param)

    lines_img = _get_lines(gray)
    np.place(thresh, lines_img, bg_color)

    morph_kernel = np.ones((MORPH_KERNEL_SIZE, MORPH_KERNEL_SIZE))
    dilate_img = cv2.dilate(thresh, kernel=morph_kernel, iterations=1)

    contours_origin, _ = cv2.findContours(thresh, cv2.RETR_LIST, cv2.CHAIN_APPROX_NONE)
    contours_origin_external, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # cv2.drawContours(orig_img, contours_origin, -1, (0, 255, 0), 1)
    # cv2.namedWindow('Test', cv2.WINDOW_NORMAL)
    # cv2.resizeWindow("Test", 1700, 900)
    # cv2.imshow("Test", orig_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()

    contours_with_dilate, _ = cv2.findContours(dilate_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    orig_boxes_with_cnt: [(RectangleData, [[int, int]])] = _get_boxes_cnt(contours_origin)
    orig_boxes_with_cnt_external: [(RectangleData, [[int, int]])] = _get_boxes_cnt(contours_origin_external)
    boxes_with_cnt: [(RectangleData, [[int, int]])] = _get_boxes_cnt(contours_with_dilate)

    rect_possibly_contains_text = []
    for bc in boxes_with_cnt:
        box, cnt = bc
        count_of_points_per_area, count_boxes = _get_count_of_points_per_area(box, orig_boxes_with_cnt)
        if count_of_points_per_area < 700: #THRESHOLD_CONTOURS_POINTS:
            continue
        if is_debug:
            rect_possibly_contains_text.append((box, (count_of_points_per_area, count_boxes)))  # DEBUG ONLY
        else:
            rect_possibly_contains_text.append(box)

    return rect_possibly_contains_text
