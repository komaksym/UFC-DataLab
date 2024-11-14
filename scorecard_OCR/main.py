import re
from paddleocr import PaddleOCR
import os
import pdb
from tqdm import tqdm
from multiprocessing import Pool
import pandas as pd


red_fighter_name = []
blue_fighter_name = []
date = []
red_fighter_total_pts = []
blue_fighter_total_pts = []


def read_images(path):
    """Reads images in a folder and saves paths to each of the images.

    Args:
        path (str): Path to a folder the images are in.

    Returns:
        list[str]: Paths to each of the images.
    """
    images = [os.path.join(path, image) for image in os.listdir(path)[:200] if image.endswith('.jpg')]
    return images


def parse_image(image):
    # Initialize PaddleOCR instance here
    ocr_instance = PaddleOCR(use_angle_cls=False, lang='en')

    # Needed data
    temp_red_fighter_name = []
    temp_blue_fighter_name = []
    temp_date = []
    temp_red_fighter_total_pts = []
    temp_blue_fighter_total_pts = []

    # Ocr instance
    result = ocr_instance.ocr(image, cls=False)

    # Parsing
    for res in result:
        print(image)
        for jdx, item in enumerate(res):
            text = item[1][0]
            # Extracting fighter names
            if text.lower() == "vs.":
                temp_red_fighter_name.append(res[jdx-1][1][0])
                temp_blue_fighter_name.append(res[jdx+1][1][0])

            # Extracting the date of the fight
            elif re.findall(r"(\d+\/\d+\/\d+)", text):
                temp_date.append(*re.findall(r"(\d+\/\d+\/\d+)", text))

            # Parsing the total points
            elif sum(1 for w, t in zip(text.lower(), "total") if w != t) < 2 and 4 <= len(text) <= 5:
                total_points_red = res[jdx-1][1][0]
                total_points_blue = res[jdx+1][1][0]
                if total_points_red.lower() == "total" or total_points_blue.lower() == "total":
                    temp_red_fighter_total_pts.append("-")
                    temp_blue_fighter_total_pts.append("-")
                else:
                    temp_red_fighter_total_pts.append(total_points_red)
                    temp_blue_fighter_total_pts.append(total_points_blue)

    if len(temp_red_fighter_total_pts) != 3 or len(temp_blue_fighter_total_pts) != 3 \
            or len(temp_date) != 1 or len(temp_red_fighter_name) != 1 \
            or len(temp_blue_fighter_name) != 1:
        results = {
            "red_fighter_name": temp_red_fighter_name,
            "blue_fighter_name": temp_blue_fighter_name,
            "date": temp_date,
            "red_fighter_total_pts": temp_red_fighter_total_pts,
            "blue_fighter_total_pts": temp_blue_fighter_total_pts
        }
        print("\n\nOUTLIER:\n\n")
        print(f"\n\n{item[1][0]}\n\n")
        print(f"\n\n\n{results}\n\n\n")
        print(f"len(red_fighter_name): {len(temp_red_fighter_name)}")
        print(f"len(blue_fighter_name): {len(temp_blue_fighter_name)}")
        print(f"len(date): {len(temp_date)}")
        print(f"len(red_fighter_total_pts): {len(temp_red_fighter_total_pts)}")
        print(f"len(blue_fighter_total_pts): {len(temp_blue_fighter_total_pts)}")

    red_fighter_name.append(temp_red_fighter_name)
    blue_fighter_name.append(temp_blue_fighter_name)
    date.append(temp_date)
    red_fighter_total_pts.append(temp_red_fighter_total_pts)
    blue_fighter_total_pts.append(temp_blue_fighter_total_pts)

    return {"red_fighter_name": red_fighter_name,
            "blue_fighter_name": blue_fighter_name,
            "date": date,
            "red_fighter_total_pts": red_fighter_total_pts,
            "blue_fighter_total_pts": blue_fighter_total_pts}


def main():
    folder_path = 'datasets/scorecard_images_results/new_version/'
    images = read_images(folder_path)

    collected_results = []

    # Multiprocessing
    with Pool(8) as pool:
        for result in tqdm(pool.imap(parse_image, images), total=len(images), unit="image"):
            collected_results.append(result)

    results = {"red_fighter_name": [entry["red_fighter_name"][0][0] for entry in collected_results],
               "blue_fighter_name": [entry["blue_fighter_name"][0][0] for entry in collected_results],
               "date": [entry["date"][0][0] for entry in collected_results],
               "red_fighter_total_pts": [entry["red_fighter_total_pts"][0] for entry in collected_results],
               "blue_fighter_total_pts": [entry["blue_fighter_total_pts"][0] for entry in collected_results]}
     
    results_df = pd.DataFrame(results)
    print(results_df)

    results_df.to_csv("datasets/parsed_scorecards.csv", index=False)


if __name__ == "__main__":
    main()
