
import pdf2image
import sys

pdf_path = sys.argv[1]

images = pdf2image.convert_from_path(pdf_path)

for idx, img in enumerate(images):
    img.save(str(idx)+'.bmp')