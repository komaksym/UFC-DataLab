import pdb
import scrapy
from ..items import FightData


class UFCSpider(scrapy.Spider):
    name = "ufc_spider"
    allowed_domains = ["ufcstats.com"]
    start_urls = ["http://ufcstats.com/statistics/events/completed?page=all"]

    # Add constants for commonly used XPath bases
    GENERAL_FIGHT_BASE_PATH = "/html/body/section/div/div/div"
    DETAILED_TOTALS_BASE_PATH = "/html/body/section/div/div/section[2]/table/tbody/tr/td"
    SIGSTR_TARGET_BASE_PATH = "/html/body/section/div/div/table/tbody/tr/td"
    SIGSTR_POS_BASE_PATH = "/html/body/section/div/div/section[6]/div/div/div[1]/div"

    def _safe_extract(self, response, xpath: str, default: str = "-") -> str:
        """Helper method to safely extract XPath data with a default value"""
        return response.xpath(xpath).get(default)

    def _extract_fighter_data(self, response, base_path: str, side: str) -> dict:
        """Helper method to extract fighter-specific data"""
        idx = "1" if side == "red" else "2"
        return {
            f"{side}_fighter_name": self._safe_extract(f"{base_path}[1]/div[{idx}]/div/h3/a/text()"),
            f"{side}_fighter_nickname": self._safe_extract(f"{base_path}[1]/div[{idx}]/div/p/text()"),
            f"{side}_fighter_result": self._safe_extract(f"{base_path}[1]/div[{idx}]/i/text()")
        }

    def parse(self, response):
        """Events and fights page"""
        
        # Extract links to all UFC events
        events_links = response.xpath("//a[@class='b-link b-link_style_black']/@href").getall()
        # Go through each event
        for event_link in events_links:
            yield scrapy.Request(url=event_link, callback=self.parse_event)

    def parse_event(self, response):
        # Scraping the event data
        event_data = {}
        event_data_base_path = "/html/body/section/div/"
        event_data["event"] = response.xpath(f"{event_data_base_path}h2/span/text()").get("-")
        event_data["date"] = response.xpath(f"{event_data_base_path}div/div[1]/ul/li[1]/text()[normalize-space()]").get("-")
        event_data["location"] = response.xpath(f"{event_data_base_path}div/div[1]/ul/li[2]/text()[normalize-space()]").get("-")

        # Extract links of each individual fight in that event
        fights_links = response.xpath("//a[@class='b-flag b-flag_style_green']/@href").getall()
        # Go through each fight
        for fight_link in fights_links:
            yield scrapy.Request(url=fight_link, callback=self.parse_fight, meta={"event_data": event_data})

    def parse_fight(self, response):
        """Parse each individual fight matchup"""
        event_data = response.meta["event_data"]
        fight_data_item = FightData()

        # Extract basic fighter data
        red_fighter_data = self._extract_fighter_data(response, self.GENERAL_FIGHT_BASE_PATH, "red")
        blue_fighter_data = self._extract_fighter_data(response, self.GENERAL_FIGHT_BASE_PATH, "blue")
        fight_data_item.update(red_fighter_data)
        fight_data_item.update(blue_fighter_data)

        # Extract fight details
        fight_data_item.update({
            "method": self._safe_extract(f"{self.GENERAL_FIGHT_BASE_PATH}[2]/div[2]/p[1]/i[1]/i[2]/text()"),
            "round": self._safe_extract(f"{self.GENERAL_FIGHT_BASE_PATH}[2]/div[2]/p[1]/i[2]/text()[2]"),
            "time": self._safe_extract(f"{self.GENERAL_FIGHT_BASE_PATH}[2]/div[2]/p[1]/i[3]/text()[2]"),
            "time_format": self._safe_extract(f"{self.GENERAL_FIGHT_BASE_PATH}[2]/div[2]/p[1]/i[4]/text()[2]"),
            "referee": self._safe_extract(f"{self.GENERAL_FIGHT_BASE_PATH}[2]/div[2]/p[1]/i[5]/span/text()"),
            "details": response.xpath("//p[@class='b-fight-details__text'][2]//text()[normalize-space() and not (contains(., 'Details:'))]").getall(),
            "bout_type": self._safe_extract(f"{self.GENERAL_FIGHT_BASE_PATH}[2]/div[1]/i/text()[-1]"),
            "bonus": self._safe_extract(f"{self.GENERAL_FIGHT_BASE_PATH}[2]/div[1]/i/img/@src")
        })

        # Add event data
        fight_data_item.update(event_data)

        # Detailed Fight data totals
        fight_data_item["red_fighter_KD"] = self._safe_extract(f"{self.DETAILED_TOTALS_BASE_PATH}[2]/p[1]/text()")
        fight_data_item["blue_fighter_KD"] = self._safe_extract(f"{self.DETAILED_TOTALS_BASE_PATH}[2]/p[2]/text()")
        fight_data_item["red_fighter_sig_str"] = self._safe_extract(f"{self.DETAILED_TOTALS_BASE_PATH}[3]/p[1]/text()")
        fight_data_item["blue_fighter_sig_str"] = self._safe_extract(f"{self.DETAILED_TOTALS_BASE_PATH}[3]/p[2]/text()")
        fight_data_item["red_fighter_sig_str_pct"] = self._safe_extract(f"{self.DETAILED_TOTALS_BASE_PATH}[4]/p[1]/text()")
        fight_data_item["blue_fighter_sig_str_pct"] = self._safe_extract(f"{self.DETAILED_TOTALS_BASE_PATH}[4]/p[2]/text()")
        fight_data_item["red_fighter_total_str"] = self._safe_extract(f"{self.DETAILED_TOTALS_BASE_PATH}[5]/p[1]/text()")
        fight_data_item["blue_fighter_total_str"] = self._safe_extract(f"{self.DETAILED_TOTALS_BASE_PATH}[5]/p[2]/text()")
        fight_data_item["red_fighter_TD"] = self._safe_extract(f"{self.DETAILED_TOTALS_BASE_PATH}[6]/p[1]/text()")
        fight_data_item["blue_fighter_TD"] = self._safe_extract(f"{self.DETAILED_TOTALS_BASE_PATH}[6]/p[2]/text()")
        fight_data_item["red_fighter_TD_pct"] = self._safe_extract(f"{self.DETAILED_TOTALS_BASE_PATH}[7]/p[1]/text()")
        fight_data_item["blue_fighter_TD_pct"] = self._safe_extract(f"{self.DETAILED_TOTALS_BASE_PATH}[7]/p[2]/text()")
        fight_data_item["red_fighter_sub_att"] = self._safe_extract(f"{self.DETAILED_TOTALS_BASE_PATH}[8]/p[1]/text()")
        fight_data_item["blue_fighter_sub_att"] = self._safe_extract(f"{self.DETAILED_TOTALS_BASE_PATH}[8]/p[2]/text()")
        fight_data_item["red_fighter_rev"] = self._safe_extract(f"{self.DETAILED_TOTALS_BASE_PATH}[9]/p[1]/text()")
        fight_data_item["blue_fighter_rev"] = self._safe_extract(f"{self.DETAILED_TOTALS_BASE_PATH}[9]/p[2]/text()")
        fight_data_item["red_fighter_ctrl"] = self._safe_extract(f"{self.DETAILED_TOTALS_BASE_PATH}[10]/p[1]/text()")
        fight_data_item["blue_fighter_ctrl"] = self._safe_extract(f"{self.DETAILED_TOTALS_BASE_PATH}[10]/p[2]/text()")
        
        # Detailed Fight data significant strikes
        fight_data_item["red_fighter_sig_str_head"] = self._safe_extract(f"{self.SIGSTR_TARGET_BASE_PATH}[4]/p[1]/text()")
        fight_data_item["blue_fighter_sig_str_head"] = self._safe_extract(f"{self.SIGSTR_TARGET_BASE_PATH}[4]/p[2]/text()")
        fight_data_item["red_fighter_sig_str_body"] = self._safe_extract(f"{self.SIGSTR_TARGET_BASE_PATH}[5]/p[1]/text()")
        fight_data_item["blue_fighter_sig_str_body"] = self._safe_extract(f"{self.SIGSTR_TARGET_BASE_PATH}[5]/p[2]/text()")
        fight_data_item["red_fighter_sig_str_leg"] = self._safe_extract(f"{self.SIGSTR_TARGET_BASE_PATH}[6]/p[1]/text()")
        fight_data_item["blue_fighter_sig_str_leg"] = self._safe_extract(f"{self.SIGSTR_TARGET_BASE_PATH}[6]/p[2]/text()")
        fight_data_item["red_fighter_sig_str_distance"] = self._safe_extract(f"{self.SIGSTR_TARGET_BASE_PATH}[7]/p[1]/text()")
        fight_data_item["blue_fighter_sig_str_distance"] = self._safe_extract(f"{self.SIGSTR_TARGET_BASE_PATH}[7]/p[2]/text()")
        fight_data_item["red_fighter_sig_str_clinch"] = self._safe_extract(f"{self.SIGSTR_TARGET_BASE_PATH}[8]/p[1]/text()")
        fight_data_item["blue_fighter_sig_str_clinch"] = self._safe_extract(f"{self.SIGSTR_TARGET_BASE_PATH}[8]/p[2]/text()")
        fight_data_item["red_fighter_sig_str_ground"] = self._safe_extract(f"{self.SIGSTR_TARGET_BASE_PATH}[9]/p[1]/text()")
        fight_data_item["blue_fighter_sig_str_ground"] = self._safe_extract(f"{self.SIGSTR_TARGET_BASE_PATH}[9]/p[2]/text()")
        # Detailed Fight pct data significant strikes by target
        fight_data_item["red_fighter_sig_str_head_pct"] = self._safe_extract(f"{self.SIGSTR_POS_BASE_PATH}[1]/div/div[2]/div[1]/i[1]/text()")
        fight_data_item["blue_fighter_sig_str_head_pct"] = self._safe_extract(f"{self.SIGSTR_POS_BASE_PATH}[1]/div/div[2]/div[1]/i[3]/text()")
        fight_data_item["red_fighter_sig_str_body_pct"] = self._safe_extract(f"{self.SIGSTR_POS_BASE_PATH}[1]/div/div[2]/div[2]/i[1]/text()")
        fight_data_item["blue_fighter_sig_str_body_pct"] = self._safe_extract(f"{self.SIGSTR_POS_BASE_PATH}[1]/div/div[2]/div[2]/i[3]/text()")
        fight_data_item["red_fighter_sig_str_leg_pct"] = self._safe_extract(f"{self.SIGSTR_POS_BASE_PATH}[1]/div/div[2]/div[3]/i[1]/text()")
        fight_data_item["blue_fighter_sig_str_leg_pct"] = self._safe_extract(f"{self.SIGSTR_POS_BASE_PATH}[1]/div/div[2]/div[3]/i[3]/text()")
        # Detailed Fight pct data significant strikes by position
        fight_data_item["red_fighter_sig_str_distance_pct"] = self._safe_extract(f"{self.SIGSTR_POS_BASE_PATH}[2]/div/div[2]/div[1]/i[1]/text()")
        fight_data_item["blue_fighter_sig_str_distance_pct"] = self._safe_extract(f"{self.SIGSTR_POS_BASE_PATH}[2]/div/div[2]/div[1]/i[3]/text()")
        fight_data_item["red_fighter_sig_str_clinch_pct"] = self._safe_extract(f"{self.SIGSTR_POS_BASE_PATH}[2]/div/div[2]/div[2]/i[1]/text()")
        fight_data_item["blue_fighter_sig_str_clinch_pct"] = self._safe_extract(f"{self.SIGSTR_POS_BASE_PATH}[2]/div/div[2]/div[2]/i[3]/text()")
        fight_data_item["red_fighter_sig_str_ground_pct"] = self._safe_extract(f"{self.SIGSTR_POS_BASE_PATH}[2]/div/div[2]/div[3]/i[1]/text()")
        fight_data_item["blue_fighter_sig_str_ground_pct"] = self._safe_extract(f"{self.SIGSTR_POS_BASE_PATH}[2]/div/div[2]/div[3]/i[3]/text()")

        yield fight_data_item 