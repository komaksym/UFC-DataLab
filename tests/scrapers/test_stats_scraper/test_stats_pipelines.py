import pytest
from src.scraping.ufc_stats_scraping.ufcstats_scraping.pipelines import StatsPipeline
from src.scraping.ufc_stats_scraping.ufcstats_scraping.items import FightData
from src.scraping.ufc_stats_scraping.ufcstats_scraping.spiders.stats_spider import Stats_Spider
from itemadapter import ItemAdapter


class TestStatsPipeline:
    """Test suite for the UFC Stats Pipeline.
    
    Tests the pipeline's ability to:
    - Clean and format text fields
    - Process fighter nicknames
    - Handle bonus information
    - Convert percentage values
    - Validate fight data
    """

    def setup_method(self):
        """Initialize pipeline and test items before each test."""
        self.pipeline = StatsPipeline()
        self.fight_data_raw = FightData()
        self.fight_data_processed = FightData()

    @pytest.fixture
    def mock_item_raw(self):
        """Fixture providing raw unprocessed fight data."""
        self.fight_data_raw['red_fighter_name'] = 'Colby Covington '
        self.fight_data_raw['blue_fighter_name'] = 'Joaquin Buckley '
        self.fight_data_raw['red_fighter_nickname'] = '\n      "Chaos"\n    '
        self.fight_data_raw['blue_fighter_nickname'] = '\n      "New Mansa"\n    '
        self.fight_data_raw['red_fighter_result'] = '\n    L\n  '
        self.fight_data_raw['blue_fighter_result'] = '\n    W\n  '
        self.fight_data_raw['method'] = " TKO - Doctor's Stoppage "
        self.fight_data_raw['round'] = '\n        3\n      '
        self.fight_data_raw['time'] = '\n        4:42\n\n      '
        self.fight_data_raw['time_format'] = '\n        5 Rnd (5-5-5-5-5)\n      '
        self.fight_data_raw['referee'] = '\n                                Dan Miragliotta\n                            '
        self.fight_data_raw['details'] = ['\n      \n      \n      \n\n          \n\n\n          \n      \n\n          \n\n\n          \n      \n\n          \n\n\n          \n      \n\n          \n\n\n          \n      \n\n          \n\n\n          \n      \n\n          \n\n\n          \n      \n\n          \n\n\n          \n      \n\n          \n\n\n          \n      \n\n          \n\n\n          \n      \n\n          \n\n\n          \n      \n\n          \n\n\n          \n      \n      \n      Cut above eye\n      \n\n    ']
        self.fight_data_raw['bout_type'] = '\n      \n      Welterweight Bout\n    '
        self.fight_data_raw['bonus'] = "-"
        self.fight_data_raw['event_name'] = '\n              UFC Fight Night: Covington vs. Buckley\n            '
        self.fight_data_raw['event_date'] = ['\n      ', '\n      December 14, 2024\n    ']
        self.fight_data_raw['event_location'] = ['\n      ', '\n\n      Tampa, Florida, USA\n    ']
        self.fight_data_raw['red_fighter_KD'] = '\n      0\n    '
        self.fight_data_raw['blue_fighter_KD'] = '\n      0\n    '
        self.fight_data_raw['red_fighter_sig_str'] = '\n      37 of 124\n    '
        self.fight_data_raw['blue_fighter_sig_str'] = '\n      75 of 151\n    '
        self.fight_data_raw['red_fighter_sig_str_pct'] = '\n      29%\n    '
        self.fight_data_raw['blue_fighter_sig_str_pct'] = '\n      49%\n    '
        self.fight_data_raw['red_fighter_total_str'] = '\n      71 of 161\n    '
        self.fight_data_raw['blue_fighter_total_str'] = '\n      81 of 160\n    '
        self.fight_data_raw['red_fighter_TD'] = '\n      1 of 8\n    '
        self.fight_data_raw['blue_fighter_TD'] = '\n      0 of 1\n    '
        self.fight_data_raw['red_fighter_TD_pct'] = '\n      12%\n    '
        self.fight_data_raw['blue_fighter_TD_pct'] = '\n      0%\n    '
        self.fight_data_raw['red_fighter_sub_att'] = '\n      0\n    '
        self.fight_data_raw['blue_fighter_sub_att'] = '\n      1\n    '
        self.fight_data_raw['red_fighter_rev'] = '\n      0\n    '
        self.fight_data_raw['blue_fighter_rev'] = '\n      0\n    '
        self.fight_data_raw['red_fighter_ctrl'] = '\n      3:40\n    '
        self.fight_data_raw['blue_fighter_ctrl'] = '\n      1:18\n    '
        self.fight_data_raw['red_fighter_sig_str_head'] = '\n      26 of 108\n    '
        self.fight_data_raw['blue_fighter_sig_str_head'] = '\n      59 of 131\n    '
        self.fight_data_raw['red_fighter_sig_str_body'] = '\n      8 of 11\n    '
        self.fight_data_raw['blue_fighter_sig_str_body'] = '\n      13 of 17\n    '
        self.fight_data_raw['red_fighter_sig_str_leg'] = '\n      3 of 5\n    '
        self.fight_data_raw['blue_fighter_sig_str_leg'] = '\n      3 of 3\n    '
        self.fight_data_raw['red_fighter_sig_str_distance'] = '\n      33 of 120\n    '
        self.fight_data_raw['blue_fighter_sig_str_distance'] = '\n      65 of 135\n    '
        self.fight_data_raw['red_fighter_sig_str_clinch'] = '\n      0 of 0\n    '
        self.fight_data_raw['blue_fighter_sig_str_clinch'] = '\n      6 of 8\n    '
        self.fight_data_raw['red_fighter_sig_str_ground'] = '\n      4 of 4\n    '
        self.fight_data_raw['blue_fighter_sig_str_ground'] = '\n      4 of 8\n    '
        self.fight_data_raw['red_fighter_sig_str_head_pct'] = '\n                  70%\n                '
        self.fight_data_raw['blue_fighter_sig_str_head_pct'] = '\n                  78%\n                '
        self.fight_data_raw['red_fighter_sig_str_body_pct'] = '\n                  21%\n                '
        self.fight_data_raw['blue_fighter_sig_str_body_pct'] = '\n                  17%\n                '
        self.fight_data_raw['red_fighter_sig_str_leg_pct'] = '\n                  8%\n                '
        self.fight_data_raw['blue_fighter_sig_str_leg_pct'] = '\n                  4%\n                '
        self.fight_data_raw['red_fighter_sig_str_distance_pct'] = '\n                  89%\n                '
        self.fight_data_raw['blue_fighter_sig_str_distance_pct'] = '\n                  86%\n                '
        self.fight_data_raw['red_fighter_sig_str_clinch_pct'] = '\n                  0%\n                '
        self.fight_data_raw['blue_fighter_sig_str_clinch_pct'] = '\n                  8%\n                '
        self.fight_data_raw['red_fighter_sig_str_ground_pct'] = '\n                  10%\n                '
        self.fight_data_raw['blue_fighter_sig_str_ground_pct'] = '\n                  5%\n                '

    @pytest.fixture
    def mock_item_processed(self):
        """Fixture providing expected processed fight data."""
        self.fight_data_processed['blue_fighter_KD'] = '0'
        self.fight_data_processed['blue_fighter_TD'] = '0 of 1'
        self.fight_data_processed['blue_fighter_TD_pct'] = '0%'
        self.fight_data_processed['blue_fighter_ctrl'] = '1:18'
        self.fight_data_processed['blue_fighter_name'] = 'Joaquin Buckley'
        self.fight_data_processed['blue_fighter_nickname'] = '"New Mansa"'
        self.fight_data_processed['blue_fighter_result'] = 'W'
        self.fight_data_processed['blue_fighter_rev'] = '0'
        self.fight_data_processed['blue_fighter_sig_str'] = '75 of 151'
        self.fight_data_processed['blue_fighter_sig_str_body'] = '13 of 17'
        self.fight_data_processed['blue_fighter_sig_str_body_pct'] = '17%'
        self.fight_data_processed['blue_fighter_sig_str_clinch'] = '6 of 8'
        self.fight_data_processed['blue_fighter_sig_str_clinch_pct'] = '8%'
        self.fight_data_processed['blue_fighter_sig_str_distance'] = '65 of 135'
        self.fight_data_processed['blue_fighter_sig_str_distance_pct'] = '86%'
        self.fight_data_processed['blue_fighter_sig_str_ground'] = '4 of 8'
        self.fight_data_processed['blue_fighter_sig_str_ground_pct'] = '5%'
        self.fight_data_processed['blue_fighter_sig_str_head'] = '59 of 131'
        self.fight_data_processed['blue_fighter_sig_str_head_pct'] = '78%'
        self.fight_data_processed['blue_fighter_sig_str_leg'] = '3 of 3'
        self.fight_data_processed['blue_fighter_sig_str_leg_pct'] = '4%'
        self.fight_data_processed['blue_fighter_sig_str_pct'] = '49%'
        self.fight_data_processed['blue_fighter_sub_att'] = '1'
        self.fight_data_processed['blue_fighter_total_str'] = '81 of 160'
        self.fight_data_processed['bonus'] = '-'
        self.fight_data_processed['bout_type'] = 'Welterweight Bout'
        self.fight_data_processed['details'] = 'Cut above eye'
        self.fight_data_processed['event_date'] = 'December 14, 2024'
        self.fight_data_processed['event_location'] = 'Tampa, Florida, USA'
        self.fight_data_processed['event_name'] = 'UFC Fight Night: Covington vs. Buckley'
        self.fight_data_processed['method'] = "TKO - Doctor's Stoppage"
        self.fight_data_processed['red_fighter_KD'] = '0'
        self.fight_data_processed['red_fighter_TD'] = '1 of 8'
        self.fight_data_processed['red_fighter_TD_pct'] = '12%'
        self.fight_data_processed['red_fighter_ctrl'] = '3:40'
        self.fight_data_processed['red_fighter_name'] = 'Colby Covington'
        self.fight_data_processed['red_fighter_nickname'] = '"Chaos"'
        self.fight_data_processed['red_fighter_result'] = 'L'
        self.fight_data_processed['red_fighter_rev'] = '0'
        self.fight_data_processed['red_fighter_sig_str'] = '37 of 124'
        self.fight_data_processed['red_fighter_sig_str_body'] = '8 of 11'
        self.fight_data_processed['red_fighter_sig_str_body_pct'] = '21%'
        self.fight_data_processed['red_fighter_sig_str_clinch'] = '0 of 0'
        self.fight_data_processed['red_fighter_sig_str_clinch_pct'] = '0%'
        self.fight_data_processed['red_fighter_sig_str_distance'] = '33 of 120'
        self.fight_data_processed['red_fighter_sig_str_distance_pct'] = '89%'
        self.fight_data_processed['red_fighter_sig_str_ground'] = '4 of 4'
        self.fight_data_processed['red_fighter_sig_str_ground_pct'] = '10%'
        self.fight_data_processed['red_fighter_sig_str_head'] = '26 of 108'
        self.fight_data_processed['red_fighter_sig_str_head_pct'] = '70%'
        self.fight_data_processed['red_fighter_sig_str_leg'] = '3 of 5'
        self.fight_data_processed['red_fighter_sig_str_leg_pct'] = '8%'
        self.fight_data_processed['red_fighter_sig_str_pct'] = '29%'
        self.fight_data_processed['red_fighter_sub_att'] = '0'
        self.fight_data_processed['red_fighter_total_str'] = '71 of 161'
        self.fight_data_processed['referee'] = 'Dan Miragliotta'
        self.fight_data_processed['round'] = '3'
        self.fight_data_processed['time'] = '4:42'
        self.fight_data_processed['time_format'] = '5 Rnd (5-5-5-5-5)'
        
    def test_clean_text_fields(self, mock_item_raw, mock_item_processed):
        """Test text field cleaning and formatting.
        
        Verifies that:
        - Whitespace is properly stripped
        - Special characters are handled correctly
        - Text formatting is consistent
        """
        self.pipeline.clean_text_fields(ItemAdapter(self.fight_data_raw))
        assert self.fight_data_raw == self.fight_data_processed, (
            f"Text cleaning failed.\n"
            f"Expected: {self.fight_data_processed}\n"
            f"Got: {self.fight_data_raw}"
        )

    @pytest.fixture
    def mock_nicknames_raw(self):
        self.fight_data_raw['red_fighter_nickname'] = '"Chaos"'
        self.fight_data_raw['blue_fighter_nickname'] = '"New Mansa"'

    @pytest.fixture
    def mock_nicknames_processed(self):
        self.fight_data_processed['red_fighter_nickname'] = 'Chaos'
        self.fight_data_processed['blue_fighter_nickname'] = 'New Mansa'

    def test_process_nicknames(self, mock_nicknames_raw, mock_nicknames_processed):
        """Test fighter nickname processing.
        
        Verifies that:
        - Quotes are properly removed
        - Formatting is consistent
        """
        self.pipeline.process_nicknames(ItemAdapter(self.fight_data_raw))
        assert self.fight_data_raw == self.fight_data_processed, (
            f"Nickname processing failed.\n"
            f"Expected: {self.fight_data_processed}\n"
            f"Got: {self.fight_data_raw}"
        )

    @pytest.fixture
    def mock_bonus_raw(self):
        self.fight_data_raw['bonus'] = 'http://1e49bc5171d173577ecd-1323f4090557a33db01577564f60846c.r80.cf1.rackcdn.com/belt.png'

    @pytest.fixture
    def mock_bonus_processed(self):
        self.fight_data_processed['bonus'] = 'belt'
        
    def test_process_bonus(self, mock_bonus_raw, mock_bonus_processed):
        """Test bonus information processing.
        
        Verifies that:
        - Bonus URLs are correctly parsed
        - Bonus types are properly extracted
        """
        self.pipeline.process_bonus(ItemAdapter(self.fight_data_raw))
        assert self.fight_data_raw == self.fight_data_processed, (
            f"Bonus processing failed.\n"
            f"Expected: {self.fight_data_processed}\n"
            f"Got: {self.fight_data_raw}"
        )
        
    @pytest.fixture
    def mock_pct_raw(self):
        self.fight_data_raw['blue_fighter_TD_pct'] = '50%'
        self.fight_data_raw['blue_fighter_sig_str_body_pct'] = '23%'
        self.fight_data_raw['blue_fighter_sig_str_clinch_pct'] = '16%'
        self.fight_data_raw['blue_fighter_sig_str_distance_pct'] = '83%'
        self.fight_data_raw['blue_fighter_sig_str_ground_pct'] = '0%'
        self.fight_data_raw['blue_fighter_sig_str_head_pct'] = '26%'
        self.fight_data_raw['blue_fighter_sig_str_leg_pct'] = '50%'
        self.fight_data_raw['blue_fighter_sig_str_pct'] = '50%'
        self.fight_data_raw['red_fighter_TD_pct'] = '20%'
        self.fight_data_raw['red_fighter_sig_str_body_pct'] = '16%'
        self.fight_data_raw['red_fighter_sig_str_clinch_pct'] = '8%'
        self.fight_data_raw['red_fighter_sig_str_distance_pct'] = '64%'
        self.fight_data_raw['red_fighter_sig_str_ground_pct'] = '27%'
        self.fight_data_raw['red_fighter_sig_str_head_pct'] = '78%'
        self.fight_data_raw['red_fighter_sig_str_leg_pct'] = '5%'
        self.fight_data_raw['red_fighter_sig_str_pct'] = '55%'

    @pytest.fixture
    def mock_pct_processed(self):
        self.fight_data_processed['blue_fighter_TD_pct'] = '50.0'
        self.fight_data_processed['blue_fighter_sig_str_body_pct'] = '23.0'
        self.fight_data_processed['blue_fighter_sig_str_clinch_pct'] = '16.0'
        self.fight_data_processed['blue_fighter_sig_str_distance_pct'] = '83.0'
        self.fight_data_processed['blue_fighter_sig_str_ground_pct'] = '0.0'
        self.fight_data_processed['blue_fighter_sig_str_head_pct'] = '26.0'
        self.fight_data_processed['blue_fighter_sig_str_leg_pct'] = '50.0'
        self.fight_data_processed['blue_fighter_sig_str_pct'] = '50.0'
        self.fight_data_processed['red_fighter_TD_pct'] = '20.0'
        self.fight_data_processed['red_fighter_sig_str_body_pct'] = '16.0'
        self.fight_data_processed['red_fighter_sig_str_clinch_pct'] = '8.0'
        self.fight_data_processed['red_fighter_sig_str_distance_pct'] = '64.0'
        self.fight_data_processed['red_fighter_sig_str_ground_pct'] = '27.0'
        self.fight_data_processed['red_fighter_sig_str_head_pct'] = '78.0'
        self.fight_data_processed['red_fighter_sig_str_leg_pct'] = '5.0'
        self.fight_data_processed['red_fighter_sig_str_pct'] = '55.0'

    def test_convert_percentages(self, mock_pct_raw, mock_pct_processed):
        """Test percentage value conversion.
        
        Verifies that:
        - Percentage symbols are removed
        - Values are converted to proper format
        """
        self.pipeline.convert_percentages(ItemAdapter(self.fight_data_raw))
        assert self.fight_data_raw == self.fight_data_processed, (
            f"Percentage conversion failed.\n"
            f"Expected: {self.fight_data_processed}\n"
            f"Got: {self.fight_data_raw}"
        )
        
    @pytest.fixture
    def mock_invalid_data(self):
        self.fight_data_raw['red_fighter_name'] = "-"
        self.fight_data_raw['blue_fighter_name'] = "-"
        self.fight_data_raw['event_name'] = "-"
        self.fight_data_raw['event_date'] = "-"

    def test_validate_data(self, mock_invalid_data):
        """Test fight data validation.
        
        Verifies that:
        - Invalid data is properly detected
        - Required fields are checked
        """
        assert not self.pipeline.validate_data(ItemAdapter(self.fight_data_raw)), (
            "Validation should fail for invalid data"
        )

    @pytest.fixture
    def mock_item_final_processed(self):
        self.fight_data_processed['blue_fighter_KD'] = '0'
        self.fight_data_processed['blue_fighter_TD'] = '0 of 1'
        self.fight_data_processed['blue_fighter_TD_pct'] = '0.0'
        self.fight_data_processed['blue_fighter_ctrl'] = '1:18'
        self.fight_data_processed['blue_fighter_name'] = 'Joaquin Buckley'
        self.fight_data_processed['blue_fighter_nickname'] = 'New Mansa'
        self.fight_data_processed['blue_fighter_result'] = 'W'
        self.fight_data_processed['blue_fighter_rev'] = '0'
        self.fight_data_processed['blue_fighter_sig_str'] = '75 of 151'
        self.fight_data_processed['blue_fighter_sig_str_body'] = '13 of 17'
        self.fight_data_processed['blue_fighter_sig_str_body_pct'] = '17.0'
        self.fight_data_processed['blue_fighter_sig_str_clinch'] = '6 of 8'
        self.fight_data_processed['blue_fighter_sig_str_clinch_pct'] = '8.0'
        self.fight_data_processed['blue_fighter_sig_str_distance'] = '65 of 135'
        self.fight_data_processed['blue_fighter_sig_str_distance_pct'] = '86.0'
        self.fight_data_processed['blue_fighter_sig_str_ground'] = '4 of 8'
        self.fight_data_processed['blue_fighter_sig_str_ground_pct'] = '5.0'
        self.fight_data_processed['blue_fighter_sig_str_head'] = '59 of 131'
        self.fight_data_processed['blue_fighter_sig_str_head_pct'] = '78.0'
        self.fight_data_processed['blue_fighter_sig_str_leg'] = '3 of 3'
        self.fight_data_processed['blue_fighter_sig_str_leg_pct'] = '4.0'
        self.fight_data_processed['blue_fighter_sig_str_pct'] = '49.0'
        self.fight_data_processed['blue_fighter_sub_att'] = '1'
        self.fight_data_processed['blue_fighter_total_str'] = '81 of 160'
        self.fight_data_processed['bonus'] = '-'
        self.fight_data_processed['bout_type'] = 'Welterweight Bout'
        self.fight_data_processed['details'] = 'Cut above eye'
        self.fight_data_processed['event_date'] = 'December 14, 2024'
        self.fight_data_processed['event_location'] = 'Tampa, Florida, USA'
        self.fight_data_processed['event_name'] = 'UFC Fight Night: Covington vs. Buckley'
        self.fight_data_processed['method'] = "TKO - Doctor's Stoppage"
        self.fight_data_processed['red_fighter_KD'] = '0'
        self.fight_data_processed['red_fighter_TD'] = '1 of 8'
        self.fight_data_processed['red_fighter_TD_pct'] = '12.0'
        self.fight_data_processed['red_fighter_ctrl'] = '3:40'
        self.fight_data_processed['red_fighter_name'] = 'Colby Covington'
        self.fight_data_processed['red_fighter_nickname'] = 'Chaos'
        self.fight_data_processed['red_fighter_result'] = 'L'
        self.fight_data_processed['red_fighter_rev'] = '0'
        self.fight_data_processed['red_fighter_sig_str'] = '37 of 124'
        self.fight_data_processed['red_fighter_sig_str_body'] = '8 of 11'
        self.fight_data_processed['red_fighter_sig_str_body_pct'] = '21.0'
        self.fight_data_processed['red_fighter_sig_str_clinch'] = '0 of 0'
        self.fight_data_processed['red_fighter_sig_str_clinch_pct'] = '0.0'
        self.fight_data_processed['red_fighter_sig_str_distance'] = '33 of 120'
        self.fight_data_processed['red_fighter_sig_str_distance_pct'] = '89.0'
        self.fight_data_processed['red_fighter_sig_str_ground'] = '4 of 4'
        self.fight_data_processed['red_fighter_sig_str_ground_pct'] = '10.0'
        self.fight_data_processed['red_fighter_sig_str_head'] = '26 of 108'
        self.fight_data_processed['red_fighter_sig_str_head_pct'] = '70.0'
        self.fight_data_processed['red_fighter_sig_str_leg'] = '3 of 5'
        self.fight_data_processed['red_fighter_sig_str_leg_pct'] = '8.0'
        self.fight_data_processed['red_fighter_sig_str_pct'] = '29.0'
        self.fight_data_processed['red_fighter_sub_att'] = '0'
        self.fight_data_processed['red_fighter_total_str'] = '71 of 161'
        self.fight_data_processed['referee'] = 'Dan Miragliotta'
        self.fight_data_processed['round'] = '3'
        self.fight_data_processed['time'] = '4:42'
        self.fight_data_processed['time_format'] = '5 Rnd (5-5-5-5-5)'

    def test_process_item(self, mock_item_raw, mock_item_final_processed):
        """Test complete item processing pipeline.
        
        Verifies that:
        - All processing steps are applied correctly
        - Final output matches expected format
        """
        self.pipeline.process_item(self.fight_data_raw, Stats_Spider)
        assert self.fight_data_raw == self.fight_data_processed, (
            f"Complete pipeline processing failed.\n"
            f"Expected: {self.fight_data_processed}\n"
            f"Got: {self.fight_data_raw}"
        )