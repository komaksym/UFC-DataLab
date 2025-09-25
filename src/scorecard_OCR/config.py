from pathlib import Path


class PathConfig:
    """Configuration settings for UFC scorecard OCR."""

    PROJECT_ROOT: Path = Path(__file__).resolve().parents[2]

    INPUT_PATH: Path = (
        PROJECT_ROOT / "data/scorecards/scraped_scorecard_images/new_version_scorecards_v1/"
    )
    OUTPUT_PATH: Path = (
        PROJECT_ROOT / "data/scorecards/OCR_parsed_scorecards/parsed_scorecards_new_version.csv"
    )

    def validate_paths(self) -> None:
        """Validate for path existence"""

        if not self.INPUT_PATH.exists():
            raise ValueError(f"Input path does not exist: {self.INPUT_PATH}")
        self.OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)