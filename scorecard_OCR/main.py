import pdb
from paddleocr import PaddleOCR, draw_ocr
#from PIL import Image
import pandas as pd


ocr = PaddleOCR(lang='en') # need to run only once to download and load model into memory
img_path = 'datasets/scorecard_images_results/1-UFC 270 Ngannou vs. Gane - Scorecards - Ngannou vs. Gane.jpg'
result = ocr.ocr(img_path, cls=False)

results = {}

for idx in range(len(result)):
    res = result[idx]
    for jdx in range(len(res)):
        if res[jdx][1][0] == 'VS.':
            results["red_fighter_name"] = res[jdx-1][1][0]
            results["blue_fighter_name"] = res[jdx+1][1][0]
            results["date"] = res[jdx+8][1][0]
            results["red_fighter_total_pts_judge_one"] = res[len(res)-19][1][0]
            results["blue_fighter_total_pts_judge_one"] = res[len(res)-17][1][0]
            results["red_fighter_total_pts_judge_two"] = res[len(res)-16][1][0]
            results["blue_fighter_total_pts_judge_two"] = res[len(res)-14][1][0]
            results["red_fighter_total_pts_judge_three"] = res[len(res)-13][1][0]
            results["blue_fighter_total_pts_judge_three"] = res[len(res)-11][1][0]
            results["result"] = res[len(res)-1][1][0]
        print(res[jdx])        

print(results)