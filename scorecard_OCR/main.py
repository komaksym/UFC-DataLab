from paddleocr import PaddleOCR
import os 
import pdb
import re


# Needed data
red_fighter_name = []
blue_fighter_name = []
date = []
red_fighter_total_pts = []
blue_fighter_total_pts = []


def read_images(path):
    """_reads images in a folder and saves paths to each of the images_

    Args:
        path (_str_): _path to a folder the images are in_

    Returns:
        _list[str]_: _paths to each of the images_
    """
    images = []

    for image in os.listdir(path)[:20]:
        if image.endswith('.jpg'):
            images.append(path+image)
    return images


ocr = PaddleOCR(use_angle_cls=True, lang='en')
folder_path = 'datasets/scorecard_images_results/new_version/'
images = read_images(folder_path)

for image in images:
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
                date.append(re.findall(r"(\d+\/\d+\/\d+)", res[jdx][1][0]))
            # Parsing the total points

            elif res[jdx][1][0].lower() == "total":
                total_points_red = res[jdx-1][1][0]
                total_points_blue = res[jdx+1][1][0]
                # Checking if there are total points (the fight might've ended in the first round)
                if all(char.isdigit() for char in total_points_red):
                    red_fighter_total_pts.append(total_points_red)
                if all(char.isdigit() for char in total_points_blue):
                    blue_fighter_total_pts.append(total_points_blue)
                # If no total points
                else:
                    red_fighter_total_pts.append("-")
                    blue_fighter_total_pts.append("-")
            print(res[jdx])
            
results = {"red_fighter_name": red_fighter_name, "blue_fighter_name": blue_fighter_name,
           "date": date, "red_fighter_total_pts": red_fighter_total_pts,
           "blue_fighter_total_pts": blue_fighter_total_pts
           }

print(results)

print(f"len(red_fighter_name): {len(red_fighter_name)}")
print(f"len(blue_fighter_name): {len(blue_fighter_name)}")
print(f"len(date): {len(date)}")
print(f"len(red_fighter_total_pts): {len(red_fighter_total_pts)}")
print(f"len(blue_fighter_total_pts): {len(blue_fighter_total_pts)}")