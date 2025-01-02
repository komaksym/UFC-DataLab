from pathlib import Path
from typing import Final


class PathConfig:
    """Configuration settings for UFC scorecard OCR."""
    PROJECT_ROOT: Final[Path] = Path(__file__).resolve().parent

    INPUT_PATH: Final[Path] = PROJECT_ROOT / 'mock_scorecard/'
    OUTPUT_PATH: Final[Path] = PROJECT_ROOT / 'mock_scorecard/mock_parsed_scorecard.csv'

    # Validate paths exist
    def validate_paths(self):
        if not self.INPUT_PATH.exists():
            raise ValueError(f"Input path does not exist: {self.INPUT_PATH}")
        self.OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
        