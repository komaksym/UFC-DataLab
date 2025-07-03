# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy


class FightData(scrapy.Item):
    """Schema for UFC fight data with type hints and documentation."""

    # Fight participant information
    red_fighter_name = scrapy.Field()
    blue_fighter_name = scrapy.Field()
    red_fighter_nickname = scrapy.Field()
    blue_fighter_nickname = scrapy.Field()

    # Fight results
    red_fighter_result = scrapy.Field()
    blue_fighter_result = scrapy.Field()
    method = scrapy.Field()
    round = scrapy.Field()
    time = scrapy.Field()
    time_format = scrapy.Field()
    referee = scrapy.Field()
    details = scrapy.Field()
    bout_type = scrapy.Field()
    bonus = scrapy.Field()

    # Event metadata
    event_name = scrapy.Field()
    event_date = scrapy.Field()
    event_location = scrapy.Field()

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
