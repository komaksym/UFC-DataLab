from datetime import datetime
from functools import reduce
from typing import Any, Dict, Iterator, List, Optional

import scrapy
from scrapy.http.request import Request
from scrapy.http.response import Response

from ..identity import (
    SOURCE_UFCSTATS,
    extract_ufcstats_id,
)
from ..items import FightData


class StatsSpider(scrapy.Spider):
    """Spider for scraping UFC fight statistics.

    Supports incremental scraping via the ``since`` argument.  Pass a date in
    ``DD/MM/YYYY`` format to only scrape events *after* that date::

        scrapy crawl stats_spider -a since=14/03/2026

    When ``since`` is omitted the spider performs a full scrape.
    """

    name: str = "stats_spider"
    allowed_domains: List[str] = ["ufcstats.com"]
    start_urls: List[str] = ["http://ufcstats.com/statistics/events/completed?page=all"]

    def __init__(self, *args, since: Optional[str] = None, **kwargs):
        super().__init__(*args, **kwargs)
        if since is not None:
            self.since: Optional[datetime] = datetime.strptime(since, "%d/%m/%Y")
            self.logger.info("Incremental mode: scraping events after %s", self.since.date())
        else:
            self.since = None

    @staticmethod
    def _parse_listing_date(text: str) -> Optional[datetime]:
        """Parse a date string like 'March 28, 2026' from the events listing."""
        try:
            return datetime.strptime(text.strip(), "%B %d, %Y")
        except (ValueError, AttributeError):
            return None

    def parse(self, response: Response, **kwargs) -> Iterator[Request]:
        """Extract and follow links to all UFC events.

        When running in incremental mode, events at or before the ``since``
        date are skipped entirely — no event or fight pages are fetched for
        them. The stable ``event_id`` is derived from the event URL and
        carried in request metadata so ``parse_event`` can retain it.
        """

        rows = response.css("tr.b-statistics__table-row")
        for row in rows:
            event_link = row.css("a.b-link.b-link_style_black::attr(href)").get()
            if not event_link:
                continue

            if self.since is not None:
                date_text = row.css("span.b-statistics__date::text").get()
                event_date = self._parse_listing_date(date_text)
                if event_date is not None and event_date <= self.since:
                    self.logger.info(
                        "Skipping event at %s (at or before cutoff %s)",
                        event_date.date(),
                        self.since.date(),
                    )
                    continue

            event_id = extract_ufcstats_id(event_link, "event")
            yield scrapy.Request(
                url=event_link,
                callback=self.parse_event,
                meta={"event_id": event_id, "event_url": event_link},
            )

    def parse_event(self, response: Response) -> Iterator[Request]:
        """Extract event data and follow links to individual fights."""

        # Prefer the stable ID from the event URL; fall back to request meta
        # (used by file:// fixture responses that lack a real event URL).
        meta_event_id = response.meta.get("event_id") if hasattr(response, "meta") else None
        meta_event_url = response.meta.get("event_url") if hasattr(response, "meta") else None
        event_id = extract_ufcstats_id(response.url, "event") or meta_event_id
        event_url = response.url if "ufcstats.com/event-details/" in str(response.url) else meta_event_url

        event_data: Dict[str, Any] = {
            "name": response.css("h2.b-content__title span::text").get(),
            "date": response.xpath("/html/body/section/div/div/div[1]/ul/li[1]/text()").getall(),
            "location": response.css("li.b-list__box-list-item:nth-child(2)::text").getall(),
            "event_id": event_id,
            "event_url": event_url,
        }

        fights_links: List[str] = response.css("tr.js-fight-details-click::attr(data-link)").getall()
        for fight_link in fights_links:
            fight_id = extract_ufcstats_id(fight_link, "fight")
            yield scrapy.Request(
                url=fight_link,
                callback=self.parse_fight,
                meta={
                    "event_data": event_data,
                    "event_id": event_id,
                    "event_url": event_url,
                    "fight_id": fight_id,
                    "fight_url": fight_link,
                },
                errback=self.handle_error,
            )

    def parse_fight(self, response: Response):
        """Parse individual fight data using xpath selectors."""

        event_data: Dict[str, Any] = response.meta["event_data"]
        fight_data_item: FightData = FightData()

        # Event data
        fight_data_item["event_name"] = event_data["name"]
        fight_data_item["event_date"] = event_data["date"]
        fight_data_item["event_location"] = event_data["location"]

        # Stable UFCStats identity and provenance. Red is the first corner on
        # the fight page, blue is the second; IDs and URLs must stay aligned.
        fight_data_item.update(self.extract_fight_identity(response, event_data))

        # Parse general fight data
        fight_data_item = self.parse_fight_general_data(response, fight_data_item)
        # Parse detailed fight data
        fight_data_item = self.parse_fight_detailed_data(response, fight_data_item)

        # Add error handling for critical data
        if fight_data_item["red_fighter_name"] == "-" or fight_data_item["blue_fighter_name"] == "-":
            self.logger.error(f"Missing fighter names for fight at URL: {response.url}")
            return None

        yield fight_data_item

    def extract_fight_identity(self, response: Response, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """Derive stable fight/event/fighter IDs from source links.

        The fight ID comes from the fight URL, the event ID from the event
        link on the fight page (falling back to event-request metadata), and
        the corner fighter IDs from the red/blue person links in page order.
        Red/blue orientation is positional: the first person block is red.
        """

        meta = response.meta if hasattr(response, "meta") else {}
        meta_event_id = meta.get("event_id") or event_data.get("event_id")
        meta_event_url = meta.get("event_url") or event_data.get("event_url")
        meta_fight_id = meta.get("fight_id")
        meta_fight_url = meta.get("fight_url")

        fight_url = meta_fight_url or response.url
        # Prefer the real fight URL; fixture file:// URLs carry no fight ID.
        fight_id = extract_ufcstats_id(response.url, "fight") or meta_fight_id

        event_href = response.css("h2.b-content__title a::attr(href)").get()
        event_url = event_href or meta_event_url
        if event_url and "ufcstats.com/event-details/" not in str(event_url):
            event_url = meta_event_url
        event_id = extract_ufcstats_id(event_href, "event") or meta_event_id
        # Fall back to the meta event URL when the page title has no link
        # (older event pages render the title as plain text).
        if event_id is None and meta_event_url:
            event_id = extract_ufcstats_id(meta_event_url, "event") or meta_event_id
        if event_url is None:
            event_url = meta_event_url

        corner_links: List[str] = response.css(
            "div.b-fight-details__person h3 a::attr(href)"
        ).getall()
        red_fighter_url = corner_links[0] if len(corner_links) > 0 else None
        blue_fighter_url = corner_links[1] if len(corner_links) > 1 else None
        red_fighter_id = extract_ufcstats_id(red_fighter_url, "fighter")
        blue_fighter_id = extract_ufcstats_id(blue_fighter_url, "fighter")

        # When the response URL is a fixture placeholder, keep the propagated
        # fight URL so provenance still points at the real source page.
        if "ufcstats.com/fight-details/" not in str(response.url) and meta_fight_url:
            fight_url = meta_fight_url

        return {
            "fight_id": fight_id,
            "event_id": event_id,
            "red_fighter_id": red_fighter_id,
            "blue_fighter_id": blue_fighter_id,
            "fight_url": fight_url,
            "event_url": event_url,
            "red_fighter_url": red_fighter_url,
            "blue_fighter_url": blue_fighter_url,
            "source": SOURCE_UFCSTATS,
        }

    def parse_fight_general_data(self, response: Response, fight_data_item):
        """Parses general fight data like names, bout type, time format, referee, etc."""

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
        fight_data_item["bonus"] = response.xpath(f"{general_fight_base_path}[2]/div[1]/i/img/@src").get("-")

        return fight_data_item

    def parse_fight_detailed_data(self, response: Response, fight_data_item):
        """Parses detailed fight data total strikes, significant strikes, takedowns, submissions, etc."""

        def parse_fundamentals(response: Response, fight_data_item):
            """Detailed Fight data totals"""
            detailed_fight_totals_base_path = "/html/body/section/div/div/section[2]/table/tbody/tr/td"

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
            ).get()
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

            return fight_data_item

        def parse_sig_str_acc(response: Response, fight_data_item):
            """Detailed Fight data significant strikes"""

            detailed_fight_sigstr_tar_base_path = "/html/body/section/div/div/table/tbody/tr/td"

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

            return fight_data_item

        def parse_sig_str_tar(response: Response, fight_data_item):
            """Parses significant strikes by target"""

            detailed_fight_sigstr_pos_base_path = "/html/body/section/div/div/section[6]/div/div/div[1]/div"

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

            return fight_data_item

        def parse_sig_str_pos(response: Response, fight_data_item):
            """Parses significant strikes by position"""

            detailed_fight_sigstr_pos_base_path = "/html/body/section/div/div/section[6]/div/div/div[1]/div"

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

            return fight_data_item

        # Grab all parsers into a list
        parsers = [parse_fundamentals, parse_sig_str_acc, parse_sig_str_tar, parse_sig_str_pos]

        # Run parsers
        fight_data_item = reduce(lambda item, parser: parser(response, item), parsers, fight_data_item)
        return fight_data_item

    def handle_error(self, failure) -> None:
        """Handle request failures."""

        self.logger.error(f"Request failed: {failure.request.url}")
        self.logger.error(f"Error: {failure.value}")
