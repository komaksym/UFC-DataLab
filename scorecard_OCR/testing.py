import re
from paddleocr import PaddleOCR
import os 
import pdb
import re


def parse_image(image):

    # Needed data
    red_fighter_name = []
    blue_fighter_name = []
    date = []
    red_fighter_total_pts = []
    blue_fighter_total_pts = []

    result = ocr.ocr(image, cls=True)

    # Parsing
    for idx in range(len(result)):
        print(image)
        res = result[idx]
        for jdx in range(len(res)):
            # Extracting fighter names
            if res[jdx][1][0].lower() == "vs.":
                red_fighter_name.append(res[jdx-1][1][0])
                blue_fighter_name.append(res[jdx+1][1][0])
                
            # Extracting the data of the fight
            elif re.findall(r"(\d+\/\d+\/\d+)", res[jdx][1][0]):
                date.append(*re.findall(r"(\d+\/\d+\/\d+)", res[jdx][1][0]))

            
            # Parsing the total points
            elif sum(1 for w, t in zip(res[jdx][1][0].lower(), "total") if w != t) < 2 and len(res[jdx][1][0]) <= 5 and len(res[jdx][1][0]) >= 4:
                print(f"\n\n{res[jdx][1][0].lower()}\n\n")
                total_points_red = res[jdx-1][1][0]
                total_points_blue = res[jdx+1][1][0]
                
                if total_points_red.lower() == "total" or total_points_blue.lower() == "total":
                    red_fighter_total_pts.append("-")
                    blue_fighter_total_pts.append("-")

                else:
                    red_fighter_total_pts.append(total_points_red)
                    blue_fighter_total_pts.append(total_points_blue)

            print(res[jdx])

    if len(red_fighter_total_pts) != 3 or len(blue_fighter_total_pts) != 3 or len(date) != 1 or len(red_fighter_name) != 1 or len(blue_fighter_name) != 1:
        results = {"red_fighter_name": red_fighter_name, "blue_fighter_name": blue_fighter_name,
                   "date": date, "red_fighter_total_pts": red_fighter_total_pts,
                   "blue_fighter_total_pts": blue_fighter_total_pts
                   }

        # Print the results
        print(f"\n\n\n{results}\n\n\n")

        # Print lengths of data lists
        print(f"len(red_fighter_name): {len(red_fighter_name)}")
        print(f"len(blue_fighter_name): {len(blue_fighter_name)}")
        print(f"len(date): {len(date)}")
        print(f"len(red_fighter_total_pts): {len(red_fighter_total_pts)}")
        print(f"len(blue_fighter_total_pts): {len(blue_fighter_total_pts)}")

        print(hi)


ocr = PaddleOCR(use_angle_cls=True, lang='en')
folder_path = 'datasets/scorecard_images_results/new_version/1421.jpg'
images = parse_image(folder_path)
