import re
from paddleocr import PaddleOCR
import os
import pdb
from tqdm import tqdm
from multiprocessing import Pool
import pandas as pd


count = 2


def read_images(path):
    """Reads images in a folder and saves paths to each of the images.

    Args:
        path (str): Path to a folder the images are in.

    Returns:
        list[str]: Paths to each of the images.
    """
    images = [os.path.join(path, image) for image in os.listdir(path) if image.endswith('.jpg')]
    
    return images


def parse_image(image):
    # Initialize PaddleOCR instance here
    ocr_instance = PaddleOCR(use_angle_cls=False, lang='en')

    # Needed data
    red_fighter_name = "-"
    blue_fighter_name = "-"
    date = "-"
    red_fighter_total_pts = []
    blue_fighter_total_pts = []

    # Ocr instance
    result = ocr_instance.ocr(image, cls=False)

    # Parsing
    for res in result:
        print(image)
        for jdx, item in enumerate(res):
            text = item[1][0]
            # Extracting fighter names
            if text.lower() == "vs.":
                red_fighter_name = res[jdx-1][1][0]
                blue_fighter_name = res[jdx+1][1][0]

            # Extracting the date of the fight
            elif re.findall(r"(\d+\/\d+\/\d+)", text):
                date = re.findall(r"(\d+\/\d+\/\d+)", text)[0]

            # Parsing the total points
            elif sum(1 for w, t in zip(text.lower(), "total") if w != t) < 2 and 4 <= len(text) <= 5:
                total_points_red = res[jdx-1][1][0]
                total_points_blue = res[jdx+1][1][0]
                if total_points_red.lower() == "total" or total_points_blue.lower() == "total":
                    red_fighter_total_pts.append("-")
                    blue_fighter_total_pts.append("-")
                else:
                    red_fighter_total_pts.append(total_points_red)
                    blue_fighter_total_pts.append(total_points_blue)

    if len(red_fighter_total_pts) != 3 or len(blue_fighter_total_pts) != 3 or red_fighter_name == "-" or blue_fighter_name == "-":
        print(f"\nImage: {image}\n")
        results = {
            "red_fighter_name": red_fighter_name,
            "blue_fighter_name": blue_fighter_name,
            "date": date,
            "red_fighter_total_pts": red_fighter_total_pts,
            "blue_fighter_total_pts": blue_fighter_total_pts
        }
        print("\nOUTLIER:\n")
        print(f"\n{text}\n")
        print(f"\n{results}\n")
        print(f"len(red_fighter_total_pts): {len(red_fighter_total_pts)}")
        print(f"len(blue_fighter_total_pts): {len(blue_fighter_total_pts)}\n")

    return [red_fighter_name,
            blue_fighter_name,
            date,
            red_fighter_total_pts,
            blue_fighter_total_pts]


def main():
    folder_path = 'datasets/scorecards/scraped_scorecards/scorecard_images_results/new_version/'
    images = read_images(folder_path)

    collected_results = []

    # Multiprocessing
    with Pool(8) as pool:
        for pos, result in enumerate(tqdm(pool.imap(parse_image, images), total=len(images), unit="image"), start=2):
            print(f"\n\nPosition: {pos}\n\n")
            collected_results.append(result)
 
    results = {"red_fighter_name": [data_point[0] for data_point in collected_results],
               "blue_fighter_name": [data_point[1] for data_point in collected_results],
               "date": [data_point[2] for data_point in collected_results],
               "red_fighter_total_pts": [data_point[3] for data_point in collected_results],
               "blue_fighter_total_pts": [data_point[4] for data_point in collected_results]}
     
    results_df = pd.DataFrame(results)
    print(results_df)

    results_df.to_csv("datasets/scorecards/OCR_parsed_scorecards/parsed_scorecards_new_version", index=False)


if __name__ == "__main__":
    main()
