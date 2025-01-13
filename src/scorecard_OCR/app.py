import re
import logging
from typing import List, Optional
from dataclasses import dataclass
from pathlib import Path
import pandas as pd
from paddleocr import PaddleOCR
from tqdm import tqdm
from multiprocessing import Pool
from src.scorecard_OCR.config import PathConfig
from dataclasses import field


# CONSTANTS
DEFAULT_NUM_WORKERS = 8


@dataclass
class FightData:
    """Data class to store fight information."""
    red_fighter_name: str = "-"
    blue_fighter_name: str = "-"
    date: str = "-"
    red_fighter_total_pts: List[str] = field(default_factory=list)
    blue_fighter_total_pts: List[str] = field(default_factory=list)

    def to_list(self) -> List:
        """Convert the data class to a list format."""
        return [
            self.red_fighter_name,
            self.blue_fighter_name,
            self.date,
            self.red_fighter_total_pts,
            self.blue_fighter_total_pts
        ]
    
    def validate(self) -> bool:
        """Validate fight data"""
        try:
            # Basic validation rules
            if len(self.red_fighter_total_pts) != 3 or len(self.blue_fighter_total_pts) != 3:
                return False
            if self.red_fighter_name == "-" or self.blue_fighter_name == "-":
                return False
            if not all(p.isdigit() or p == "-" for p in self.red_fighter_total_pts + self.blue_fighter_total_pts):
                return False
            return True
        
        except Exception as e:
            logging.error(f"Validation failed: {str(e)}")
            return False


def parse_image(image_path: str) -> FightData:
    """Parsing the image."""
    try:
        # Defining ocr engine object
        ocr = PaddleOCR(use_angle_cls=False, lang='en')
        result = ocr.ocr(image_path, cls=False)

        # Fight data object
        fight_data = FightData()

        if not result:
            raise ValueError(f"No OCR results for image: {image_path}")

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
                    
        if not fight_data.validate():
            raise ValueError("Fight data validation failed.")

        return fight_data

    except Exception as e:
        raise ValueError(f"Error processing {image_path}: {str(e)}")


def read_images(folder_path: Path) -> List[str]:
    """Read image paths from a folder."""
    return [str(file) for file in folder_path.glob("*.jpg")][:5]


def extract_date(text: str) -> Optional[str]:
    """Extract date from text using regex."""
    date_match = re.findall(r"(\d+\/\d+\/\d+)", text)
    return date_match[0] if date_match else None


def is_total_text(text: str) -> bool:
    """Check if text represents 'total'."""
    return sum(1 for w, t in zip(text.lower(), "total") 
               if w != t) < 2 and 4 <= len(text) <= 5


def save_results(collected_results: List[FightData],
                 save_path: Path) -> pd.DataFrame:
    """Create a container where the results will be stored
       and specify the Path"""
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

    # Path, output directory, save
    output_path = Path(save_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    results_df.to_csv(output_path, index=False)
    logging.info(f"Results saved to {output_path}")

    return results_df


def process_scorecards(input_path: Path, output_path: Path, 
                       num_workers: int = DEFAULT_NUM_WORKERS) -> pd.DataFrame:
    """Main function to process scorecard images."""
    try:
        try:
            images = read_images(input_path)
            print(images)
            logging.info(f"Found {len(images)} images to process")

        except Exception:
            raise ValueError(f"Error reading images at {input_path}")

        collected_results = []
        
        with Pool(num_workers) as pool:
            for result in tqdm(pool.imap(parse_image, images), 
                               total=len(images), desc="Processing images"):

                # Process results as they complete
                collected_results.append(result)
                
        # Saving results
        return save_results(collected_results, output_path)

    except Exception as e:
        logging.error(f"Error in main processing: {str(e)}")
        raise


if __name__ == "__main__":
    try:
        path_config: PathConfig = PathConfig()
        path_config.validate_paths()
        process_scorecards(path_config.INPUT_PATH, path_config.OUTPUT_PATH)

    except Exception as e:
        logging.error(f"Application failed: {e}")
