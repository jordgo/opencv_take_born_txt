import subprocess

import bs4
import cv2
from pytesseract import pytesseract


SPACE_WIDTH_PX = 10


def _spaces(current_x: int, prev_offset: int = 0) -> str:
    offset = current_x - prev_offset
    n_spaces = offset if SPACE_WIDTH_PX == 0 else int(offset / SPACE_WIDTH_PX)
    # print("offset", current_x, prev_offset, offset)
    return "".join(" " for _ in range(n_spaces))


def _parse_hocr(hocr) -> list:
    hocr.encode(encoding="utf-8")
    soup = bs4.BeautifulSoup(hocr, features='xml')
    ocr_lines = soup.findAll("span", {"class": "ocr_line"})
    lines_structure = []
    for line in ocr_lines:
        line_text = line.text.replace("\n", " ").strip()
        title = line['title']
        # The coordinates of the bounding box
        x1, y1, x2, y2 = map(int, title[5:title.find(";")].split())
        lines_structure.append({"x1": x1, "y1": y1, "x2": x2, "y2": y2, "text": line_text})
    return lines_structure


def _get_text(lines_structure: list):
    text = ""
    for l in lines_structure:
        spaces = _spaces(l["x1"])
        text = text + spaces + l["text"] + "\n"
    return text


def get_img_text(img):
    tesseract_path = subprocess.run(['which', 'tesseract'], stdout=subprocess.PIPE) \
        .stdout.decode('utf-8').replace('\n', '')

    pytesseract.tesseract_cmd = tesseract_path

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    ret, thresh1 = cv2.threshold(gray, 0, 255, cv2.THRESH_OTSU | cv2.THRESH_BINARY_INV)

    config = '-l eng --oem 1 --psm 3 hocr'
    hocr = pytesseract.run_and_get_output(thresh1, extension="hocr", lang="eng", config=config)

    lines_structure = _parse_hocr(hocr)
    text = _get_text(lines_structure)
    return text