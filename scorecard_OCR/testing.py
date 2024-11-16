from paddleocr import PaddleOCR


ocr_instance = PaddleOCR(use_angle_cls=False, lang='en')
file_path = "datasets/scorecard_images_results/new_version/317.jpg"
result = ocr_instance.ocr(file_path, cls=False)

for res in result:
    for r in res:
        print(r)