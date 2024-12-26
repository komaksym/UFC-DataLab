import pdb
import re
import logging
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path
import pandas as pd
from paddleocr import PaddleOCR
from tqdm import tqdm
from multiprocessing import Pool


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('scorecard_parser.log', mode='w', encoding='utf-8'),
        logging.StreamHandler()
    ]
)


@dataclass
class FightData:
    """Data class to store fight information."""
    red_fighter_name: str = "-"
    blue_fighter_name: str = "-"
    date: str = "-"
    red_fighter_total_pts: List[str] = None
    blue_fighter_total_pts: List[str] = None

    def __post_init__(self):
        """Keep populating points lists if it's not a first run"""
        self.red_fighter_total_pts = [] if self.red_fighter_total_pts is None else self.red_fighter_total_pts
        self.blue_fighter_total_pts = [] if self.blue_fighter_total_pts is None else self.blue_fighter_total_pts

    def to_list(self) -> List:
        """Convert the data class to a list format."""
        return [
            self.red_fighter_name,
            self.blue_fighter_name,
            self.date,
            self.red_fighter_total_pts,
            self.blue_fighter_total_pts
        ]


def read_images(folder_path: Path) -> List[str]:
    """Read image paths from a folder."""
    path = Path(folder_path)
    if not path.exists():
        raise FileNotFoundError(f"Folder not found: {folder_path}")
                                
    return [str(file) for file in path.glob("*.jpg")]


def extract_date(text: str) -> Optional[str]:
    """Extract date from text using regex."""
    date_match = re.findall(r"(\d+\/\d+\/\d+)", text)
    return date_match[0] if date_match else None


def is_total_text(text: str) -> bool:
    """Check if text represents 'total'."""
    return sum(1 for w, t in zip(text.lower(), "total") 
               if w != t) < 2 and 4 <= len(text) <= 5


def parse_image(image_path: str) -> FightData:
    """Parse a single image and extract fight data."""
    try:
        # Initialize OCR inside the worker process
        ocr = PaddleOCR(use_angle_cls=False, lang='en')
       
        fight_data = FightData()
        result = ocr.ocr(image_path, cls=False)

        if not result:
            logging.warning(f"No OCR results for image: {image_path}")
            return fight_data

        for res in result:
            for idx, item in enumerate(res):
                text = item[1][0]
                # Extract fighter names
                if text.lower() == "vs.":
                    fight_data.red_fighter_name = res[idx-1][1][0]
                    fight_data.blue_fighter_name = res[idx+1][1][0]
               
                # Extract date
                elif date := extract_date(text):
                    fight_data.date = date
               
                # Extract total points
                elif is_total_text(text):
                    total_points_red = res[idx-1][1][0]
                    total_points_blue = res[idx+1][1][0]
                    
                    if total_points_red.lower() == "total" or total_points_blue.lower() == "total":
                        fight_data.red_fighter_total_pts.append("-")
                        fight_data.blue_fighter_total_pts.append("-")
                    else:
                        fight_data.red_fighter_total_pts.append(total_points_red)
                        fight_data.blue_fighter_total_pts.append(total_points_blue)
                    
        run_unit_tests(fight_data.red_fighter_total_pts, fight_data.blue_fighter_total_pts,
                       fight_data.red_fighter_name, fight_data.blue_fighter_name)

        return fight_data

    except Exception as e:
        logging.error(f"Error processing image {image_path}: {str(e)}")
        return FightData()


def test_points_length(red_fighter_total_pts, blue_fighter_total_pts):
    # Check if the fighter points are valid.
    assert (len(red_fighter_total_pts) == 3 and 
            len(blue_fighter_total_pts) == 3), ("Invalid total points length."
                                                        "Expected: len(red_fighter_total_pts) and \
                                                        len(blue_fighter_total_pts) == 3",
                                                        f"Got: {len(red_fighter_total_pts)}\n \
                                                        {len(blue_fighter_total_pts)}")


def test_names(red_fighter_name, blue_fighter_name):
    # Check if the fighter names are valid.
    assert (red_fighter_name != "-" and
            blue_fighter_name != "-")


def test_points_values(red_fighter_total_pts, blue_fighter_total_pts):
    # Unit testing red_fighter_total_pts.
    invalid_points_red = [f for f in red_fighter_total_pts if f != "-" and not f.isdigit()]
    assert not invalid_points_red, (
        "Invalid points format.", 
        "Expected: red_fighter_total_pts to be either an integer or '-'",
        f"Got: {invalid_points_red}")
        
    # Unit testing blue_fighter_total_pts
    invalid_points_blue = [f for f in blue_fighter_total_pts if f != "-" and not f.isdigit()]
    assert not invalid_points_blue, (
        "Invalid points format.",
        "Expected: blue_fighter_total_pts to be either an integer or '-'",
        f"Got: {invalid_points_blue}")


def run_unit_tests(red_fighter_total_pts, blue_fighter_total_pts,
                   red_fighter_name, blue_fighter_name):
    # Run unit tests.
    test_points_length(red_fighter_total_pts, blue_fighter_total_pts)
    test_points_values(red_fighter_total_pts, blue_fighter_total_pts)
    test_names(red_fighter_name, blue_fighter_name)


def process_scorecards(folder_path: Path, output_path: Path, num_workers: int = 8):
    """Main function to process scorecard images."""
    try:
        images = read_images(folder_path)
        logging.info(f"Found {len(images)} images to process")

        collected_results = []
        with Pool(num_workers) as pool:
            for result in tqdm(pool.imap(parse_image, images), 
                               total=len(images), 
                               desc="Processing images"):
                collected_results.append(result.to_list())

        # Create DataFrame
        results_df = pd.DataFrame(
            collected_results,
            columns=[
                "red_fighter_name",
                "blue_fighter_name",
                "date",
                "red_fighter_total_pts",
                "blue_fighter_total_pts"
            ]
        )

        # Save results
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        results_df.to_csv(output_path, index=False)
        logging.info(f"Results saved to {output_path}")

        return results_df

    except Exception as e:
        logging.error(f"Error in main processing: {str(e)}")
        raise


if __name__ == "__main__":
    FOLDER_PATH = Path(__file__).resolve().parents[2] / 'src/datasets/scorecards/scraped_scorecard_images/new_version_scorecards/'
    OUTPUT_PATH = Path(__file__).resolve().parents[2] / 'src/datasets/scorecards/OCR_parsed_scorecards/parsed_scorecards_new_version.csv'
    
    try:
        process_scorecards(FOLDER_PATH, OUTPUT_PATH)
    except Exception as e:
        logging.error(f"Error parsing I/O PATHs {FOLDER_PATH}, {OUTPUT_PATH}: {str(e)}")
