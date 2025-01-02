import pytest
from typing import List
from config import PathConfig
from pathlib import Path
from src.scorecard_OCR.app import (process_scorecards, read_images,
                                   parse_image, FightData)


class TestFightData():
    """Tests on Fight Data class"""
    fight = FightData()

    def test_initialization(self):
        """Test __init__ method"""
        assert self.fight.red_fighter_name == "-"
        assert self.fight.blue_fighter_name == "-"
        assert self.fight.date == "-"
        assert self.fight.red_fighter_total_pts == []
        assert self.fight.blue_fighter_total_pts == []
    
    def test_to_list(self):
        """Test to_list method"""
        assert isinstance(self.fight.to_list(), list) and len(self.fight.to_list()) == 5

    @pytest.fixture
    def mock_data(self):
        """Mock data for validation testing"""
        self.fight.red_fighter_name = 'BRYAN BARBERENA'
        self.fight.blue_fighter_name = 'DARIAN WEEKS'
        self.fight.date = '12/04/2021'
        self.fight.red_fighter_total_pts = ['29', '29', '29']
        self.fight.blue_fighter_total_pts = ['28', '28', '28']
    
    def test_validation(self, mock_data):
        """Testing validation function"""
        assert self.fight.validate()


@pytest.fixture
def mock_scorecard_path():
    """Set up a mock scorecard folder path"""
    path_config = PathConfig()
    path_config.validate_paths() 
    return path_config.INPUT_PATH


@pytest.fixture
def mock_output_path():
    """Set up a mock scorecard folder path"""
    path_config = PathConfig()
    return path_config.OUTPUT_PATH


@pytest.fixture
def mock_scorecard_image(mock_scorecard_path):
    """Set up a mock scorecard image path"""
    return read_images(mock_scorecard_path)


def test_read_images(mock_scorecard_path):
    """Testing read_images function"""
    assert read_images(mock_scorecard_path)[0].endswith('.jpg')


def test_parse_image(mock_scorecard_image):
    """Testing parse_image function"""
    # Extracting data
    fight_data = parse_image(*mock_scorecard_image)

    # Running tests
    assert fight_data.red_fighter_name == 'BRANDON MORENO'
    assert fight_data.blue_fighter_name == 'AMIR ALBAZI'
    assert fight_data.date == '11/02/2024'
    assert fight_data.red_fighter_total_pts == ['49', '50', '50']
    assert fight_data.blue_fighter_total_pts == ['46', '45', '45']


def test_process_scorecards(mock_scorecard_path, mock_output_path):
    """Testing process scorecards"""
    resulting_df = process_scorecards(mock_scorecard_path, mock_output_path)
    assert resulting_df.shape == (1, 5)
