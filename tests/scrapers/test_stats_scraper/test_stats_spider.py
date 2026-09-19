from pathlib import Path
from typing import Any, Dict, Iterator, List, Optional

import pytest
import scrapy
from scrapy.http import HtmlResponse, Request

from src.scraping.ufc_stats.ufcstats_scraping.items import FightData
from src.scraping.ufc_stats.ufcstats_scraping.spiders.stats_spider import StatsSpider


class TestStatsSpider:
    """Test suite for the UFC Stats Spider."""

    def setup_method(self) -> None:
        self.spider: StatsSpider = StatsSpider()
        self.mock_pages: Dict[str, Path]
        self.start_urls: Path

        def create_full_path(relative_path: str) -> Path:
            """Method for finding paths to mock pages"""
            full_path: Path = Path(__file__).parents[0] / relative_path
            return full_path.resolve()

        # Storing mock pages
        self.mock_pages = {
            "events_page": create_full_path("mock_pages/mock_events_page/events_page.html"),
            "single_event": create_full_path("mock_pages/mock_event_page/single_event_page.html"),
            "result_variants_event": create_full_path(
                "mock_pages/mock_event_page/result_variants_event_page.html"
            ),
            "single_fight": create_full_path("mock_pages/mock_fight_page/fight_page.html"),
        }

        self.start_urls = self.mock_pages["events_page"]

    def mock_response(self, path: Path, metadata: Optional[Dict[str, Any]] = None) -> HtmlResponse:
        """Create a mock HtmlResponse object for testing."""

        with open(path, "r") as f:
            html_content: str = f.read()

        # Mock url
        url: str = f"file://{path}"

        # Ensuring metadata is a dictionary
        if metadata is None:
            metadata = {}

        # Mock request
        request = scrapy.Request(url=url, meta=metadata)
        # Mock response
        response = HtmlResponse(url=url, request=request, body=html_content, encoding="utf-8")

        return response

    def test_parse(self) -> None:
        """Test the main parse method for correct event link extraction."""

        responses: Iterator[Request] = self.spider.parse(self.mock_response(self.start_urls))
        assert all(response.url.startswith("http://ufcstats.com/event-details/") for response in responses), (
            f"Invalid event links detected.\n"
            f"All URLs should start with 'http://ufcstats.com/event-details/'\n"
            f"Invalid URLs: {[r.url for r in responses if not r.url.startswith('http://ufcstats.com/event-details/')]}"
        )

    @pytest.fixture
    def mock_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Fixture providing sample event metadata for testing."""

        event_id = "daff32bc96d1eabf"
        event_url = f"http://ufcstats.com/event-details/{event_id}"
        fight_id = "b35e47f2f58ef026"
        fight_url = f"http://ufcstats.com/fight-details/{fight_id}"
        return {
            "event_data": {
                "name": "\n              UFC 309: Jones vs. Miocic\n            ",
                "date": ["\n      ", "\n      November 16, 2024\n    "],
                "location": ["\n      ", "\n\n      New York City, New York, USA\n    "],
                "event_id": event_id,
                "event_url": event_url,
            },
            "event_id": event_id,
            "event_url": event_url,
            "fight_id": fight_id,
            "fight_url": fight_url,
        }

    def test_parse_event(self, mock_metadata: Dict[str, Dict[str, Any]]) -> None:
        """Test event page parsing for correct fight link extraction.

        Verifies that:
        - Event metadata is correctly extracted
        - All fight links are valid URLs
        - Links maintain expected format
        - Stable fight IDs propagate in request metadata
        """

        responses: List[Request] = list(
            self.spider.parse_event(self.mock_response(self.mock_pages["single_event"]))
        )

        # File:// fixture has no real event URL, so event_id falls back to None,
        # but every fight request must carry the stable fight_id from data-link.
        assert responses[0].meta["event_data"]["name"] == mock_metadata["event_data"]["name"]
        assert "event_id" in responses[0].meta["event_data"]
        assert "event_url" in responses[0].meta["event_data"]
        assert responses[0].meta["fight_id"] == "b35e47f2f58ef026"
        assert responses[0].meta["fight_url"] == "http://ufcstats.com/fight-details/b35e47f2f58ef026"
        assert responses[0].meta["event_data"]["event_id"] is None

        assert all(response.url.startswith("http://ufcstats.com/fight-details/") for response in responses), (
            f"Invalid fight links detected.\n"
            f"All URLs should start with 'http://ufcstats.com/fight-details/'\n"
            f"Invalid URLs: {[r.url for r in responses if not r.url.startswith('http://ufcstats.com/fight-details/')]}"
        )

    def test_parse_event_uses_row_links_for_non_decisive_fights(self) -> None:
        """Event parsing should follow row detail links regardless of result styling."""

        responses: List[Request] = list(
            self.spider.parse_event(self.mock_response(self.mock_pages["result_variants_event"]))
        )

        assert [response.url for response in responses] == [
            "http://ufcstats.com/fight-details/decisive-fight",
            "http://ufcstats.com/fight-details/draw-fight",
            "http://ufcstats.com/fight-details/no-contest-fight",
        ]

    def test_parse_incremental_skips_old_events(self) -> None:
        """When ``since`` is set, events at or before that date are skipped."""

        # Mock events page has events from December 14, 2024 down to earlier dates.
        # Setting since to November 16 should skip Nov 16 and everything before it.
        spider = StatsSpider(since="16/11/2024")
        responses: List[Request] = list(spider.parse(self.mock_response(self.start_urls)))

        full_spider = StatsSpider()
        all_responses: List[Request] = list(full_spider.parse(self.mock_response(self.start_urls)))

        assert len(responses) < len(all_responses), (
            "Incremental spider should yield fewer events than full spider"
        )
        # Events on or before Nov 16 should be excluded
        assert len(responses) > 0, "Should still yield some recent events"

    def test_parse_full_scrape_when_since_omitted(self) -> None:
        """Without ``since``, all events are scraped."""

        spider = StatsSpider()
        assert spider.since is None
        responses: List[Request] = list(spider.parse(self.mock_response(self.start_urls)))
        assert len(responses) > 0

    @pytest.fixture
    def expected_parsed_fight_data(self):
        """Fixture providing expected parsed fight data."""

        return [
            {
                "blue_fighter_KD": "\n      0\n    ",
                "blue_fighter_TD": "\n      0 of 0\n    ",
                "blue_fighter_TD_pct": "\n      ---\n    ",
                "blue_fighter_ctrl": "\n      0:00\n    ",
                "blue_fighter_name": "Stipe Miocic ",
                "blue_fighter_nickname": "\n      \n    ",
                "blue_fighter_result": "\n    L\n  ",
                "blue_fighter_rev": "\n      0\n    ",
                "blue_fighter_sig_str": "\n      37 of 89\n    ",
                "blue_fighter_sig_str_body": "\n      7 of 8\n    ",
                "blue_fighter_sig_str_body_pct": "\n                  18%\n                ",
                "blue_fighter_sig_str_clinch": "\n      4 of 5\n    ",
                "blue_fighter_sig_str_clinch_pct": "\n                  10%\n                ",
                "blue_fighter_sig_str_distance": "\n      32 of 83\n    ",
                "blue_fighter_sig_str_distance_pct": "\n                  86%\n                ",
                "blue_fighter_sig_str_ground": "\n      1 of 1\n    ",
                "blue_fighter_sig_str_ground_pct": "\n                  2%\n                ",
                "blue_fighter_sig_str_head": "\n      24 of 75\n    ",
                "blue_fighter_sig_str_head_pct": "\n                  64%\n                ",
                "blue_fighter_sig_str_leg": "\n      6 of 6\n    ",
                "blue_fighter_sig_str_leg_pct": "\n                  16%\n                ",
                "blue_fighter_sig_str_pct": "\n      41%\n    ",
                "blue_fighter_sub_att": "\n      0\n    ",
                "blue_fighter_total_str": "\n      42 of 94\n    ",
                "blue_fighter_id": "d28dee5c705991df",
                "blue_fighter_url": "http://ufcstats.com/fighter-details/d28dee5c705991df",
                "bonus": "fight_page_files/belt.png",
                "bout_type": "\n      UFC Heavyweight Title Bout\n    ",
                "details": [
                    "\n"
                    "      \n"
                    "      \n"
                    "      \n"
                    "\n"
                    "          \n"
                    "\n"
                    "\n"
                    "          \n"
                    "      \n"
                    "\n"
                    "          \n"
                    "\n"
                    "\n"
                    "          \n"
                    "      \n"
                    "\n"
                    "          \n"
                    "\n"
                    "\n"
                    "          \n"
                    "      \n"
                    "\n"
                    "          \n"
                    "\n"
                    "\n"
                    "          \n"
                    "      \n"
                    "\n"
                    "          \n"
                    "\n"
                    "\n"
                    "          \n"
                    "      \n"
                    "\n"
                    "          \n"
                    "\n"
                    "\n"
                    "          \n"
                    "      \n"
                    "\n"
                    "          \n"
                    "\n"
                    "\n"
                    "          \n"
                    "      \n"
                    "\n"
                    "          \n"
                    "\n"
                    "\n"
                    "          \n"
                    "      \n"
                    "\n"
                    "          \n"
                    "\n"
                    "\n"
                    "          \n"
                    "      \n"
                    "\n"
                    "          \n"
                    "\n"
                    "\n"
                    "          \n"
                    "      \n"
                    "\n"
                    "          \n"
                    "\n"
                    "\n"
                    "          \n"
                    "      \n"
                    "      Spinning Back Kick Body\n"
                    "       \n"
                    "      \n"
                    "\n"
                    "    "
                ],
                "event_date": ["\n      ", "\n      November 16, 2024\n    "],
                "event_location": ["\n      ", "\n\n      New York City, New York, USA\n    "],
                "event_name": "\n              UFC 309: Jones vs. Miocic\n            ",
                "event_id": "daff32bc96d1eabf",
                "event_url": "http://ufcstats.com/event-details/daff32bc96d1eabf",
                "fight_id": "b35e47f2f58ef026",
                "fight_url": "http://ufcstats.com/fight-details/b35e47f2f58ef026",
                "source": "ufcstats",
                "method": " KO/TKO ",
                "red_fighter_KD": "\n      1\n    ",
                "red_fighter_TD": "\n      1 of 1\n    ",
                "red_fighter_TD_pct": "\n      100%\n    ",
                "red_fighter_ctrl": "\n      3:51\n    ",
                "red_fighter_name": "Jon Jones ",
                "red_fighter_nickname": '\n      "Bones"\n    ',
                "red_fighter_result": "\n    W\n  ",
                "red_fighter_rev": "\n      0\n    ",
                "red_fighter_sig_str": "\n      96 of 119\n    ",
                "red_fighter_sig_str_body": "\n      16 of 18\n    ",
                "red_fighter_sig_str_body_pct": "\n                  16%\n                ",
                "red_fighter_sig_str_clinch": "\n      2 of 3\n    ",
                "red_fighter_sig_str_clinch_pct": "\n                  2%\n                ",
                "red_fighter_sig_str_distance": "\n      54 of 70\n    ",
                "red_fighter_sig_str_distance_pct": "\n                  56%\n                ",
                "red_fighter_sig_str_ground": "\n      40 of 46\n    ",
                "red_fighter_sig_str_ground_pct": "\n                  41%\n                ",
                "red_fighter_sig_str_head": "\n      70 of 91\n    ",
                "red_fighter_sig_str_head_pct": "\n                  72%\n                ",
                "red_fighter_sig_str_leg": "\n      10 of 10\n    ",
                "red_fighter_sig_str_leg_pct": "\n                  10%\n                ",
                "red_fighter_sig_str_pct": "\n      80%\n    ",
                "red_fighter_sub_att": "\n      0\n    ",
                "red_fighter_total_str": "\n      104 of 128\n    ",
                "red_fighter_id": "07f72a2a7591b409",
                "red_fighter_url": "http://ufcstats.com/fighter-details/07f72a2a7591b409",
                "referee": "\n                                Herb Dean\n                            ",
                "round": "\n        3\n      ",
                "time": "\n        4:29\n\n      ",
                "time_format": "\n        5 Rnd (5-5-5-5-5)\n      ",
            }
        ]

    def test_parse_fight(self, mock_metadata: Dict[str, Dict[str, Any]], expected_parsed_fight_data) -> None:
        """Test individual fight page parsing.

        Verifies that:
        - Fight data is correctly extracted
        - Output is properly formatted as FightData item
        """

        response: List[FightData] = list(
            self.spider.parse_fight(self.mock_response(self.mock_pages["single_fight"], mock_metadata))
        )

        assert response == expected_parsed_fight_data, (
            f"The parsed fight data is invalid.\nExpected:{expected_parsed_fight_data}.\nGot:{response}"
        )

        assert isinstance(response[0], FightData), (
            f"Invalid response type.\nExpected: FightData\nGot: {type(response[0])}"
        )

    def test_parse_fight_retains_stable_identity_and_provenance(
        self, mock_metadata: Dict[str, Dict[str, Any]]
    ) -> None:
        """Scraped records retain IDs, URLs, orientation, and provenance."""

        item = list(
            self.spider.parse_fight(self.mock_response(self.mock_pages["single_fight"], mock_metadata))
        )[0]

        assert item["fight_id"] == "b35e47f2f58ef026"
        assert item["event_id"] == "daff32bc96d1eabf"
        assert item["red_fighter_id"] == "07f72a2a7591b409"
        assert item["blue_fighter_id"] == "d28dee5c705991df"
        assert item["fight_url"] == "http://ufcstats.com/fight-details/b35e47f2f58ef026"
        assert item["event_url"] == "http://ufcstats.com/event-details/daff32bc96d1eabf"
        assert item["red_fighter_url"] == "http://ufcstats.com/fighter-details/07f72a2a7591b409"
        assert item["blue_fighter_url"] == "http://ufcstats.com/fighter-details/d28dee5c705991df"
        assert item["source"] == "ufcstats"
        # Red/blue orientation: first corner on the page is red.
        assert item["red_fighter_name"].strip() == "Jon Jones"
        assert item["blue_fighter_name"].strip() == "Stipe Miocic"
        assert item["red_fighter_result"].strip() == "W"
        assert item["blue_fighter_result"].strip() == "L"

    def test_parse_event_propagates_stable_fight_ids(self) -> None:
        """Event parsing carries stable fight IDs without collapsing rows."""

        responses: List[Request] = list(
            self.spider.parse_event(self.mock_response(self.mock_pages["single_event"]))
        )

        fight_ids = [response.meta["fight_id"] for response in responses]
        assert fight_ids[0] == "b35e47f2f58ef026"
        # Same-card bouts keep distinct stable IDs (no name-based collapsing).
        assert len(set(fight_ids)) == len(fight_ids)
        assert all(url.startswith("http://ufcstats.com/fight-details/") for url in [r.url for r in responses])

    def test_extract_ufcstats_id_parses_detail_urls(self) -> None:
        """IDs derive from source links, never from names or dates."""

        from src.scraping.ufc_stats.ufcstats_scraping.identity import extract_ufcstats_id

        assert extract_ufcstats_id("http://ufcstats.com/fight-details/b35e47f2f58ef026", "fight") == "b35e47f2f58ef026"
        assert extract_ufcstats_id("http://ufcstats.com/event-details/daff32bc96d1eabf", "event") == "daff32bc96d1eabf"
        assert (
            extract_ufcstats_id("http://ufcstats.com/fighter-details/07f72a2a7591b409", "fighter")
            == "07f72a2a7591b409"
        )
        assert extract_ufcstats_id(None, "fight") is None
        assert extract_ufcstats_id("http://ufcstats.com/statistics/events/completed", "fight") is None
        assert extract_ufcstats_id("http://ufcstats.com/fight-details/b35e47f2f58ef026", "event") is None
