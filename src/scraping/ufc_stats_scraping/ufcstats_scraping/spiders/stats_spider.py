import scrapy
from typing import List, Iterator, Optional, Dict, Any
from twisted.python.failure import Failure
from ..items import FightData
from scrapy.http.request import Request
from scrapy.http.response import Response


class Stats_Spider(scrapy.Spider):
    """Spider for scraping UFC fight statistics."""

    name: str = "stats_spider"
    allowed_domains: List[str] = ["ufcstats.com"]
    start_urls: List[str] = ["http://ufcstats.com/statistics/events/completed?page=all"]

    def parse(self, response: Response) -> Iterator[Request]:
        """Extract and follow links to all UFC events.

        Args:
            response: The response containing the events page HTML

        Returns:
            Iterator of Requests to event pages
        """
        events_links: List[str] = response.css(
            "a.b-link.b-link_style_black::attr(href)"
        ).getall()
        for event_link in events_links:
            yield scrapy.Request(url=event_link, callback=self.parse_event)

    def parse_event(self, response: Response) -> Iterator[Request]:
        """Extract event data and follow links to individual fights.

        Args:
            response: The response containing the event page HTML

        Returns:
            Iterator of Requests to fight pages with event metadata
        """
        event_data: Dict[str, Any] = {
            "name": response.css("h2.b-content__title span::text").get(),
            "date": response.xpath(
                "/html/body/section/div/div/div[1]/ul/li[1]/text()"
            ).getall(),
            "location": response.css(
                "li.b-list__box-list-item:nth-child(2)::text"
            ).getall(),
        }

        fights_links: List[str] = response.css(
            "a.b-flag.b-flag_style_green::attr(href)"
        ).getall()
        for fight_link in fights_links:
            yield scrapy.Request(
                url=fight_link,
                callback=self.parse_fight,
                meta={"event_data": event_data},
                errback=self.handle_error,
            )

    def parse_fight(self, response: Response) -> Optional[FightData]:
        """Parse individual fight data using xpath selectors.

        Args:
            response: The response containing the fight page HTML

        Returns:
            FightData item containing all fight statistics or None if critical data missing
        """
        event_data: Dict[str, Any] = response.meta["event_data"]
        fight_data_item: FightData = FightData()
        general_fight_base_path = "/html/body/section/div/div/div"

        fight_data_item["red_fighter_name"] = response.xpath(
            f"{general_fight_base_path}[1]/div[1]/div/h3/a/text()"
        ).get()
        fight_data_item["blue_fighter_name"] = response.xpath(
            f"{general_fight_base_path}[1]/div[2]/div/h3/a/text()"
        ).get()
        fight_data_item["red_fighter_nickname"] = response.xpath(
            f"{general_fight_base_path}[1]/div[1]/div/p/text()"
        ).get()
        fight_data_item["blue_fighter_nickname"] = response.xpath(
            f"{general_fight_base_path}[1]/div[2]/div/p/text()"
        ).get()
        fight_data_item["red_fighter_result"] = response.xpath(
            f"{general_fight_base_path}[1]/div[1]/i/text()"
        ).get()
        fight_data_item["blue_fighter_result"] = response.xpath(
            f"{general_fight_base_path}[1]/div[2]/i/text()"
        ).get()
        fight_data_item["method"] = response.xpath(
            f"{general_fight_base_path}[2]/div[2]/p[1]/i[1]/i[2]/text()"
        ).get()
        fight_data_item["round"] = response.xpath(
            f"{general_fight_base_path}[2]/div[2]/p[1]/i[2]/text()[2]"
        ).get()
        fight_data_item["time"] = response.xpath(
            f"{general_fight_base_path}[2]/div[2]/p[1]/i[3]/text()[2]"
        ).get()
        fight_data_item["time_format"] = response.xpath(
            f"{general_fight_base_path}[2]/div[2]/p[1]/i[4]/text()[2]"
        ).get()
        fight_data_item["referee"] = response.xpath(
            f"{general_fight_base_path}[2]/div[2]/p[1]/i[5]/span/text()"
        ).get()
        fight_data_item["details"] = response.xpath(
            "//p[@class='b-fight-details__text'][2]//text()[normalize-space() and not (contains(., 'Details:'))]"
        ).getall()
        fight_data_item["bout_type"] = response.xpath(
            f"{general_fight_base_path}[2]/div[1]/i/text()"
        ).getall()[-1]
        fight_data_item["bonus"] = response.xpath(
            f"{general_fight_base_path}[2]/div[1]/i/img/@src"
        ).get("-")

        # Event data
        fight_data_item["event_name"] = event_data["name"]
        fight_data_item["event_date"] = event_data["date"]
        fight_data_item["event_location"] = event_data["location"]

        # Detailed Fight data totals
        detailed_fight_totals_base_path = (
            "/html/body/section/div/div/section[2]/table/tbody/tr/td"
        )
        fight_data_item["red_fighter_KD"] = response.xpath(
            f"{detailed_fight_totals_base_path}[2]/p[1]/text()"
        ).get()
        fight_data_item["blue_fighter_KD"] = response.xpath(
            f"{detailed_fight_totals_base_path}[2]/p[2]/text()"
        ).get()
        fight_data_item["red_fighter_sig_str"] = response.xpath(
            f"{detailed_fight_totals_base_path}[3]/p[1]/text()"
        ).get()
        fight_data_item["blue_fighter_sig_str"] = response.xpath(
            f"{detailed_fight_totals_base_path}[3]/p[2]/text()"
        ).get():
        fight_data_item["red_fighter_sig_str_pct"] = response.xpath(
            f"{detailed_fight_totals_base_path}[4]/p[1]/text()"
        ).get()
        fight_data_item["blue_fighter_sig_str_pct"] = response.xpath(
            f"{detailed_fight_totals_base_path}[4]/p[2]/text()"
        ).get()
        fight_data_item["red_fighter_total_str"] = response.xpath(
            f"{detailed_fight_totals_base_path}[5]/p[1]/text()"
        ).get()
        fight_data_item["blue_fighter_total_str"] = response.xpath(
            f"{detailed_fight_totals_base_path}[5]/p[2]/text()"
        ).get()
        fight_data_item["red_fighter_TD"] = response.xpath(
            f"{detailed_fight_totals_base_path}[6]/p[1]/text()"
        ).get()
        fight_data_item["blue_fighter_TD"] = response.xpath(
            f"{detailed_fight_totals_base_path}[6]/p[2]/text()"
        ).get()
        fight_data_item["red_fighter_TD_pct"] = response.xpath(
            f"{detailed_fight_totals_base_path}[7]/p[1]/text()"
        ).get()
        fight_data_item["blue_fighter_TD_pct"] = response.xpath(
            f"{detailed_fight_totals_base_path}[7]/p[2]/text()"
        ).get()
        fight_data_item["red_fighter_sub_att"] = response.xpath(
            f"{detailed_fight_totals_base_path}[8]/p[1]/text()"
        ).get()
        fight_data_item["blue_fighter_sub_att"] = response.xpath(
            f"{detailed_fight_totals_base_path}[8]/p[2]/text()"
        ).get()
        fight_data_item["red_fighter_rev"] = response.xpath(
            f"{detailed_fight_totals_base_path}[9]/p[1]/text()"
        ).get()
        fight_data_item["blue_fighter_rev"] = response.xpath(
            f"{detailed_fight_totals_base_path}[9]/p[2]/text()"
        ).get()
        fight_data_item["red_fighter_ctrl"] = response.xpath(
            f"{detailed_fight_totals_base_path}[10]/p[1]/text()"
        ).get()
        fight_data_item["blue_fighter_ctrl"] = response.xpath(
            f"{detailed_fight_totals_base_path}[10]/p[2]/text()"
        ).get()

        # Detailed Fight data significant strikes
        detailed_fight_sigstr_tar_base_path = (
            "/html/body/section/div/div/table/tbody/tr/td"
        )
        detailed_fight_sigstr_pos_base_path = (
            "/html/body/section/div/div/section[6]/div/div/div[1]/div"
        )
        fight_data_item["red_fighter_sig_str_head"] = response.xpath(
            f"{detailed_fight_sigstr_tar_base_path}[4]/p[1]/text()"
        ).get()
        fight_data_item["blue_fighter_sig_str_head"] = response.xpath(
            f"{detailed_fight_sigstr_tar_base_path}[4]/p[2]/text()"
        ).get()
        fight_data_item["red_fighter_sig_str_body"] = response.xpath(
            f"{detailed_fight_sigstr_tar_base_path}[5]/p[1]/text()"
        ).get()
        fight_data_item["blue_fighter_sig_str_body"] = response.xpath(
            f"{detailed_fight_sigstr_tar_base_path}[5]/p[2]/text()"
        ).get()
        fight_data_item["red_fighter_sig_str_leg"] = response.xpath(
            f"{detailed_fight_sigstr_tar_base_path}[6]/p[1]/text()"
        ).get()
        fight_data_item["blue_fighter_sig_str_leg"] = response.xpath(
            f"{detailed_fight_sigstr_tar_base_path}[6]/p[2]/text()"
        ).get()
        fight_data_item["red_fighter_sig_str_distance"] = response.xpath(
            f"{detailed_fight_sigstr_tar_base_path}[7]/p[1]/text()"
        ).get()
        fight_data_item["blue_fighter_sig_str_distance"] = response.xpath(
            f"{detailed_fight_sigstr_tar_base_path}[7]/p[2]/text()"
        ).get()
        fight_data_item["red_fighter_sig_str_clinch"] = response.xpath(
            f"{detailed_fight_sigstr_tar_base_path}[8]/p[1]/text()"
        ).get()
        fight_data_item["blue_fighter_sig_str_clinch"] = response.xpath(
            f"{detailed_fight_sigstr_tar_base_path}[8]/p[2]/text()"
        ).get()
        fight_data_item["red_fighter_sig_str_ground"] = response.xpath(
            f"{detailed_fight_sigstr_tar_base_path}[9]/p[1]/text()"
        ).get()
        fight_data_item["blue_fighter_sig_str_ground"] = response.xpath(
            f"{detailed_fight_sigstr_tar_base_path}[9]/p[2]/text()"
        ).get()
        # Detailed Fight pct data significant strikes by target
        fight_data_item["red_fighter_sig_str_head_pct"] = response.xpath(
            f"{detailed_fight_sigstr_pos_base_path}[1]/div/div[2]/div[1]/i[1]/text()"
        ).get()
        fight_data_item["blue_fighter_sig_str_head_pct"] = response.xpath(
            f"{detailed_fight_sigstr_pos_base_path}[1]/div/div[2]/div[1]/i[3]/text()"
        ).get()
        fight_data_item["red_fighter_sig_str_body_pct"] = response.xpath(
            f"{detailed_fight_sigstr_pos_base_path}[1]/div/div[2]/div[2]/i[1]/text()"
        ).get()
        fight_data_item["blue_fighter_sig_str_body_pct"] = response.xpath(
            f"{detailed_fight_sigstr_pos_base_path}[1]/div/div[2]/div[2]/i[3]/text()"
        ).get()
        fight_data_item["red_fighter_sig_str_leg_pct"] = response.xpath(
            f"{detailed_fight_sigstr_pos_base_path}[1]/div/div[2]/div[3]/i[1]/text()"
        ).get()
        fight_data_item["blue_fighter_sig_str_leg_pct"] = response.xpath(
            f"{detailed_fight_sigstr_pos_base_path}[1]/div/div[2]/div[3]/i[3]/text()"
        ).get()
        # Detailed Fight pct data significant strikes by position
        fight_data_item["red_fighter_sig_str_distance_pct"] = response.xpath(
            f"{detailed_fight_sigstr_pos_base_path}[2]/div/div[2]/div[1]/i[1]/text()"
        ).get()
        fight_data_item["blue_fighter_sig_str_distance_pct"] = response.xpath(
            f"{detailed_fight_sigstr_pos_base_path}[2]/div/div[2]/div[1]/i[3]/text()"
        ).get()
        fight_data_item["red_fighter_sig_str_clinch_pct"] = response.xpath(
            f"{detailed_fight_sigstr_pos_base_path}[2]/div/div[2]/div[2]/i[1]/text()"
        ).get()
        fight_data_item["blue_fighter_sig_str_clinch_pct"] = response.xpath(
            f"{detailed_fight_sigstr_pos_base_path}[2]/div/div[2]/div[2]/i[3]/text()"
        ).get()
        fight_data_item["red_fighter_sig_str_ground_pct"] = response.xpath(
            f"{detailed_fight_sigstr_pos_base_path}[2]/div/div[2]/div[3]/i[1]/text()"
        ).get()
        fight_data_item["blue_fighter_sig_str_ground_pct"] = response.xpath(
            f"{detailed_fight_sigstr_pos_base_path}[2]/div/div[2]/div[3]/i[3]/text()"
        ).get()

        # Add error handling for critical data
        if (
            fight_data_item["red_fighter_name"] == "-"
            or fight_data_item["blue_fighter_name"] == "-"
        ):
            self.logger.error(f"Missing fighter names for fight at URL: {response.url}")
            return None

        yield fight_data_item

    def handle_error(self, failure: Failure) -> None:
        """Handle request failures.

        Args:
            failure: The Failure object containing error details
        """
        self.logger.error(f"Request failed: {failure.request.url}")
        self.logger.error(f"Error: {failure.value}")
