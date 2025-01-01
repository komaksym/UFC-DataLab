import pytest

import sys
print(sys.path)

from src.scorecard_OCR.app import (process_scorecards, save_results,
                                   read_images, parse_image, FightData)


# class TestFightData():
#     fight = FightData()

#     """Tests on Fight Data class"""
#     def test_initialization(self):
#         """Test __init__ method"""
#         assert self.fight.red_fighter_name == "-"
#         assert self.fight.blue_fighter_name == "tes-"
#         assert self.fight.date == "-"
#         assert self.fight.red_fighter_total_pts == []
#         assert self.fight.blue_fighter_total_pts == []
    
#     def test_to_list(self):
#         """Test to_list method"""
#         assert self.fight.to_list == [] and len(self.fight.to_list) == 5

#     @pytest.fixture
#     def mock_data(self):
#         self.fight.red_fighter_name = 'BRYAN BARBERENA'
#         self.fight.blue_fighter_name = 'DARIAN WEEKS'
#         self.fight.date = '12/04/2021'
#         self.fight.red_fighter_total_pts = ['29', '29', '29']
#         self.fight.blue_fighter_total_pts = ['28', '28', '28']
    
#     def test_validation(self, mock_data):
#         mock_data()
#         print(self.fight.red_fighter_name)
#         assert self.fight.validate

