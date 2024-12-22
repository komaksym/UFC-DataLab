# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import re
import logging
from typing import Any, Dict, Optional


logger = logging.getLogger(__name__)


class UfcstatsScrapingPipeline:
    """Pipeline for processing and cleaning UFC fight data."""
    
    def __init__(self):
        self.items_processed = 0
        self.errors = 0
        
    def process_item(self, item: Dict[str, Any], spider: Any) -> Dict[str, Any]:
        """
        Process and clean scraped UFC fight data.
        
        Args:
            item: Scraped item containing fight data
            spider: Spider instance that generated this item
        Returns:
            Processed item with cleaned data
        """
        try:
            adapter = ItemAdapter(item)
            self._clean_text_fields(adapter)
            self._process_nicknames(adapter)
            self._process_bonus(adapter)
            self._convert_percentages(adapter)
            self._validate_data(adapter)
            self._unit_test(adapter)
            
            self.items_processed += 1
            return item
            
        except Exception as e:
            self.errors += 1
            logger.error(f"Error processing item: {str(e)}")
            raise
            
    def _clean_text_fields(self, adapter: ItemAdapter) -> None:
        """Clean and normalize text fields."""
        for fieldname in adapter.field_names():
            value = adapter.get(fieldname, "-")
            if isinstance(value, list):
                # Join lists and clean whitespace
                value = " ".join(value)
                value = " ".join(value.replace("\n", "").split())
            else:
                value = value.strip()
            adapter[fieldname] = value
            
    def _process_nicknames(self, adapter: ItemAdapter) -> None:
        """Clean fighter nicknames."""
        for nickname in ['red_fighter_nickname', 'blue_fighter_nickname']:
            if adapter.get(nickname):
                adapter[nickname] = re.sub(r'["\\]', '', adapter.get(nickname))
                
    def _process_bonus(self, adapter: ItemAdapter) -> None:
        """Extract bonus type from image source."""
        bonus = adapter.get('bonus')
        if bonus and bonus != "-":
            try:
                adapter['bonus'] = re.findall(r"\w+(?=\.png)", bonus)[0]
            except IndexError:
                logger.warning(f"Could not extract bonus type from: {bonus}")
                adapter['bonus'] = "-"
                
    def _convert_percentages(self, adapter: ItemAdapter) -> None:
        """Convert percentage strings to numeric values."""
        percentage_fields = [field for field in adapter.field_names() if field.endswith('_pct')]
        for field in percentage_fields:
            value = adapter.get(field, "-")
            if value != "-":
                try:
                    adapter[field] = str(float(value.replace('%', '')))
                except ValueError:
                    logger.warning(f"Invalid percentage value in {field}: {value}")
                    
    def _validate_data(self, adapter: ItemAdapter) -> None:
        """Validate critical data fields."""
        required_fields = ['red_fighter_name', 'blue_fighter_name', 'event_name', 'event_date']
        for field in required_fields:
            if not adapter.get(field):
                logger.warning(f"Missing required field: {field}")

    def _unit_test(self, adapter: ItemAdapter) -> None:

        def _unit_test_fight_participant(self, adapter: ItemAdapter) -> None:
            # Unit testing fighter names
            for name in ["red_fighter_name", "blue_fighter_name"]:
                assert bool(re.match(r"^\w+ \w+$", adapter.get(name))), "Fighter_name test has failed"    

            # Unit testing fighter nicknames
            for name in ['red_fighter_nickname', 'blue_fighter_nickname']:
                assert bool()
        """Fight participant information"""
        
        
        # Unit testing fight results
        for result in ["red_fighter_result", "blue_fighter_result"]:
            assert adapter[result] in ["W", "L"], "Fighter_result test has failed"

        # Unit testing fight result method
        assert adapter['method'] in ['KO/TKO', 'Submission', 'Decision - Unanimous', 'Decision - Split',
               "TKO - Doctor's Stoppage", 'Decision - Majority', 'DQ'], "Fight_method test has failed"
        
        # Unit testing fight round 
        assert adapter['event_date'] in [1, 2, 3, 4, 5], "Event_date test has failed"

        # Unit testing event location
        assert adapter['event_location'] != "-", "Event_location test has failed"

        # Unit testing red/blue fighter KD
        assert adapter['red_fighter_KD'].isnumeric() and adapter['blue_fighter_KD'].isnumeric(), \
               "Red/blue_fighter_KD test has failed"

        # Unit testing red/blue fighter significant strikes
        assert 'of' in adapter['red_fighter_sig_str'] and 'of' in adapter['blue_fighter_sig_str'], \
                "Red/blue_fighter_sig_str test has failed"

        # Unit testing red/blue fighter sig str pct
        assert ("%" in adapter['red_fighter_sig_str_pct'] or "%" in adapter['blue_fighter_sig_str_pct']) \
               or ("-" in adapter['red_fighter_sig_str_pct'] or "-" in adapter['blue_fighter_sig_str_pct']), \
               "Red/blue_fighter_sig_str_pct test has failed"

        # Unit testing red/blue fighter total strikes
        assert 'of' in adapter['red_fighter_total_str'] and 'of' in adapter['blue_fighter_total_str'], \
                "Red/blue_fighter_total_str test has failed"
        
        # Unit testing red/blue fighter TD
        assert 'of' in adapter['red_fighter_TD'] and 'of' in adapter['blue_fighter_TD'], \
                "Red/blue_fighter_TD test has failed"
        
        # Unit testing red/blue fighter TD pct
        assert ("%" in adapter['red_fighter_TD_pct'] or "%" in adapter['blue_fighter_TD_pct']) \
               or ("-" in adapter['red_fighter_TD_pct'] or "-" in adapter['blue_fighter_TD_pct']), \
               "Red/blue_fighter_TD_pct test has failed"
        
        # Unit testing red/blue fighter sub att
        assert adapter['red_fighter_sub_att'].isnumeric() and adapter['blue_fighter_sub_att'].isnumeric(), \
               "Red/blue_fighter_sub_att test has failed"
        
        # Unit testing red/blue fighter rev
        assert adapter['red_fighter_rev'].isnumeric() and adapter['blue_fighter_rev'].isnumeric(), \
               "Red/blue_fighter_rev test has failed"
        
        # Unit testing red/blue fighter ctrl
        assert adapter['red_fighter_ctrl'].isnumeric() and adapter['blue_fighter_ctrl'].isnumeric(), \
               "Red/blue_fighter_ctrl test has failed"
        
        # Unit testing red/blue fighter sig str head
        assert 'of' in adapter['red_fighter_sig_str_head'] and 'of' in adapter['blue_fighter_sig_str_head'], \
                "Red/blue_fighter_sig_str_head test has failed"
        
        # Unit testing red/blue fighter sig str body
        assert 'of' in adapter['red_fighter_sig_str_body'] and 'of' in adapter['blue_fighter_sig_str_body'], \
                "Red/blue_fighter_sig_str_body test has failed"
        
        # Unit testing red/blue fighter sig str leg
        assert 'of' in adapter['red_fighter_sig_str_leg'] and 'of' in adapter['blue_fighter_sig_str_leg'], \
                "Red/blue_fighter_sig_str_leg test has failed"
        
        # Unit testing red/blue fighter sig str distance
        assert 'of' in adapter['red_fighter_sig_str_distance'] and 'of' in adapter['blue_fighter_sig_str_distance'], \
                "Red/blue_fighter_sig_str_distance test has failed"
        
        # Unit testing red/blue fighter sig str clinch
        assert 'of' in adapter['red_fighter_sig_str_clinch'] and 'of' in adapter['blue_fighter_sig_str_clinch'], \
                "Red/blue_fighter_sig_str_clinch test has failed"
        
        # Unit testing red/blue fighter sig str ground
        assert 'of' in adapter['red_fighter_sig_str_ground'] and 'of' in adapter['blue_fighter_sig_str_ground'], \
                "Red/blue_fighter_sig_str_ground test has failed"
        
        # Unit testing red/blue fighter sig str head pct
        assert '%' in adapter['red_fighter_sig_str_head_pct'] and '%' in adapter['blue_fighter_sig_str_head_pct'], \
                "Red/blue_fighter_sig_str_head_pct"
        
        # Unit testing red/blue fighter sig str body pct
        assert '%' in adapter['red_fighter_sig_str_body_pct'] and '%' in adapter['blue_fighter_sig_str_body_pct'], \
                "Red/blue_fighter_sig_str_body_pct"
        
        # Unit testing red/blue fighter sig str leg pct
        assert '%' in adapter['red_fighter_sig_str_leg_pct'] and '%' in adapter['blue_fighter_sig_str_leg_pct'], \
                "Red/blue_fighter_sig_str_leg_pct"
        
        # Unit testing red/blue fighter sig str distance pct
        assert '%' in adapter['red_fighter_sig_str_distance_pct'] and '%' in adapter['blue_fighter_sig_str_distance_pct'], \
                "Red/blue_fighter_sig_str_distance_pct"
        
        # Unit testing red/blue fighter sig str clinch pct
        assert '%' in adapter['red_fighter_sig_str_clinch_pct'] and '%' in adapter['blue_fighter_sig_str_clinch_pct'], \
                "Red/blue_fighter_sig_str_clinch_pct"
        
        # Unit testing red/blue fighter sig str ground pct
        assert '%' in adapter['red_fighter_sig_str_ground_pct'] and '%' in adapter['blue_fighter_sig_str_ground_pct'], \
                "Red/blue_fighter_sig_str_ground_pct"
