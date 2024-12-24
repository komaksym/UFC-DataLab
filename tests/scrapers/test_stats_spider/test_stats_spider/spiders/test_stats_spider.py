import scrapy
from pathlib import Path
from test_stats_spider.items import FightData


class Test_Stats_Spider(scrapy.Spider):
    name = "test_stats_spider"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create a method to generate file URLs
        def create_file_url(relative_path):
            full_path = Path(__file__).parents[2] / relative_path
            return f"file://{full_path.resolve()}"
        
        # Storing mock pages
        self.event_paths = {
            'events_page': create_file_url("dummy_pages_to_scrape/dummy_events_page/events_page.html"),
            'single_event': create_file_url("dummy_pages_to_scrape/dummy_event_page/single_event_page.html"),
            'single_fight': create_file_url("dummy_pages_to_scrape/dummy_fight_page/fight_page.html")
        }     
    
        self.start_urls = [self.event_paths['events_page']]
                           
    def parse(self, response):
        """Extract and follow links to all UFC events."""
        events_links = response.css("a.b-link.b-link_style_black::attr(href)").getall()

        # Checking if all parsed events links are indeed links
        assert all(link.startswith("http://ufcstats.com/event-details/") 
               for link in events_links), (
               f"Invalid event links format. "
               f"Expected: URLs starting with 'http://ufcstats.com/event-details/', "
               f"Got: {[link for link in events_links if not link.startswith('http://ufcstats.com/event-details/')]}"
        )

        return scrapy.Request(url=self.event_paths['single_event'],
                            callback=self.parse_event, 
                            errback=self.handle_error)

    def parse_event(self, response):
        """Extract event data and follow links to individual fights."""
        event_data = {
            "name": response.css("h2.b-content__title span::text").get(),
            "date": response.css("li.b-list__box-list-item:nth-child(1)::text").getall(),
            "location": response.css("li.b-list__box-list-item:nth-child(2)::text").getall()
        }
        fights_links = response.css("a.b-flag.b-flag_style_green::attr(href)").getall()

        # Checking event data
        assert isinstance(event_data['name'], str) and len(event_data['name']) > 4, (
            f"Invalid event name format. "
            f"Expected: String longer than 4 characters, "
            f"Got: {event_data['name']}"
        )
        
        # Checking fight links
        assert all(link.startswith("http://ufcstats.com/fight-details/") 
                  for link in fights_links), (
            f"Invalid fight links format. "
            f"Expected: URLs starting with 'http://ufcstats.com/fight-details/', "
            f"Got: {[link for link in fights_links if not link.startswith('http://ufcstats.com/fight-details/')]}"
        )
        
        return scrapy.Request(url=self.event_paths['single_fight'],
                            callback=self.parse_fight,
                            meta={'event_data': event_data}, 
                            errback=self.handle_error)

    def parse_fight(self, response):
        """Parse individual fight data using more robust selectors."""
        event_data = response.meta["event_data"]
        fight_data_item = FightData()
        general_fight_base_path = "/html/body/section/div/div/div"
        
        fight_data_item["red_fighter_name"] = response.xpath(f"{general_fight_base_path}[1]/div[1]/div/h3/a/text()").get()
        fight_data_item["blue_fighter_name"] = response.xpath(f"{general_fight_base_path}[1]/div[2]/div/h3/a/text()").get()
        fight_data_item["red_fighter_nickname"] = response.xpath(f"{general_fight_base_path}[1]/div[1]/div/p/text()").get()
        fight_data_item["blue_fighter_nickname"] = response.xpath(f"{general_fight_base_path}[1]/div[2]/div/p/text()").get()
        fight_data_item["red_fighter_result"] = response.xpath(f"{general_fight_base_path}[1]/div[1]/i/text()").get()
        fight_data_item["blue_fighter_result"] = response.xpath(f"{general_fight_base_path}[1]/div[2]/i/text()").get()
        fight_data_item["method"] = response.xpath(f"{general_fight_base_path}[2]/div[2]/p[1]/i[1]/i[2]/text()").get()
        fight_data_item["round"] = response.xpath(f"{general_fight_base_path}[2]/div[2]/p[1]/i[2]/text()[2]").get()
        fight_data_item["time"] = response.xpath(f"{general_fight_base_path}[2]/div[2]/p[1]/i[3]/text()[2]").get()
        fight_data_item["time_format"] = response.xpath(f"{general_fight_base_path}[2]/div[2]/p[1]/i[4]/text()[2]").get()
        fight_data_item["referee"] = response.xpath(f"{general_fight_base_path}[2]/div[2]/p[1]/i[5]/span/text()").get()
        fight_data_item["details"] = response.xpath("//p[@class='b-fight-details__text'][2]//text()[normalize-space() and not (contains(., 'Details:'))]").getall()
        fight_data_item["bout_type"] = response.xpath(f"{general_fight_base_path}[2]/div[1]/i/text()").getall()[-1]
        fight_data_item["bonus"] = response.xpath(f"{general_fight_base_path}[2]/div[1]/i/img/@src").get()
        
        # Event data
        fight_data_item['event_name'] = event_data["name"]
        fight_data_item['event_date'] = event_data["date"]
        fight_data_item['event_location'] = event_data["location"]
        
        # Detailed Fight data totals
        detailed_fight_totals_base_path = "/html/body/section/div/div/section[2]/table/tbody/tr/td"
        fight_data_item["red_fighter_KD"] = response.xpath(f"{detailed_fight_totals_base_path}[2]/p[1]/text()").get()
        fight_data_item["blue_fighter_KD"] = response.xpath(f"{detailed_fight_totals_base_path}[2]/p[2]/text()").get()
        fight_data_item["red_fighter_sig_str"] = response.xpath(f"{detailed_fight_totals_base_path}[3]/p[1]/text()").get()
        fight_data_item["blue_fighter_sig_str"] = response.xpath(f"{detailed_fight_totals_base_path}[3]/p[2]/text()").get()
        fight_data_item["red_fighter_sig_str_pct"] = response.xpath(f"{detailed_fight_totals_base_path}[4]/p[1]/text()").get()
        fight_data_item["blue_fighter_sig_str_pct"] = response.xpath(f"{detailed_fight_totals_base_path}[4]/p[2]/text()").get()
        fight_data_item["red_fighter_total_str"] = response.xpath(f"{detailed_fight_totals_base_path}[5]/p[1]/text()").get()
        fight_data_item["blue_fighter_total_str"] = response.xpath(f"{detailed_fight_totals_base_path}[5]/p[2]/text()").get()
        fight_data_item["red_fighter_TD"] = response.xpath(f"{detailed_fight_totals_base_path}[6]/p[1]/text()").get()
        fight_data_item["blue_fighter_TD"] = response.xpath(f"{detailed_fight_totals_base_path}[6]/p[2]/text()").get()
        fight_data_item["red_fighter_TD_pct"] = response.xpath(f"{detailed_fight_totals_base_path}[7]/p[1]/text()").get()
        fight_data_item["blue_fighter_TD_pct"] = response.xpath(f"{detailed_fight_totals_base_path}[7]/p[2]/text()").get()
        fight_data_item["red_fighter_sub_att"] = response.xpath(f"{detailed_fight_totals_base_path}[8]/p[1]/text()").get()
        fight_data_item["blue_fighter_sub_att"] = response.xpath(f"{detailed_fight_totals_base_path}[8]/p[2]/text()").get()
        fight_data_item["red_fighter_rev"] = response.xpath(f"{detailed_fight_totals_base_path}[9]/p[1]/text()").get()
        fight_data_item["blue_fighter_rev"] = response.xpath(f"{detailed_fight_totals_base_path}[9]/p[2]/text()").get()
        fight_data_item["red_fighter_ctrl"] = response.xpath(f"{detailed_fight_totals_base_path}[10]/p[1]/text()").get()
        fight_data_item["blue_fighter_ctrl"] = response.xpath(f"{detailed_fight_totals_base_path}[10]/p[2]/text()").get()
        
        # Detailed Fight data significant strikes
        detailed_fight_sigstr_tar_base_path = "/html/body/section/div/div/table/tbody/tr/td"
        detailed_fight_sigstr_pos_base_path = "/html/body/section/div/div/section[6]/div/div/div[1]/div"
        fight_data_item["red_fighter_sig_str_head"] = response.xpath(f"{detailed_fight_sigstr_tar_base_path}[4]/p[1]/text()").get()
        fight_data_item["blue_fighter_sig_str_head"] = response.xpath(f"{detailed_fight_sigstr_tar_base_path}[4]/p[2]/text()").get()
        fight_data_item["red_fighter_sig_str_body"] = response.xpath(f"{detailed_fight_sigstr_tar_base_path}[5]/p[1]/text()").get()
        fight_data_item["blue_fighter_sig_str_body"] = response.xpath(f"{detailed_fight_sigstr_tar_base_path}[5]/p[2]/text()").get()
        fight_data_item["red_fighter_sig_str_leg"] = response.xpath(f"{detailed_fight_sigstr_tar_base_path}[6]/p[1]/text()").get()
        fight_data_item["blue_fighter_sig_str_leg"] = response.xpath(f"{detailed_fight_sigstr_tar_base_path}[6]/p[2]/text()").get()
        fight_data_item["red_fighter_sig_str_distance"] = response.xpath(f"{detailed_fight_sigstr_tar_base_path}[7]/p[1]/text()").get()
        fight_data_item["blue_fighter_sig_str_distance"] = response.xpath(f"{detailed_fight_sigstr_tar_base_path}[7]/p[2]/text()").get()
        fight_data_item["red_fighter_sig_str_clinch"] = response.xpath(f"{detailed_fight_sigstr_tar_base_path}[8]/p[1]/text()").get()
        fight_data_item["blue_fighter_sig_str_clinch"] = response.xpath(f"{detailed_fight_sigstr_tar_base_path}[8]/p[2]/text()").get()
        fight_data_item["red_fighter_sig_str_ground"] = response.xpath(f"{detailed_fight_sigstr_tar_base_path}[9]/p[1]/text()").get()
        fight_data_item["blue_fighter_sig_str_ground"] = response.xpath(f"{detailed_fight_sigstr_tar_base_path}[9]/p[2]/text()").get()
        # Detailed Fight pct data significant strikes by target
        fight_data_item["red_fighter_sig_str_head_pct"] = response.xpath(f"{detailed_fight_sigstr_pos_base_path}[1]/div/div[2]/div[1]/i[1]/text()").get()
        fight_data_item["blue_fighter_sig_str_head_pct"] = response.xpath(f"{detailed_fight_sigstr_pos_base_path}[1]/div/div[2]/div[1]/i[3]/text()").get()
        fight_data_item["red_fighter_sig_str_body_pct"] = response.xpath(f"{detailed_fight_sigstr_pos_base_path}[1]/div/div[2]/div[2]/i[1]/text()").get()
        fight_data_item["blue_fighter_sig_str_body_pct"] = response.xpath(f"{detailed_fight_sigstr_pos_base_path}[1]/div/div[2]/div[2]/i[3]/text()").get()
        fight_data_item["red_fighter_sig_str_leg_pct"] = response.xpath(f"{detailed_fight_sigstr_pos_base_path}[1]/div/div[2]/div[3]/i[1]/text()").get()
        fight_data_item["blue_fighter_sig_str_leg_pct"] = response.xpath(f"{detailed_fight_sigstr_pos_base_path}[1]/div/div[2]/div[3]/i[3]/text()").get()
        # Detailed Fight pct data significant strikes by position
        fight_data_item["red_fighter_sig_str_distance_pct"] = response.xpath(f"{detailed_fight_sigstr_pos_base_path}[2]/div/div[2]/div[1]/i[1]/text()").get()
        fight_data_item["blue_fighter_sig_str_distance_pct"] = response.xpath(f"{detailed_fight_sigstr_pos_base_path}[2]/div/div[2]/div[1]/i[3]/text()").get()
        fight_data_item["red_fighter_sig_str_clinch_pct"] = response.xpath(f"{detailed_fight_sigstr_pos_base_path}[2]/div/div[2]/div[2]/i[1]/text()").get()
        fight_data_item["blue_fighter_sig_str_clinch_pct"] = response.xpath(f"{detailed_fight_sigstr_pos_base_path}[2]/div/div[2]/div[2]/i[3]/text()").get()
        fight_data_item["red_fighter_sig_str_ground_pct"] = response.xpath(f"{detailed_fight_sigstr_pos_base_path}[2]/div/div[2]/div[3]/i[1]/text()").get()
        fight_data_item["blue_fighter_sig_str_ground_pct"] = response.xpath(f"{detailed_fight_sigstr_pos_base_path}[2]/div/div[2]/div[3]/i[3]/text()").get()

        yield fight_data_item

    def handle_error(self, failure):
        """Handle request failures"""
        self.logger.error(f"Request failed: {failure.request.url}")
        self.logger.error(f"Error: {failure.value}")