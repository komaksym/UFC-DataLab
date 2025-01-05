import pytest
from ufcstats_scraping.pipelines import UfcstatsScrapingPipeline
from ufcstats_scraping.items import FightData

class TestUfcstatsPipeline:
    
    def setup_method(self):
        self.pipeline = UfcstatsScrapingPipeline()
        
    def test_clean_text_fields(self):
        item = FightData()
        item['red_fighter_name'] = '  John  Doe\n'
        item['details'] = ['Round 1 - ', 'Fighter wins by KO']
        
        processed = self.pipeline.process_item(item, None)
        assert processed['red_fighter_name'] == 'John Doe'
        assert processed['details'] == 'Round 1 - Fighter wins by KO'

    def test_process_nicknames(self):
        item = FightData()
        item['red_fighter_nickname'] = '"The Spider"\\'
        item['blue_fighter_nickname'] = 'The "Eagle"'
        
        processed = self.pipeline.process_item(item, None)
        assert processed['red_fighter_nickname'] == 'The Spider'
        assert processed['blue_fighter_nickname'] == 'The Eagle'

    def test_process_bonus(self):
        item = FightData()
        item['bonus'] = 'http://example.com/potn.png'
        
        processed = self.pipeline.process_item(item, None)
        assert processed['bonus'] == 'potn'

    def test_convert_percentages(self):
        item = FightData()
        item['red_fighter_sig_str_pct'] = '65%'
        item['blue_fighter_TD_pct'] = '40%'
        
        processed = self.pipeline.process_item(item, None)
        assert processed['red_fighter_sig_str_pct'] == '65.0'
        assert processed['blue_fighter_TD_pct'] == '40.0'

    def test_validation(self):
        item = FightData()
        # Missing required fields should raise warning but not fail
        item['red_fighter_name'] = 'John Doe'
        item['blue_fighter_name'] = ''
        
        with pytest.warns(UserWarning):
            processed = self.pipeline.process_item(item, None)
