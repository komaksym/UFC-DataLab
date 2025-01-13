import pytest
from typing import List, Tuple, Optional
import pandas as pd
from config import PathConfig
from src.scorecard_OCR.app import (process_scorecards, read_images,
                                   parse_image, FightData)


class TestFightData:
    """Tests on Fight Data class"""

    def setup_method(self) -> None:
        self.fight = FightData()

    def test_initialization(self) -> None:
        """Test __init__ method"""
        assert self.fight.red_fighter_name == "-", "Red fighter name should be initialized as '-'"
        assert self.fight.blue_fighter_name == "-", "Blue fighter name should be initialized as '-'"
        assert self.fight.date == "-", "Date should be initialized as '-'"
        assert self.fight.red_fighter_total_pts == [], "Red fighter points should be initialized as empty list"
        assert self.fight.blue_fighter_total_pts == [], "Blue fighter points should be initialized as empty list"
    
    def test_to_list(self) -> None:
        """Test to_list method"""
        result: List[str] = self.fight.to_list()
        assert isinstance(result, list), "to_list() should return a list"
        assert len(result) == 5, "to_list() should return 5 elements"

    @pytest.fixture
    def mock_data(self) -> None:
        """Mock data for validation testing"""
        self.fight.red_fighter_name = 'BRYAN BARBERENA'
        self.fight.blue_fighter_name = 'DARIAN WEEKS'
        self.fight.date = '12/04/2021'
        self.fight.red_fighter_total_pts = ['29', '29', '29']
        self.fight.blue_fighter_total_pts = ['28', '28', '28']
    
    def test_validation(self, mock_data) -> None:
        """Testing validation function"""
        assert self.fight.validate(), "Fight data validation method failed.\nExpected: True.\nGot: False."


@pytest.fixture
def mock_scorecard_path() -> str:
    """Set up a mock scorecard folder path"""
    path_config = PathConfig()
    path_config.validate_paths() 
    return path_config.INPUT_PATH


@pytest.fixture
def mock_output_path() -> str:
    """Set up a mock scorecard folder path"""
    path_config = PathConfig()
    return path_config.OUTPUT_PATH


@pytest.fixture
def mock_scorecard_image(mock_scorecard_path: str) -> Tuple[str, str]:
    """Set up a mock scorecard image path"""
    return read_images(mock_scorecard_path)


def test_read_images(mock_scorecard_path: str) -> None:
    """Testing read_images function"""
    assert read_images(mock_scorecard_path)[0].endswith('.jpg'), "Image path should end with .jpg extension"


def test_parse_image(mock_scorecard_image: Tuple[str, str]) -> None:
    """Testing parse_image function"""
    # Extracting data
    fight_data: FightData = parse_image(*mock_scorecard_image)

    # Running tests
    assert fight_data.red_fighter_name == 'BRANDON MORENO', "Red fighter name not correctly parsed"
    assert fight_data.blue_fighter_name == 'AMIR ALBAZI', "Blue fighter name not correctly parsed"
    assert fight_data.date == '11/02/2024', "Fight date not correctly parsed"
    assert fight_data.red_fighter_total_pts == ['49', '50', '50'], "Red fighter points not correctly parsed"
    assert fight_data.blue_fighter_total_pts == ['46', '45', '45'], "Blue fighter points not correctly parsed"


def test_process_scorecards(mock_scorecard_path: str, mock_output_path: str) -> None:
    """Testing process scorecards"""
    resulting_df: pd.DataFrame = process_scorecards(mock_scorecard_path, mock_output_path)
    assert resulting_df.shape == (1, 5), "Resulting DataFrame should have 1 row and 5 columns"
