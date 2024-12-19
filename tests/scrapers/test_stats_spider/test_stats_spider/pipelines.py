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
        # Unit testing fighter names
        for name in ["red_fighter_name", "blue_fighter_name"]:
            assert bool(re.match(r"^\w+ \w+$", adapter.get(name))), "Fighter name test has failed"
        
        # Unit testing fight results
        for result in ["red_fighter_result", "blue_fighter_result"]:
            assert adapter[result] in ["W", "L"], "Fighter result test has failed"

        # Unit testing fight result method
        assert adapter['method'] in []
        
