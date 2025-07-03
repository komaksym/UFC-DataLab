from pathlib import Path
from typing import List, Tuple

import pandas as pd
import pytest

from src.scorecard_OCR.ocr import (
    FightData,
    parse_image,
    process_scorecards,
    read_images,
)

from .config import PathConfig


class TestFightData:
    """Tests on FightData class."""

    def setup_method(self) -> None:
        """Initial setup for testing."""

        self.fight_data = FightData()

    @pytest.fixture
    def expected_init_data(self) -> FightData:
        return FightData(
            red_fighter_name="-",
            blue_fighter_name="-",
            date="-",
            red_fighter_total_pts=[],
            blue_fighter_total_pts=[],
        )

    def test_initialization(self, expected_init_data) -> None:
        assert expected_init_data == self.fight_data

    @pytest.fixture
    def expected_to_list_data(self) -> FightData:
        return FightData(
            red_fighter_name="-",
            blue_fighter_name="-",
            date="-",
            red_fighter_total_pts=[],
            blue_fighter_total_pts=[],
        )

    def test_to_list(self, expected_to_list_data) -> None:
        got = self.fight_data
        assert got == expected_to_list_data

    @pytest.fixture
    def mock_validation_data(self) -> FightData:
        """Mock data for validation testing"""

        return FightData(
            red_fighter_name="BRYAN BARBERENA",
            blue_fighter_name="DARIAN WEEKS",
            date="12/04/2021",
            red_fighter_total_pts=["29", "29", "29"],
            blue_fighter_total_pts=["28", "28", "28"],
        )

    def test_validation(self, mock_validation_data) -> None:
        """Testing validation function."""

        assert mock_validation_data.validate(), (
            "Fight data validation method failed.\nExpected: True.\nGot: False."
        )


@pytest.fixture
def mock_scorecard_path() -> Path:
    """Set up a mock scorecard folder path"""

    path_config = PathConfig()
    path_config.validate_paths()
    return path_config.INPUT_PATH


@pytest.fixture
def mock_output_path() -> Path:
    """Set up a mock scorecard folder path"""

    path_config = PathConfig()
    return path_config.OUTPUT_PATH


@pytest.fixture
def mock_scorecard_image(mock_scorecard_path: Path) -> List[str]:
    """Set up a mock scorecard image path"""

    return read_images(mock_scorecard_path)


def test_read_images(mock_scorecard_path: Path) -> None:
    """Testing read_images function"""

    assert read_images(mock_scorecard_path)[0].endswith(".jpg"), "Image path should end with .jpg extension"


@pytest.fixture
def expected_img_parsed_data() -> FightData:
    return FightData(
        red_fighter_name="BRANDON MORENO",
        blue_fighter_name="AMIR ALBAZI",
        date="11/02/2024",
        red_fighter_total_pts=["49", "50", "50"],
        blue_fighter_total_pts=["46", "45", "45"],
    )


def test_parse_image(mock_scorecard_image: Tuple[str, str], expected_img_parsed_data) -> None:
    """Testing parse_image function"""

    # Extracting data
    got: FightData = parse_image(mock_scorecard_image[0])

    # Running tests
    assert got == expected_img_parsed_data


def test_process_scorecards(mock_scorecard_path: Path, mock_output_path: Path) -> None:
    """Testing process scorecards"""

    resulting_df: pd.DataFrame = process_scorecards(mock_scorecard_path, mock_output_path)
    assert resulting_df.shape == (1, 5), "Resulting DataFrame should have 1 row and 5 columns"
