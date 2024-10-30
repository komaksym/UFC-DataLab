import pdb
import scrapy
from ..items import EventData, GeneralFightData, \
                    DetailedFightData_Totals, DetailedFightData_Sig_strikes 


class UFCSpider(scrapy.Spider):
    name = "ufc_spider"
    allowed_domains = ["ufcstats.com"]
    start_urls = ["http://ufcstats.com/statistics/events/completed?page=all"]

    def parse(self, response):
        """Events and fights page"""
        events_links = response.xpath("//a[@class='b-link b-link_style_black']/@href").getall()[:2]
        events_links.reverse()
        for event_link in events_links:
            yield scrapy.Request(url=event_link, callback=self.parse_event)

    def parse_event(self, response):
        # Scraping the event data
        event_data = {}
        event_data_base_path = "/html/body/section/div/"
        event_data["event"] = response.xpath(f"{event_data_base_path}h2/span/text()").get()
        event_data["date"] = response.xpath(f"{event_data_base_path}div/div[1]/ul/li[1]/text()[normalize-space()]").get()
        event_data["location"] = response.xpath(f"{event_data_base_path}div/div[1]/ul/li[2]/text()[normalize-space()]").get()

        # Extract links of each individual fight in that event
        fights_links = response.xpath("//a[@class='b-flag b-flag_style_green']/@href").getall()[::-1]
        for fight_link in fights_links:
            yield scrapy.Request(url=fight_link, callback=self.parse_fight, meta={"event_data": event_data})

    def parse_fight(self, response):
        event_data_item = response.meta["event_data"]

        """Parse each individual fight matchup"""
        # General fight data
        general_fight_data_item = GeneralFightData()
        general_fight_base_path = "/html/body/section/div/div/div"

        general_fight_data_item["red_fighter_name"] = response.xpath(f"{general_fight_base_path}[1]/div[1]/div/h3/a/text()").get()
        general_fight_data_item["blue_fighter_name"] = response.xpath(f"{general_fight_base_path}[1]/div[2]/div/h3/a/text()").get()
        general_fight_data_item["red_fighter_nickname"] = response.xpath(f"{general_fight_base_path}[1]/div[1]/div/p/text()").get()
        general_fight_data_item["blue_fighter_nickname"] = response.xpath(f"{general_fight_base_path}[1]/div[2]/div/p/text()").get()
        general_fight_data_item["red_fighter_result"] = response.xpath(f"{general_fight_base_path}[1]/div[1]/i/text()").get()
        general_fight_data_item["blue_fighter_result"] = response.xpath(f"{general_fight_base_path}[1]/div[2]/i/text()").get()
        general_fight_data_item["method"] = response.xpath(f"{general_fight_base_path}[2]/div[2]/p[1]/i[1]/i[2]/text()").get()
        general_fight_data_item["round"] = response.xpath(f"{general_fight_base_path}[2]/div[2]/p[1]/i[2]/text()[2]").get()
        general_fight_data_item["time"] = response.xpath(f"{general_fight_base_path}[2]/div[2]/p[1]/i[3]/text()[2]").get()
        general_fight_data_item["time_format"] = response.xpath(f"{general_fight_base_path}[2]/div[2]/p[1]/i[3]/text()[2]").get()
        general_fight_data_item["referee"] = response.xpath(f"{general_fight_base_path}[2]/div[2]/p[1]/i[5]/span/text()").get()
        general_fight_data_item["details"] = response.xpath("//p[@class='b-fight-details__text'][2]//text()[normalize-space() and not (contains(., 'Details:'))]").getall()
        general_fight_data_item["bout_type"] = response.xpath(f"{general_fight_base_path}[2]/div[1]/i/text()").getall()[-1]
        general_fight_data_item["bonus"] = response.xpath(f"{general_fight_base_path}[2]/div[1]/i/img/@src").get("-")

        general_fight_data_item['event_name'] = event_data_item["event"]
        general_fight_data_item['event_date'] = event_data_item["date"]
        general_fight_data_item['event_location'] = event_data_item["location"]
        yield general_fight_data_item

        # Detailed Fight data totals
        detailed_fight_data_totals_item = DetailedFightData_Totals()
        detailed_fight_totals_base_path = "/html/body/section/div/div/section[2]/table/tbody/tr/td"

        detailed_fight_data_totals_item["red_fighter_KD"] = response.xpath(f"{detailed_fight_totals_base_path}[2]/p[1]/text()").get()
        detailed_fight_data_totals_item["blue_fighter_KD"] = response.xpath(f"{detailed_fight_totals_base_path}[2]/p[2]/text()").get()
        detailed_fight_data_totals_item["red_fighter_sig_str"] = response.xpath(f"{detailed_fight_totals_base_path}[3]/p[1]/text()").get()
        detailed_fight_data_totals_item["blue_fighter_sig_str"] = response.xpath(f"{detailed_fight_totals_base_path}[3]/p[2]/text()").get()
        detailed_fight_data_totals_item["red_fighter_sig_str_pct"] = response.xpath(f"{detailed_fight_totals_base_path}[4]/p[1]/text()").get()
        detailed_fight_data_totals_item["blue_fighter_sig_str_pct"] = response.xpath(f"{detailed_fight_totals_base_path}[4]/p[2]/text()").get()
        detailed_fight_data_totals_item["red_fighter_total_str"] = response.xpath(f"{detailed_fight_totals_base_path}[5]/p[1]/text()").get()
        detailed_fight_data_totals_item["blue_fighter_total_str"] = response.xpath(f"{detailed_fight_totals_base_path}[5]/p[2]/text()").get()
        detailed_fight_data_totals_item["red_fighter_TD"] = response.xpath(f"{detailed_fight_totals_base_path}[6]/p[1]/text()").get()
        detailed_fight_data_totals_item["blue_fighter_TD"] = response.xpath(f"{detailed_fight_totals_base_path}[6]/p[2]/text()").get()
        detailed_fight_data_totals_item["red_fighter_TD_pct"] = response.xpath(f"{detailed_fight_totals_base_path}[7]/p[1]/text()").get()
        detailed_fight_data_totals_item["blue_fighter_TD_pct"] = response.xpath(f"{detailed_fight_totals_base_path}[7]/p[2]/text()").get()
        detailed_fight_data_totals_item["red_fighter_sub_att"] = response.xpath(f"{detailed_fight_totals_base_path}[8]/p[1]/text()").get()
        detailed_fight_data_totals_item["blue_fighter_sub_att"] = response.xpath(f"{detailed_fight_totals_base_path}[8]/p[2]/text()").get()
        detailed_fight_data_totals_item["red_fighter_rev"] = response.xpath(f"{detailed_fight_totals_base_path}[9]/p[1]/text()").get()
        detailed_fight_data_totals_item["blue_fighter_rev"] = response.xpath(f"{detailed_fight_totals_base_path}[9]/p[2]/text()").get()
        detailed_fight_data_totals_item["red_fighter_ctrl"] = response.xpath(f"{detailed_fight_totals_base_path}[10]/p[1]/text()").get()
        detailed_fight_data_totals_item["blue_fighter_ctrl"] = response.xpath(f"{detailed_fight_totals_base_path}[10]/p[2]/text()").get()
        yield detailed_fight_data_totals_item
        
        # Detailed Fight data significant strikes
        detailed_fight_data_sigstr_item = DetailedFightData_Sig_strikes()
        detailed_fight_sigstr_tar_base_path = "/html/body/section/div/div/table/tbody/tr/td"
        detailed_fight_sigstr_pos_base_path = "/html/body/section/div/div/section[6]/div/div/div[1]/div"

        detailed_fight_data_sigstr_item["red_fighter_sig_str_head"] = response.xpath(f"{detailed_fight_sigstr_tar_base_path}[4]/p[1]/text()").get()
        detailed_fight_data_sigstr_item["blue_fighter_sig_str_head"] = response.xpath(f"{detailed_fight_sigstr_tar_base_path}[4]/p[2]/text()").get()
        detailed_fight_data_sigstr_item["red_fighter_sig_str_body"] = response.xpath(f"{detailed_fight_sigstr_tar_base_path}[5]/p[1]/text()").get()
        detailed_fight_data_sigstr_item["blue_fighter_sig_str_body"] = response.xpath(f"{detailed_fight_sigstr_tar_base_path}[5]/p[2]/text()").get()
        detailed_fight_data_sigstr_item["red_fighter_sig_str_leg"] = response.xpath(f"{detailed_fight_sigstr_tar_base_path}[6]/p[1]/text()").get()
        detailed_fight_data_sigstr_item["blue_fighter_sig_str_leg"] = response.xpath(f"{detailed_fight_sigstr_tar_base_path}[6]/p[2]/text()").get()
        detailed_fight_data_sigstr_item["red_fighter_sig_str_distance"] = response.xpath(f"{detailed_fight_sigstr_tar_base_path}[7]/p[1]/text()").get()
        detailed_fight_data_sigstr_item["blue_fighter_sig_str_distance"] = response.xpath(f"{detailed_fight_sigstr_tar_base_path}[7]/p[2]/text()").get()
        detailed_fight_data_sigstr_item["red_fighter_sig_str_clinch"] = response.xpath(f"{detailed_fight_sigstr_tar_base_path}[8]/p[1]/text()").get()
        detailed_fight_data_sigstr_item["blue_fighter_sig_str_clinch"] = response.xpath(f"{detailed_fight_sigstr_tar_base_path}[8]/p[2]/text()").get()
        detailed_fight_data_sigstr_item["red_fighter_sig_str_ground"] = response.xpath(f"{detailed_fight_sigstr_tar_base_path}[9]/p[1]/text()").get()
        detailed_fight_data_sigstr_item["blue_fighter_sig_str_ground"] = response.xpath(f"{detailed_fight_sigstr_tar_base_path}[9]/p[2]/text()").get()
        detailed_fight_data_sigstr_item["red_fighter_sig_str_head_pct"] = response.xpath(f"{detailed_fight_sigstr_pos_base_path}[1]/div/div[2]/div[1]/i[1]/text()").get()
        detailed_fight_data_sigstr_item["blue_fighter_sig_str_head_pct"] = response.xpath(f"{detailed_fight_sigstr_pos_base_path}[1]/div/div[2]/div[1]/i[3]/text()").get()
        detailed_fight_data_sigstr_item["red_fighter_sig_str_body_pct"] = response.xpath(f"{detailed_fight_sigstr_pos_base_path}[1]/div/div[2]/div[2]/i[1]/text()").get()
        detailed_fight_data_sigstr_item["blue_fighter_sig_str_body_pct"] = response.xpath(f"{detailed_fight_sigstr_pos_base_path}[1]/div/div[2]/div[2]/i[3]/text()").get()
        detailed_fight_data_sigstr_item["red_fighter_sig_str_leg_pct"] = response.xpath(f"{detailed_fight_sigstr_pos_base_path}[1]/div/div[2]/div[3]/i[1]/text()").get()
        detailed_fight_data_sigstr_item["blue_fighter_sig_str_leg_pct"] = response.xpath(f"{detailed_fight_sigstr_pos_base_path}[1]/div/div[2]/div[3]/i[3]/text()").get()
        detailed_fight_data_sigstr_item["red_fighter_sig_str_distance_pct"] = response.xpath(f"{detailed_fight_sigstr_pos_base_path}[2]/div/div[2]/div[1]/i[1]/text()").get()
        detailed_fight_data_sigstr_item["blue_fighter_sig_str_distance_pct"] = response.xpath(f"{detailed_fight_sigstr_pos_base_path}[2]/div/div[2]/div[1]/i[3]/text()").get()
        detailed_fight_data_sigstr_item["red_fighter_sig_str_clinch_pct"] = response.xpath(f"{detailed_fight_sigstr_pos_base_path}[2]/div/div[2]/div[2]/i[1]/text()").get()
        detailed_fight_data_sigstr_item["blue_fighter_sig_str_clinch_pct"] = response.xpath(f"{detailed_fight_sigstr_pos_base_path}[2]/div/div[2]/div[2]/i[3]/text()").get()
        detailed_fight_data_sigstr_item["red_fighter_sig_str_ground_pct"] = response.xpath(f"{detailed_fight_sigstr_pos_base_path}[2]/div/div[2]/div[3]/i[1]/text()").get()
        detailed_fight_data_sigstr_item["blue_fighter_sig_str_ground_pct"] = response.xpath(f"{detailed_fight_sigstr_pos_base_path}[2]/div/div[2]/div[3]/i[3]/text()").get()
        yield detailed_fight_data_sigstr_item