# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy
from typing import Dict, Any, Optional


class BaseItem(scrapy.Item):
    """Base class for scraped items with common validation methods."""
    
    def clean_field(self, field_name: str) -> None:
        """Clean individual field values."""
        if field_name in self:
            value = self[field_name]
            if isinstance(value, str):
                self[field_name] = value.strip()


class FightData(BaseItem):
    """Schema for UFC fight data with type hints and documentation."""
    
    # Fight participant information
    red_fighter_name: str = scrapy.Field()
    blue_fighter_name: str = scrapy.Field()
    red_fighter_nickname: Optional[str] = scrapy.Field()
    blue_fighter_nickname: Optional[str] = scrapy.Field()
    
    # Fight results
    red_fighter_result: str = scrapy.Field()
    blue_fighter_result: str = scrapy.Field()
    method: str = scrapy.Field()
    round: str = scrapy.Field()
    time: str = scrapy.Field()
    time_format: str = scrapy.Field()
    referee: str = scrapy.Field()
    details: str = scrapy.Field()
    bout_type: str = scrapy.Field()
    bonus: Optional[str] = scrapy.Field()
    
    # Event metadata
    event_name: str = scrapy.Field()
    event_date: str = scrapy.Field()
    event_location: str = scrapy.Field()
    
   # Detailed Fight data totals
    red_fighter_KD = scrapy.Field()
    blue_fighter_KD = scrapy.Field()
    red_fighter_sig_str = scrapy.Field()
    blue_fighter_sig_str = scrapy.Field()
    red_fighter_sig_str_pct = scrapy.Field()
    blue_fighter_sig_str_pct = scrapy.Field()
    red_fighter_total_str = scrapy.Field()
    blue_fighter_total_str = scrapy.Field()
    red_fighter_TD = scrapy.Field()
    blue_fighter_TD = scrapy.Field()
    red_fighter_TD_pct = scrapy.Field()
    blue_fighter_TD_pct = scrapy.Field()
    red_fighter_sub_att = scrapy.Field()
    blue_fighter_sub_att = scrapy.Field()
    red_fighter_rev = scrapy.Field()
    blue_fighter_rev = scrapy.Field()
    red_fighter_ctrl = scrapy.Field()
    blue_fighter_ctrl = scrapy.Field()

    # Detailed Fight data significant strikes
    red_fighter_sig_str_head = scrapy.Field()
    blue_fighter_sig_str_head = scrapy.Field()
    red_fighter_sig_str_body = scrapy.Field()
    blue_fighter_sig_str_body = scrapy.Field()
    red_fighter_sig_str_leg = scrapy.Field()
    blue_fighter_sig_str_leg = scrapy.Field()
    red_fighter_sig_str_distance = scrapy.Field()
    blue_fighter_sig_str_distance = scrapy.Field()
    red_fighter_sig_str_clinch = scrapy.Field()
    blue_fighter_sig_str_clinch = scrapy.Field()
    red_fighter_sig_str_ground = scrapy.Field()
    blue_fighter_sig_str_ground = scrapy.Field()

    # Detailed Fight pct data significant strikes by target
    red_fighter_sig_str_head_pct = scrapy.Field()
    blue_fighter_sig_str_head_pct = scrapy.Field()
    red_fighter_sig_str_body_pct = scrapy.Field()
    blue_fighter_sig_str_body_pct = scrapy.Field()
    red_fighter_sig_str_leg_pct = scrapy.Field()
    blue_fighter_sig_str_leg_pct = scrapy.Field()

    # Detailed Fight pct data significant strikes by position
    red_fighter_sig_str_distance_pct = scrapy.Field()
    blue_fighter_sig_str_distance_pct = scrapy.Field()
    red_fighter_sig_str_clinch_pct = scrapy.Field()
    blue_fighter_sig_str_clinch_pct = scrapy.Field()
    red_fighter_sig_str_ground_pct = scrapy.Field()
    blue_fighter_sig_str_ground_pct = scrapy.Field()