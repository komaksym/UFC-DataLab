import scrapy
import logging
from typing import Generator, Dict, Any
from datetime import datetime
from ..items import FightData


logger = logging.getLogger(__name__)


class UFCSpider(scrapy.Spider):
    """Spider for scraping UFC fight statistics."""
    
    name = "ufc_spider"
    allowed_domains = ["ufcstats.com"]
    start_urls = ["http://ufcstats.com/statistics/events/completed?page=all"]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.events_processed = 0
        self.fights_processed = 0
        
    def start_requests(self) -> Generator:
        """Initialize requests with custom headers."""
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; UFCStats/1.0; +http://example.com)',
        }
        for url in self.start_urls:
            yield scrapy.Request(url=url, headers=headers, callback=self.parse)

    def parse(self, response: scrapy.http.Response) -> Generator:
        """Parse the events listing page."""
        try:
            events_links = response.xpath("//a[@class='b-link b-link_style_black']/@href").getall()
            logger.info(f"Found {len(events_links)} events to process")
            
            for event_link in events_links:
                yield scrapy.Request(
                    url=event_link,
                    callback=self.parse_event,
                    errback=self.handle_error,
                    meta={'dont_retry': False}
                )
        except Exception as e:
            logger.error(f"Error parsing events page: {str(e)}")
            
    def parse_event(self, response: scrapy.http.Response) -> Generator:
        """Parse individual event pages."""
        try:
            event_data = self._extract_event_data(response)
            self.events_processed += 1
            
            fights_links = response.xpath("//a[@class='b-flag b-flag_style_green']/@href").getall()
            logger.debug(f"Found {len(fights_links)} fights for event: {event_data['event']}")
            
            for fight_link in fights_links:
                yield scrapy.Request(
                    url=fight_link,
                    callback=self.parse_fight,
                    errback=self.handle_error,
                    meta={'event_data': event_data}
                )
        except Exception as e:
            logger.error(f"Error parsing event page: {str(e)}")
            
    def parse_fight(self, response: scrapy.http.Response) -> Generator:
        """Parse individual fight pages."""
        try:
            fight_data = FightData()
            event_data = response.meta["event_data"]
            
            self._extract_general_fight_data(response, fight_data)
            self._extract_fight_totals(response, fight_data)
            self._extract_significant_strikes(response, fight_data)
            
            # Add event metadata
            fight_data.update(event_data)
            
            self.fights_processed += 1
            yield fight_data
            
        except Exception as e:
            logger.error(f"Error parsing fight page: {str(e)}")
            
    def _extract_event_data(self, response: scrapy.http.Response) -> Dict[str, str]:
        """Extract event metadata."""
        base_path = "/html/body/section/div/"
        return {
            "event": response.xpath(f"{base_path}h2/span/text()").get("-"),
            "date": response.xpath(f"{base_path}div/div[1]/ul/li[1]/text()[normalize-space()]").get("-"),
            "location": response.xpath(f"{base_path}div/div[1]/ul/li[2]/text()[normalize-space()]").get("-")
        }
    
    def _extract_general_fight_data(self, response: scrapy.http.Response, fight_data: FightData) -> None:
        """Extract general fight information."""
        base_path = "/html/body/section/div/div/div"
        
        # Fighter names and nicknames
        fight_data["red_fighter_name"] = response.xpath(f"{base_path}[1]/div[1]/div/h3/a/text()").get("-")
        fight_data["blue_fighter_name"] = response.xpath(f"{base_path}[1]/div[2]/div/h3/a/text()").get("-")
        fight_data["red_fighter_nickname"] = response.xpath(f"{base_path}[1]/div[1]/div/p/text()").get("-")
        fight_data["blue_fighter_nickname"] = response.xpath(f"{base_path}[1]/div[2]/div/p/text()").get("-")
        
        # Fight results
        fight_data["red_fighter_result"] = response.xpath(f"{base_path}[1]/div[1]/i/text()").get("-")
        fight_data["blue_fighter_result"] = response.xpath(f"{base_path}[1]/div[2]/i/text()").get("-")
        
        # Fight details
        fight_data["method"] = response.xpath(f"{base_path}[2]/div[2]/p[1]/i[1]/i[2]/text()").get("-")
        fight_data["round"] = response.xpath(f"{base_path}[2]/div[2]/p[1]/i[2]/text()[2]").get("-")
        fight_data["time"] = response.xpath(f"{base_path}[2]/div[2]/p[1]/i[3]/text()[2]").get("-")
        fight_data["time_format"] = response.xpath(f"{base_path}[2]/div[2]/p[1]/i[4]/text()[2]").get("-")
        fight_data["referee"] = response.xpath(f"{base_path}[2]/div[2]/p[1]/i[5]/span/text()").get("-")
        
        # Additional details
        fight_data["details"] = response.xpath("//p[@class='b-fight-details__text'][2]//text()[normalize-space() and not (contains(., 'Details:'))]").getall()
        fight_data["bout_type"] = response.xpath(f"{base_path}[2]/div[1]/i/text()").getall()[-1]
        fight_data["bonus"] = response.xpath(f"{base_path}[2]/div[1]/i/img/@src").get("-")

    def _extract_fight_totals(self, response: scrapy.http.Response, fight_data: FightData) -> None:
        """Extract fight total statistics."""
        base_path = "/html/body/section/div/div/section[2]/table/tbody/tr/td"
        
        # Dictionary mapping of field names to their XPath indices
        total_stats = {
            "KD": 2,
            "sig_str": 3,
            "sig_str_pct": 4,
            "total_str": 5,
            "TD": 6,
            "TD_pct": 7,
            "sub_att": 8,
            "rev": 9,
            "ctrl": 10
        }
        
        # Extract all total statistics
        for stat, index in total_stats.items():
            fight_data[f"red_fighter_{stat}"] = response.xpath(f"{base_path}[{index}]/p[1]/text()").get("-")
            fight_data[f"blue_fighter_{stat}"] = response.xpath(f"{base_path}[{index}]/p[2]/text()").get("-")

    def _extract_significant_strikes(self, response: scrapy.http.Response, fight_data: FightData) -> None:
        """Extract significant strike statistics."""
        target_base_path = "/html/body/section/div/div/table/tbody/tr/td"
        position_base_path = "/html/body/section/div/div/section[6]/div/div/div[1]/div"
        
        # Target statistics (head, body, leg)
        target_stats = {
            "head": 4,
            "body": 5,
            "leg": 6,
            "distance": 7,
            "clinch": 8,
            "ground": 9
        }
        
        # Extract strike statistics by target
        for target, index in target_stats.items():
            fight_data[f"red_fighter_sig_str_{target}"] = response.xpath(f"{target_base_path}[{index}]/p[1]/text()").get("-")
            fight_data[f"blue_fighter_sig_str_{target}"] = response.xpath(f"{target_base_path}[{index}]/p[2]/text()").get("-")
        
        # Extract percentage statistics for strike targets
        target_positions = ["head", "body", "leg"]
        for i, target in enumerate(target_positions, 1):
            fight_data[f"red_fighter_sig_str_{target}_pct"] = response.xpath(f"{position_base_path}[1]/div/div[2]/div[{i}]/i[1]/text()").get("-")
            fight_data[f"blue_fighter_sig_str_{target}_pct"] = response.xpath(f"{position_base_path}[1]/div/div[2]/div[{i}]/i[3]/text()").get("-")
        
        # Extract percentage statistics for strike positions
        strike_positions = ["distance", "clinch", "ground"]
        for i, position in enumerate(strike_positions, 1):
            fight_data[f"red_fighter_sig_str_{position}_pct"] = response.xpath(f"{position_base_path}[2]/div/div[2]/div[{i}]/i[1]/text()").get("-")
            fight_data[f"blue_fighter_sig_str_{position}_pct"] = response.xpath(f"{position_base_path}[2]/div/div[2]/div[{i}]/i[3]/text()").get("-")
        
    def handle_error(self, failure):
        """Handle request failures."""
        logger.error(f"Request failed: {failure.value}")