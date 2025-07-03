import pytest
from src.scraping.ufc_stats.ufcstats_scraping.pipelines import StatsPipeline
from src.scraping.ufc_stats.ufcstats_scraping.items import FightData
from src.scraping.ufc_stats.ufcstats_scraping.spiders.stats_spider import StatsSpider
from itemadapter import ItemAdapter


class TestStatsPipeline:
    """Testing the stats scraping pipeline"""

    def setup_method(self) -> None:
        """General setup for testing."""

        self.pipeline: StatsPipeline = StatsPipeline()
        self.fight_data_raw: FightData = FightData()
        self.fight_data_processed: FightData = FightData()

    @pytest.fixture
    def mock_item_raw(self):
        """Mock raw version of an item."""

        self.fight_data_raw["red_fighter_name"] = "Colby Covington "
        self.fight_data_raw["blue_fighter_name"] = "Joaquin Buckley "
        self.fight_data_raw["red_fighter_nickname"] = '\n      "Chaos"\n    '
        self.fight_data_raw["blue_fighter_nickname"] = '\n      "New Mansa"\n    '
        self.fight_data_raw["red_fighter_result"] = "\n    L\n  "
        self.fight_data_raw["blue_fighter_result"] = "\n    W\n  "
        self.fight_data_raw["method"] = " TKO - Doctor's Stoppage "
        self.fight_data_raw["round"] = "\n        3\n      "
        self.fight_data_raw["time"] = "\n        4:42\n\n      "
        self.fight_data_raw["time_format"] = "\n        5 Rnd (5-5-5-5-5)\n      "
        self.fight_data_raw["referee"] = (
            "\n                                Dan Miragliotta\n                            "
        )
        self.fight_data_raw["details"] = [
            "\n      \n      \n      \n\n          \n\n\n          \n      \n\n          \n\n\n          \n      \n\n          \n\n\n          \n      \n\n          \n\n\n          \n      \n\n          \n\n\n          \n      \n\n          \n\n\n          \n      \n\n          \n\n\n          \n      \n\n          \n\n\n          \n      \n\n          \n\n\n          \n      \n\n          \n\n\n          \n      \n\n          \n\n\n          \n      \n      \n      Cut above eye\n      \n\n    "
        ]
        self.fight_data_raw["bout_type"] = "\n      \n      Welterweight Bout\n    "
        self.fight_data_raw["bonus"] = "-"
        self.fight_data_raw["event_name"] = (
            "\n              UFC Fight Night: Covington vs. Buckley\n            "
        )
        self.fight_data_raw["event_date"] = ["\n      ", "\n      December 14, 2024\n    "]
        self.fight_data_raw["event_location"] = ["\n      ", "\n\n      Tampa, Florida, USA\n    "]
        self.fight_data_raw["red_fighter_KD"] = "\n      0\n    "
        self.fight_data_raw["blue_fighter_KD"] = "\n      0\n    "
        self.fight_data_raw["red_fighter_sig_str"] = "\n      37 of 124\n    "
        self.fight_data_raw["blue_fighter_sig_str"] = "\n      75 of 151\n    "
        self.fight_data_raw["red_fighter_sig_str_pct"] = "\n      29%\n    "
        self.fight_data_raw["blue_fighter_sig_str_pct"] = "\n      49%\n    "
        self.fight_data_raw["red_fighter_total_str"] = "\n      71 of 161\n    "
        self.fight_data_raw["blue_fighter_total_str"] = "\n      81 of 160\n    "
        self.fight_data_raw["red_fighter_TD"] = "\n      1 of 8\n    "
        self.fight_data_raw["blue_fighter_TD"] = "\n      0 of 1\n    "
        self.fight_data_raw["red_fighter_TD_pct"] = "\n      12%\n    "
        self.fight_data_raw["blue_fighter_TD_pct"] = "\n      0%\n    "
        self.fight_data_raw["red_fighter_sub_att"] = "\n      0\n    "
        self.fight_data_raw["blue_fighter_sub_att"] = "\n      1\n    "
        self.fight_data_raw["red_fighter_rev"] = "\n      0\n    "
        self.fight_data_raw["blue_fighter_rev"] = "\n      0\n    "
        self.fight_data_raw["red_fighter_ctrl"] = "\n      3:40\n    "
        self.fight_data_raw["blue_fighter_ctrl"] = "\n      1:18\n    "
        self.fight_data_raw["red_fighter_sig_str_head"] = "\n      26 of 108\n    "
        self.fight_data_raw["blue_fighter_sig_str_head"] = "\n      59 of 131\n    "
        self.fight_data_raw["red_fighter_sig_str_body"] = "\n      8 of 11\n    "
        self.fight_data_raw["blue_fighter_sig_str_body"] = "\n      13 of 17\n    "
        self.fight_data_raw["red_fighter_sig_str_leg"] = "\n      3 of 5\n    "
        self.fight_data_raw["blue_fighter_sig_str_leg"] = "\n      3 of 3\n    "
        self.fight_data_raw["red_fighter_sig_str_distance"] = "\n      33 of 120\n    "
        self.fight_data_raw["blue_fighter_sig_str_distance"] = "\n      65 of 135\n    "
        self.fight_data_raw["red_fighter_sig_str_clinch"] = "\n      0 of 0\n    "
        self.fight_data_raw["blue_fighter_sig_str_clinch"] = "\n      6 of 8\n    "
        self.fight_data_raw["red_fighter_sig_str_ground"] = "\n      4 of 4\n    "
        self.fight_data_raw["blue_fighter_sig_str_ground"] = "\n      4 of 8\n    "
        self.fight_data_raw["red_fighter_sig_str_head_pct"] = "\n                  70%\n                "
        self.fight_data_raw["blue_fighter_sig_str_head_pct"] = "\n                  78%\n                "
        self.fight_data_raw["red_fighter_sig_str_body_pct"] = "\n                  21%\n                "
        self.fight_data_raw["blue_fighter_sig_str_body_pct"] = "\n                  17%\n                "
        self.fight_data_raw["red_fighter_sig_str_leg_pct"] = "\n                  8%\n                "
        self.fight_data_raw["blue_fighter_sig_str_leg_pct"] = "\n                  4%\n                "
        self.fight_data_raw["red_fighter_sig_str_distance_pct"] = "\n                  89%\n                "
        self.fight_data_raw["blue_fighter_sig_str_distance_pct"] = "\n                  86%\n                "
        self.fight_data_raw["red_fighter_sig_str_clinch_pct"] = "\n                  0%\n                "
        self.fight_data_raw["blue_fighter_sig_str_clinch_pct"] = "\n                  8%\n                "
        self.fight_data_raw["red_fighter_sig_str_ground_pct"] = "\n                  10%\n                "
        self.fight_data_raw["blue_fighter_sig_str_ground_pct"] = "\n                  5%\n                "

    @pytest.fixture
    def mock_item_processed(self) -> None:
        """Mock preprocessed version of an item."""

        self.fight_data_processed["blue_fighter_KD"] = "0"
        self.fight_data_processed["blue_fighter_TD"] = "0 of 1"
        self.fight_data_processed["blue_fighter_TD_pct"] = "0%"
        self.fight_data_processed["blue_fighter_ctrl"] = "1:18"
        self.fight_data_processed["blue_fighter_name"] = "Joaquin Buckley"
        self.fight_data_processed["blue_fighter_nickname"] = '"New Mansa"'
        self.fight_data_processed["blue_fighter_result"] = "W"
        self.fight_data_processed["blue_fighter_rev"] = "0"
        self.fight_data_processed["blue_fighter_sig_str"] = "75 of 151"
        self.fight_data_processed["blue_fighter_sig_str_body"] = "13 of 17"
        self.fight_data_processed["blue_fighter_sig_str_body_pct"] = "17%"
        self.fight_data_processed["blue_fighter_sig_str_clinch"] = "6 of 8"
        self.fight_data_processed["blue_fighter_sig_str_clinch_pct"] = "8%"
        self.fight_data_processed["blue_fighter_sig_str_distance"] = "65 of 135"
        self.fight_data_processed["blue_fighter_sig_str_distance_pct"] = "86%"
        self.fight_data_processed["blue_fighter_sig_str_ground"] = "4 of 8"
        self.fight_data_processed["blue_fighter_sig_str_ground_pct"] = "5%"
        self.fight_data_processed["blue_fighter_sig_str_head"] = "59 of 131"
        self.fight_data_processed["blue_fighter_sig_str_head_pct"] = "78%"
        self.fight_data_processed["blue_fighter_sig_str_leg"] = "3 of 3"
        self.fight_data_processed["blue_fighter_sig_str_leg_pct"] = "4%"
        self.fight_data_processed["blue_fighter_sig_str_pct"] = "49%"
        self.fight_data_processed["blue_fighter_sub_att"] = "1"
        self.fight_data_processed["blue_fighter_total_str"] = "81 of 160"
        self.fight_data_processed["bonus"] = "-"
        self.fight_data_processed["bout_type"] = "Welterweight Bout"
        self.fight_data_processed["details"] = "Cut above eye"
        self.fight_data_processed["event_date"] = "December 14, 2024"
        self.fight_data_processed["event_location"] = "Tampa, Florida, USA"
        self.fight_data_processed["event_name"] = "UFC Fight Night: Covington vs. Buckley"
        self.fight_data_processed["method"] = "TKO - Doctor's Stoppage"
        self.fight_data_processed["red_fighter_KD"] = "0"
        self.fight_data_processed["red_fighter_TD"] = "1 of 8"
        self.fight_data_processed["red_fighter_TD_pct"] = "12%"
        self.fight_data_processed["red_fighter_ctrl"] = "3:40"
        self.fight_data_processed["red_fighter_name"] = "Colby Covington"
        self.fight_data_processed["red_fighter_nickname"] = '"Chaos"'
        self.fight_data_processed["red_fighter_result"] = "L"
        self.fight_data_processed["red_fighter_rev"] = "0"
        self.fight_data_processed["red_fighter_sig_str"] = "37 of 124"
        self.fight_data_processed["red_fighter_sig_str_body"] = "8 of 11"
        self.fight_data_processed["red_fighter_sig_str_body_pct"] = "21%"
        self.fight_data_processed["red_fighter_sig_str_clinch"] = "0 of 0"
        self.fight_data_processed["red_fighter_sig_str_clinch_pct"] = "0%"
        self.fight_data_processed["red_fighter_sig_str_distance"] = "33 of 120"
        self.fight_data_processed["red_fighter_sig_str_distance_pct"] = "89%"
        self.fight_data_processed["red_fighter_sig_str_ground"] = "4 of 4"
        self.fight_data_processed["red_fighter_sig_str_ground_pct"] = "10%"
        self.fight_data_processed["red_fighter_sig_str_head"] = "26 of 108"
        self.fight_data_processed["red_fighter_sig_str_head_pct"] = "70%"
        self.fight_data_processed["red_fighter_sig_str_leg"] = "3 of 5"
        self.fight_data_processed["red_fighter_sig_str_leg_pct"] = "8%"
        self.fight_data_processed["red_fighter_sig_str_pct"] = "29%"
        self.fight_data_processed["red_fighter_sub_att"] = "0"
        self.fight_data_processed["red_fighter_total_str"] = "71 of 161"
        self.fight_data_processed["referee"] = "Dan Miragliotta"
        self.fight_data_processed["round"] = "3"
        self.fight_data_processed["time"] = "4:42"
        self.fight_data_processed["time_format"] = "5 Rnd (5-5-5-5-5)"

    def test_clean_text_fields(self, mock_item_raw: None, mock_item_processed: None) -> None:
        """Testing the clean_text_fields method"""

        # Passing the raw data to the pipeline method
        self.pipeline.clean_text_fields(ItemAdapter(self.fight_data_raw))
        # Checking whether the results meet the requirements
        assert self.fight_data_raw == self.fight_data_processed, (
            f"Text cleaning failed.\nExpected: {self.fight_data_processed}\nGot: {self.fight_data_raw}"
        )

    @pytest.fixture
    def mock_nicknames_raw(self) -> None:
        """Mock raw version of nicknames."""

        self.fight_data_raw["red_fighter_nickname"] = '"Chaos"'
        self.fight_data_raw["blue_fighter_nickname"] = '"New Mansa"'

    @pytest.fixture
    def mock_nicknames_processed(self) -> None:
        """Mock preprocessed version of nicknames."""

        self.fight_data_processed["red_fighter_nickname"] = "Chaos"
        self.fight_data_processed["blue_fighter_nickname"] = "New Mansa"

    def test_process_nicknames(self, mock_nicknames_raw: None, mock_nicknames_processed: None) -> None:
        """Testing the process_nicknames method."""

        # Passing the raw data to the pipeline method
        self.pipeline.process_nicknames(ItemAdapter(self.fight_data_raw))
        # Checking whether the results meet the requirements
        assert self.fight_data_raw == self.fight_data_processed, (
            f"Nickname processing failed.\nExpected: {self.fight_data_processed}\nGot: {self.fight_data_raw}"
        )

    @pytest.fixture
    def mock_bonus_raw(self) -> None:
        """Mock raw bersion of the bonus field."""

        self.fight_data_raw["bonus"] = (
            "http://1e49bc5171d173577ecd-1323f4090557a33db01577564f60846c.r80.cf1.rackcdn.com/belt.png"
        )

    @pytest.fixture
    def mock_bonus_processed(self) -> None:
        """Mock raw bersion of the bonus field."""

        self.fight_data_processed["bonus"] = "belt"

    def test_process_bonus(self, mock_bonus_raw: None, mock_bonus_processed: None) -> None:
        """Testing the process_bonus method."""

        # Passing the raw data to the pipeline method
        self.pipeline.process_bonus(ItemAdapter(self.fight_data_raw))
        # Checking whether the results meet the requirements
        assert self.fight_data_raw == self.fight_data_processed, (
            f"Bonus processing failed.\nExpected: {self.fight_data_processed}\nGot: {self.fight_data_raw}"
        )

    @pytest.fixture
    def mock_pct_raw(self) -> None:
        """Mock raw version of 'pct' features."""

        self.fight_data_raw["blue_fighter_TD_pct"] = "50%"
        self.fight_data_raw["blue_fighter_sig_str_body_pct"] = "23%"
        self.fight_data_raw["blue_fighter_sig_str_clinch_pct"] = "16%"
        self.fight_data_raw["blue_fighter_sig_str_distance_pct"] = "83%"
        self.fight_data_raw["blue_fighter_sig_str_ground_pct"] = "0%"
        self.fight_data_raw["blue_fighter_sig_str_head_pct"] = "26%"
        self.fight_data_raw["blue_fighter_sig_str_leg_pct"] = "50%"
        self.fight_data_raw["blue_fighter_sig_str_pct"] = "50%"
        self.fight_data_raw["red_fighter_TD_pct"] = "20%"
        self.fight_data_raw["red_fighter_sig_str_body_pct"] = "16%"
        self.fight_data_raw["red_fighter_sig_str_clinch_pct"] = "8%"
        self.fight_data_raw["red_fighter_sig_str_distance_pct"] = "64%"
        self.fight_data_raw["red_fighter_sig_str_ground_pct"] = "27%"
        self.fight_data_raw["red_fighter_sig_str_head_pct"] = "78%"
        self.fight_data_raw["red_fighter_sig_str_leg_pct"] = "5%"
        self.fight_data_raw["red_fighter_sig_str_pct"] = "55%"

    @pytest.fixture
    def mock_pct_processed(self) -> None:
        """Mock preprocessed version of 'pct' features."""

        self.fight_data_processed["blue_fighter_TD_pct"] = "50.0"
        self.fight_data_processed["blue_fighter_sig_str_body_pct"] = "23.0"
        self.fight_data_processed["blue_fighter_sig_str_clinch_pct"] = "16.0"
        self.fight_data_processed["blue_fighter_sig_str_distance_pct"] = "83.0"
        self.fight_data_processed["blue_fighter_sig_str_ground_pct"] = "0.0"
        self.fight_data_processed["blue_fighter_sig_str_head_pct"] = "26.0"
        self.fight_data_processed["blue_fighter_sig_str_leg_pct"] = "50.0"
        self.fight_data_processed["blue_fighter_sig_str_pct"] = "50.0"
        self.fight_data_processed["red_fighter_TD_pct"] = "20.0"
        self.fight_data_processed["red_fighter_sig_str_body_pct"] = "16.0"
        self.fight_data_processed["red_fighter_sig_str_clinch_pct"] = "8.0"
        self.fight_data_processed["red_fighter_sig_str_distance_pct"] = "64.0"
        self.fight_data_processed["red_fighter_sig_str_ground_pct"] = "27.0"
        self.fight_data_processed["red_fighter_sig_str_head_pct"] = "78.0"
        self.fight_data_processed["red_fighter_sig_str_leg_pct"] = "5.0"
        self.fight_data_processed["red_fighter_sig_str_pct"] = "55.0"

    def test_convert_percentages(self, mock_pct_raw: None, mock_pct_processed: None) -> None:
        """Testing the convert_percentages method."""

        # Passing the raw data to the pipeline method
        self.pipeline.convert_percentages(ItemAdapter(self.fight_data_raw))
        # Checking whether the results meet the requirements
        assert self.fight_data_raw == self.fight_data_processed, (
            f"Percentage conversion failed.\nExpected: {self.fight_data_processed}\nGot: {self.fight_data_raw}"
        )

    @pytest.fixture
    def mock_invalid_data(self) -> None:
        """Mock invalid data for testing that is expected to fail."""

        self.fight_data_raw["red_fighter_name"] = "-"
        self.fight_data_raw["blue_fighter_name"] = "-"
        self.fight_data_raw["event_name"] = "-"
        self.fight_data_raw["event_date"] = "-"

    def test_validate_data(self, mock_invalid_data: None) -> None:
        """Testing the validate_data method."""

        assert not self.pipeline.validate_data(ItemAdapter(self.fight_data_raw)), (
            "Data validation should have failed for invalid data"
        )

    @pytest.fixture
    def mock_item_final_processed(self) -> None:
        """Mock final version of preprocessed features in an item."""

        self.fight_data_processed["blue_fighter_KD"] = "0"
        self.fight_data_processed["blue_fighter_TD"] = "0 of 1"
        self.fight_data_processed["blue_fighter_TD_pct"] = "0.0"
        self.fight_data_processed["blue_fighter_ctrl"] = "1:18"
        self.fight_data_processed["blue_fighter_name"] = "Joaquin Buckley"
        self.fight_data_processed["blue_fighter_nickname"] = "New Mansa"
        self.fight_data_processed["blue_fighter_result"] = "W"
        self.fight_data_processed["blue_fighter_rev"] = "0"
        self.fight_data_processed["blue_fighter_sig_str"] = "75 of 151"
        self.fight_data_processed["blue_fighter_sig_str_body"] = "13 of 17"
        self.fight_data_processed["blue_fighter_sig_str_body_pct"] = "17.0"
        self.fight_data_processed["blue_fighter_sig_str_clinch"] = "6 of 8"
        self.fight_data_processed["blue_fighter_sig_str_clinch_pct"] = "8.0"
        self.fight_data_processed["blue_fighter_sig_str_distance"] = "65 of 135"
        self.fight_data_processed["blue_fighter_sig_str_distance_pct"] = "86.0"
        self.fight_data_processed["blue_fighter_sig_str_ground"] = "4 of 8"
        self.fight_data_processed["blue_fighter_sig_str_ground_pct"] = "5.0"
        self.fight_data_processed["blue_fighter_sig_str_head"] = "59 of 131"
        self.fight_data_processed["blue_fighter_sig_str_head_pct"] = "78.0"
        self.fight_data_processed["blue_fighter_sig_str_leg"] = "3 of 3"
        self.fight_data_processed["blue_fighter_sig_str_leg_pct"] = "4.0"
        self.fight_data_processed["blue_fighter_sig_str_pct"] = "49.0"
        self.fight_data_processed["blue_fighter_sub_att"] = "1"
        self.fight_data_processed["blue_fighter_total_str"] = "81 of 160"
        self.fight_data_processed["bonus"] = "-"
        self.fight_data_processed["bout_type"] = "Welterweight Bout"
        self.fight_data_processed["details"] = "Cut above eye"
        self.fight_data_processed["event_date"] = "December 14, 2024"
        self.fight_data_processed["event_location"] = "Tampa, Florida, USA"
        self.fight_data_processed["event_name"] = "UFC Fight Night: Covington vs. Buckley"
        self.fight_data_processed["method"] = "TKO - Doctor's Stoppage"
        self.fight_data_processed["red_fighter_KD"] = "0"
        self.fight_data_processed["red_fighter_TD"] = "1 of 8"
        self.fight_data_processed["red_fighter_TD_pct"] = "12.0"
        self.fight_data_processed["red_fighter_ctrl"] = "3:40"
        self.fight_data_processed["red_fighter_name"] = "Colby Covington"
        self.fight_data_processed["red_fighter_nickname"] = "Chaos"
        self.fight_data_processed["red_fighter_result"] = "L"
        self.fight_data_processed["red_fighter_rev"] = "0"
        self.fight_data_processed["red_fighter_sig_str"] = "37 of 124"
        self.fight_data_processed["red_fighter_sig_str_body"] = "8 of 11"
        self.fight_data_processed["red_fighter_sig_str_body_pct"] = "21.0"
        self.fight_data_processed["red_fighter_sig_str_clinch"] = "0 of 0"
        self.fight_data_processed["red_fighter_sig_str_clinch_pct"] = "0.0"
        self.fight_data_processed["red_fighter_sig_str_distance"] = "33 of 120"
        self.fight_data_processed["red_fighter_sig_str_distance_pct"] = "89.0"
        self.fight_data_processed["red_fighter_sig_str_ground"] = "4 of 4"
        self.fight_data_processed["red_fighter_sig_str_ground_pct"] = "10.0"
        self.fight_data_processed["red_fighter_sig_str_head"] = "26 of 108"
        self.fight_data_processed["red_fighter_sig_str_head_pct"] = "70.0"
        self.fight_data_processed["red_fighter_sig_str_leg"] = "3 of 5"
        self.fight_data_processed["red_fighter_sig_str_leg_pct"] = "8.0"
        self.fight_data_processed["red_fighter_sig_str_pct"] = "29.0"
        self.fight_data_processed["red_fighter_sub_att"] = "0"
        self.fight_data_processed["red_fighter_total_str"] = "71 of 161"
        self.fight_data_processed["referee"] = "Dan Miragliotta"
        self.fight_data_processed["round"] = "3"
        self.fight_data_processed["time"] = "4:42"
        self.fight_data_processed["time_format"] = "5 Rnd (5-5-5-5-5)"

    def test_process_item(self, mock_item_raw: None, mock_item_final_processed: None) -> None:
        """Testing the process_item method."""

        # Passing the raw data to the pipeline method
        self.pipeline.process_item(self.fight_data_raw, StatsSpider)
        # Checking whether the results meet the requirements
        assert self.fight_data_raw == self.fight_data_processed, (
            "Complete item processing failed.\n"
            f"Expected: {self.fight_data_processed}\n"
            f"Got: {self.fight_data_raw}"
        )
