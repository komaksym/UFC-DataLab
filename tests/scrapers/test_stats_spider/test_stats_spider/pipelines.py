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


class TestStatsScrapingPipeline:
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
        def _test_fight_participant(adapter: ItemAdapter) -> None:
            # Unit testing fighter names
            for name in ["red_fighter_name", "blue_fighter_name"]:
                assert not bool(re.search(r"\d", adapter[name])), (
                    f"Invalid fighter name. Expected no digits, got: {adapter[name]}"
                )
                
        def _test_general_fight_info(adapter: ItemAdapter) -> None:
            # Unit testing fight results
            for result in ["red_fighter_result", "blue_fighter_result"]:
                assert adapter[result] in ["W", "L"], (
                    f"Invalid fight result. Expected 'W' or 'L', got: {adapter[result]}"
                )

            # Unit testing fight result method
            assert adapter['method'] in ['KO/TKO', 'Submission', 'Decision - Unanimous', 
                'Decision - Split', "TKO - Doctor's Stoppage", 'Decision - Majority', 'DQ'], (
                f"Invalid fight method. Expected valid method, got: {adapter['method']}"
            )
            
            # Unit testing fight result round
            assert adapter['round'] in ["1", "2", "3", "4", "5"], (
                f"Invalid fight round. Expected round 1-5, got: {adapter['round']}"
            )

            # Unit testing fight result time
            assert ":" in adapter['time'], (
                f"Invalid time format. Expected MM:SS format, got: {adapter['time']}"
            )

            # Unit testing fight time format
            assert adapter['time_format'] in ['3 Rnd (5-5-5)', '3 Rnd + OT (5-5-5-5)', 
                '5 Rnd (5-5-5-5-5)'], (
                f"Invalid time format. Expected standard format, got: {adapter['time_format']}"
            )

            # Unit testing fight referee
            assert not bool(re.search(r"\d", adapter['referee'])), (
                f"Invalid referee name. Expected no digits, got: {adapter['referee']}"
            )

            # Unit testing fight bout type
            assert "Bout" in adapter['bout_type'], f"Expected bout, got: {adapter['bout_type']}"

            # Unit testing fight bonus
            assert adapter['bonus'] in ['-', 'belt', 'fight', 'perf'], f"Expected a valid bonus value, got: {adapter['bonus']}"

        def _test_event_info(adapter: ItemAdapter) -> None:
            # Unit testing event name
            assert "UFC" in adapter['event_name'], (
                f"Invalid event name. Expected 'UFC' in name, got: {adapter['event_name']}"
            )

            # Unit testing event date
            assert re.match(r"\w+ \d{2}, \d{4}$", adapter['event_date']), (
                f"Invalid date format. Expected MM/DD/YYYY, got: {adapter['event_date']}"
            )
            
            # Unit testing event location
            assert isinstance(adapter['event_location'], str), (
                f"Invalid location type. Expected string, got: {type(adapter['event_location'])}"
            )

        def _test_fight_totals(adapter: ItemAdapter) -> None:
            # Unit testing knockdowns
            assert adapter['red_fighter_KD'].isnumeric() and adapter['blue_fighter_KD'].isnumeric(), (
                f"Invalid knockdown values. Expected numeric, got red: {adapter['red_fighter_KD']}, "
                f"blue: {adapter['blue_fighter_KD']}"
            )

            # Unit testing significant strikes
            assert 'of' in adapter['red_fighter_sig_str'] and 'of' in adapter['blue_fighter_sig_str'], (
                f"Invalid significant strikes format. Expected 'X of Y', got red: {adapter['red_fighter_sig_str']}, "
                f"blue: {adapter['blue_fighter_sig_str']}"
            )

            # Unit testing sig strike percentage
            assert (re.match(r"\d{0,3}", adapter['red_fighter_sig_str_pct'])) \
                or (re.match(r"\d{0,3}", adapter['blue_fighter_sig_str_pct'])), (
                f"Invalid sig strike percentage. Expected % or -, got red: {adapter['red_fighter_sig_str_pct']}, "
                f"blue: {adapter['blue_fighter_sig_str_pct']}"
            )

            # Unit testing total strikes
            assert 'of' in adapter['red_fighter_total_str'] and 'of' in adapter['blue_fighter_total_str'], (
                f"Invalid total strikes format. Expected 'X of Y', got red: {adapter['red_fighter_total_str']}, "
                f"blue: {adapter['blue_fighter_total_str']}"
            )

            # Unit testing takedowns
            assert 'of' in adapter['red_fighter_TD'] and 'of' in adapter['blue_fighter_TD'], (
                f"Invalid takedown format. Expected 'X of Y', got red: {adapter['red_fighter_TD']}, "
                f"blue: {adapter['blue_fighter_TD']}"
            )

            # Unit testing takedown percentage
            assert ("%" in adapter['red_fighter_TD_pct'] or "%" in adapter['blue_fighter_TD_pct']) \
                or ("-" in adapter['red_fighter_TD_pct'] or "-" in adapter['blue_fighter_TD_pct']), (
                f"Invalid takedown percentage. Expected % or -, got red: {adapter['red_fighter_TD_pct']}, "
                f"blue: {adapter['blue_fighter_TD_pct']}"
            )

            # Unit testing submission attempts
            assert adapter['red_fighter_sub_att'].isnumeric() and adapter['blue_fighter_sub_att'].isnumeric(), (
                f"Invalid submission attempts. Expected numeric, got red: {adapter['red_fighter_sub_att']}, "
                f"blue: {adapter['blue_fighter_sub_att']}"
            )

            # Unit testing reversals
            assert adapter['red_fighter_rev'].isnumeric() and adapter['blue_fighter_rev'].isnumeric(), (
                f"Invalid reversal count. Expected numeric, got red: {adapter['red_fighter_rev']}, "
                f"blue: {adapter['blue_fighter_rev']}"
            )

            # Unit testing control time
            assert ":" in adapter['red_fighter_ctrl'] and ":" in adapter['blue_fighter_ctrl'], (
                f"Invalid control time. Expected numeric, got red: {adapter['red_fighter_ctrl']}, "
                f"blue: {adapter['blue_fighter_ctrl']}"
            )

        def _test_fight_sig_str(adapter: ItemAdapter) -> None:
            # Unit testing red/blue fighter sig str head
            assert 'of' in adapter['red_fighter_sig_str_head'] and 'of' in adapter['blue_fighter_sig_str_head'], (
                f"Invalid strike format for head. Expected 'X of Y', got red: {adapter['red_fighter_sig_str_head']}, "
                f"blue: {adapter['blue_fighter_sig_str_head']}"
            )
            
            # Unit testing red/blue fighter sig str body
            assert 'of' in adapter['red_fighter_sig_str_body'] and 'of' in adapter['blue_fighter_sig_str_body'], (
                f"Invalid strike format for body. Expected 'X of Y', got red: {adapter['red_fighter_sig_str_body']}, "
                f"blue: {adapter['blue_fighter_sig_str_body']}"
            )
            
            # Unit testing red/blue fighter sig str leg
            assert 'of' in adapter['red_fighter_sig_str_leg'] and 'of' in adapter['blue_fighter_sig_str_leg'], (
                f"Invalid strike format for leg. Expected 'X of Y', got red: {adapter['red_fighter_sig_str_leg']}, "
                f"blue: {adapter['blue_fighter_sig_str_leg']}"
            )
            
            # Unit testing red/blue fighter sig str distance
            assert 'of' in adapter['red_fighter_sig_str_distance'] and 'of' in adapter['blue_fighter_sig_str_distance'], (
                f"Invalid strike format for distance. Expected 'X of Y', got red: {adapter['red_fighter_sig_str_distance']}, "
                f"blue: {adapter['blue_fighter_sig_str_distance']}"
            )
            
            # Unit testing red/blue fighter sig str clinch
            assert 'of' in adapter['red_fighter_sig_str_clinch'] and 'of' in adapter['blue_fighter_sig_str_clinch'], (
                f"Invalid strike format for clinch. Expected 'X of Y', got red: {adapter['red_fighter_sig_str_clinch']}, "
                f"blue: {adapter['blue_fighter_sig_str_clinch']}"
            )
            
            # Unit testing red/blue fighter sig str ground
            assert 'of' in adapter['red_fighter_sig_str_ground'] and 'of' in adapter['blue_fighter_sig_str_ground'], (
                f"Invalid strike format for ground. Expected 'X of Y', got red: {adapter['red_fighter_sig_str_ground']}, "
                f"blue: {adapter['blue_fighter_sig_str_ground']}"
            )
        
        def _test_sig_str_by_target(adapter: ItemAdapter) -> None:
            # Unit testing red/blue fighter sig str head pct
            assert re.match(r"\d{0,3}", adapter['red_fighter_sig_str_head_pct']) and re.match(r"\d{0,3}", adapter['blue_fighter_sig_str_head_pct']), (
                f"Invalid head strike percentage. Expected %, got red: {adapter['red_fighter_sig_str_head_pct']}, "
                f"blue: {adapter['blue_fighter_sig_str_head_pct']}"
            )
        
            # Unit testing red/blue fighter sig str body pct
            assert re.match(r"\d{0,3}", adapter['red_fighter_sig_str_body_pct']) and re.match(r"\d{0,3}", adapter['blue_fighter_sig_str_body_pct']), (
                f"Invalid body strike percentage. Expected %, got red: {adapter['red_fighter_sig_str_body_pct']}, "
                f"blue: {adapter['blue_fighter_sig_str_body_pct']}"
            )
        
            # Unit testing red/blue fighter sig str leg pct
            assert re.match(r"\d{0,3}", adapter['red_fighter_sig_str_leg_pct']) and re.match(r"\d{0,3}", adapter['blue_fighter_sig_str_leg_pct']), (
                f"Invalid leg strike percentage. Expected %, got red: {adapter['red_fighter_sig_str_leg_pct']}, "
                f"blue: {adapter['blue_fighter_sig_str_leg_pct']}"
            )
        
        def _test_sig_str_by_position(adapter: ItemAdapter) -> None:
            # Unit testing red/blue fighter sig str distance pct
            assert re.match(r"\d{0,3}", adapter['red_fighter_sig_str_distance_pct']) and re.match(r"\d{0,3}", adapter['blue_fighter_sig_str_distance_pct']), (
                f"Invalid distance strike percentage. Expected %, got red: {adapter['red_fighter_sig_str_distance_pct']}, "
                f"blue: {adapter['blue_fighter_sig_str_distance_pct']}"
            )
        
            # Unit testing red/blue fighter sig str clinch pct
            assert re.match(r"\d{0,3}", adapter['red_fighter_sig_str_clinch_pct']) and re.match(r"\d{0,3}", adapter['blue_fighter_sig_str_clinch_pct']), (
                f"Invalid clinch strike percentage. Expected %, got red: {adapter['red_fighter_sig_str_clinch_pct']}, "
                f"blue: {adapter['blue_fighter_sig_str_clinch_pct']}"
            )
        
            # Unit testing red/blue fighter sig str ground pct
            assert re.match(r"\d{0,3}", adapter['red_fighter_sig_str_ground_pct']) and re.match(r"\d{0,3}", adapter['blue_fighter_sig_str_ground_pct']), (
                f"Invalid ground strike percentage. Expected %, got red: {adapter['red_fighter_sig_str_ground_pct']}, "
                f"blue: {adapter['blue_fighter_sig_str_ground_pct']}"
            )
        
        # Using the methods
        _test_fight_participant(adapter)
        _test_general_fight_info(adapter)
        _test_event_info(adapter)
        _test_fight_totals(adapter)
        _test_fight_sig_str(adapter)
        _test_sig_str_by_target(adapter)
        _test_sig_str_by_position(adapter)