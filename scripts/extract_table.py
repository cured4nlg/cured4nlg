
# Adapted from: https://www.opcito.com/blogs/extracting-text-from-images-with-tesseract-ocr-opencv-and-python

import csv
import cv2
import pytesseract
import sys

def to_grayscale(img):
    return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

def apply_thresholding(img):
    _, th_img = cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return th_img

def parse_text(th_img, lang='eng'):
    config = '--oem 3 --psm 6'

    data = pytesseract.image_to_data(th_img, config=config, lang=lang,
                                     output_type=pytesseract.Output.DICT)

    text = [item if item != '' else '\n' for item in data['text']]

    return ' '.join(text)

if __name__ == "__main__":
    img_path = sys.argv[1]

    img = cv2.imread(img_path)
    gs_img = to_grayscale(img)
    th_img = apply_thresholding(gs_img)

    text = parse_text(img)
    
    print(text)
