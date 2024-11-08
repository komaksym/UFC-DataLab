from paddleocr import PaddleOCR, draw_ocr


ocr = PaddleOCR() # need to run only once to download and load model into memory
img_path = '../datasets/scorecard_images_results/maki-pitolo-charles-byrd-ufc-250-scorecard.jpg'
result = ocr.ocr(img_path,rec=False)
for idx in range(len(result)):
    res = result[idx]
    for line in res:
        print(line)