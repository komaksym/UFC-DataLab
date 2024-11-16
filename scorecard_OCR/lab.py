import re
from paddleocr import PaddleOCR
import os
import pdb
from tqdm import tqdm
from multiprocessing import Pool
import pandas as pd


def read_images(path):
    """Reads images in a folder and saves paths to each of the images.

    Args:
        path (str): Path to a folder the images are in.

    Returns:
        list[str]: Paths to each of the images.
    """
    images = [os.path.join(path, image) for image in os.listdir(path) if image.endswith('.jpg')]
    return images[720], images[719], images[715], images[615], images[591], images[588], images[559]


def parse_image(image):
    # Initialize PaddleOCR instance here
    print(image)


def main():
    folder_path = 'datasets/scorecards/scraped_scorecards/scorecard_images_results/new_version/'
    images = read_images(folder_path)

    # Multiprocessing
    with Pool(8) as pool:
        for _ in tqdm(pool.imap(parse_image, images), total=len(images), unit="image"):
            pass


if __name__ == "__main__":
    main()
