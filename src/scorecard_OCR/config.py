from pathlib import Path
from typing import Final


class PathConfig:
    """Configuration settings for UFC scorecard OCR."""
    PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parents[2]
    
    INPUT_PATH: Final[Path] = PROJECT_ROOT / 'src/datasets/scorecards/scraped_scorecard_images/new_version_scorecards/'
    OUTPUT_PATH: Final[Path] = PROJECT_ROOT / 'src/datasets/scorecards/OCR_parsed_scorecards/parsed_scorecards_new_version.csv'

    # Validate paths exist
    def validate_paths(self):
        if not self.INPUT_PATH.exists():
            raise ValueError(f"Input path does not exist: {self.INPUT_PATH}")
        self.OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)