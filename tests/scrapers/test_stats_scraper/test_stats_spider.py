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
            full_path = Path(__file__).parents[0] / relative_path
            return full_path.resolve()

        # Storing mock pages
        self.mock_pages = {
            "events_page": create_full_path("mock_pages/mock_events_page/events_page.html"),
            "single_event": create_full_path("mock_pages/mock_event_page/single_event_page.html"),
            "single_fight": create_full_path("mock_pages/mock_fight_page/fight_page.html"),
        }

        self.start_urls = self.mock_pages["events_page"]

    def mock_response(self, path: Path, metadata: Optional[Dict[str, Any]] = None) -> HtmlResponse:
        """Create a mock HtmlResponse object for testing.

        Args:
            path (str): Path to the mock HTML file
            metadata (dict, optional): Additional metadata for the request

        Returns:
            HtmlResponse: A mock response object containing the HTML content
        """
        with open(path, "r") as f:
            html_content = f.read()

        # Mock url
        url = f"file://{path}"

        # Ensuring metadata is a dictionary
        if metadata is None:
            metadata = {}

        # Mock request
        request = scrapy.Request(url=url, meta=metadata)
        # Mock response
        response = HtmlResponse(url=url, request=request, body=html_content, encoding="utf-8")

        return response

    def test_parse(self) -> None:
        """Test the main parse method for correct event link extraction.

        Verifies that:
        - All extracted links are valid event URLs
        - Links follow the expected UFC Stats format
        """
        responses: Iterator[Request] = self.spider.parse(self.mock_response(self.start_urls))
        assert all(response.url.startswith("http://ufcstats.com/event-details/") for response in responses), (
            f"Invalid event links detected.\n"
            f"All URLs should start with 'http://ufcstats.com/event-details/'\n"
            f"Invalid URLs: {[r.url for r in responses if not r.url.startswith('http://ufcstats.com/event-details/')]}"
        )

    @pytest.fixture
    def mock_metadata(self) -> Dict[str, Dict[str, Any]]:
        """Fixture providing sample event metadata for testing."""
        return {
            "event_data": {
                "name": "\n              UFC 309: Jones vs. Miocic\n            ",
                "date": ["\n      ", "\n      November 16, 2024\n    "],
                "location": ["\n      ", "\n\n      New York City, New York, USA\n    "],
            }
        }

    def test_parse_event(self, mock_metadata: Dict[str, Dict[str, Any]]) -> None:
        """Test event page parsing for correct fight link extraction.

        Verifies that:
        - Event metadata is correctly extracted
        - All fight links are valid URLs
        - Links maintain expected format
        """
        responses: List[Request] = list(
            self.spider.parse_event(self.mock_response(self.mock_pages["single_event"]))
        )

        assert responses[0].meta == mock_metadata, (
            f"Event metadata mismatch.\nExpected: {mock_metadata}\nGot: {responses[0].meta}"
        )

        assert all(response.url.startswith("http://ufcstats.com/fight-details/") for response in responses), (
            f"Invalid fight links detected.\n"
            f"All URLs should start with 'http://ufcstats.com/fight-details/'\n"
            f"Invalid URLs: {[r.url for r in responses if not r.url.startswith('http://ufcstats.com/fight-details/')]}"
        )

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
