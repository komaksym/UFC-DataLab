from pathlib import Path
from typing import Dict, List

import pytest
import scrapy
from scrapy.http import HtmlResponse

from src.scraping.ufc_scorecards.ufc_scorecards_scraping.spiders.scorecards_spider import ScorecardsSpider


class TestScorecardSpider:
    def setup_method(self) -> None:
        self.spider: ScorecardsSpider = ScorecardsSpider()
        self.mock_pages: Dict[str, Path]
        self.start_url: Path

        def create_full_path(relative_path: str) -> Path:
            """Method for finding paths to mock pages"""
            full_path = Path(__file__).parents[0] / relative_path
            return full_path.resolve()

        # Storing mock pages
        self.mock_pages = {
            "events_page": create_full_path("mock_pages/mock_events_page/events_page.html"),
            "single_event": create_full_path("mock_pages/mock_event_page/event_page.html"),
        }

        self.start_url = self.mock_pages["events_page"]

    def mock_response(self, path: Path) -> HtmlResponse:
        """For creating a mock html response"""
        with open(path, "r") as f:
            html_content = f.read()

        # Mock url
        url = f"file://{path}"

        # Mock request
        request = scrapy.Request(url=url)
        # Mock response
        response = HtmlResponse(url=url, request=request, body=html_content, encoding="utf-8")

        return response

    @pytest.fixture
    def mock_expected_links(self) -> List[str]:
        mock_expected = [
            "file:///news/official-judges-scorecards-ufc-fight-night-covington-vs-buckley-tampa",
            "file:///news/official-judges-scorecards-ufc-310-pantoja-vs-asakura",
            "file:///news/official-judges-scorecards-ufc-macau-yan-vs-figueiredo",
            "file:///news/official-judges-scorecards-ufc-309-jones-vs-miocic",
            "file:///news/official-judges-scorecards-ufc-fight-night-magny-vs-prates-vegas-100",
            "file:///news/official-judges-scorecards-ufc-edmonton-moreno-vs-albazi",
            "file:///Users/koval/dev/UFC_DataLab/tests/scrapers/test_scorecards_scraper/mock_pages/mock_events_page/events_page.html?page=1",
        ]

        return mock_expected

    def test_parse(self, mock_expected_links: List[str]) -> None:
        yielded_responses = self.spider.parse(self.mock_response(self.start_url))
        unpacked_responses: List[str] = [response.url for response in list(yielded_responses)]
        assert unpacked_responses == mock_expected_links

    @pytest.fixture
    def mock_expected_images(self) -> List[str]:
        mock_expected = [
            "https://ufc.com/images/styles/inline/s3/2024-11/UFC%20309%20Jones%20vs.%20Miocic%20-%20Scorecards%20-%20Hardy%20vs.%20Moura%20copy.jpg?itok=Zi5TPB4c",
            "https://ufc.com/images/styles/inline/s3/2024-11/1UFC_309_Jones_vs__Miocic_-_Scorecards_-_Hafez_vs__Elliott_pdf-copy.jpg?itok=WU5n2pHh",
            "https://ufc.com/images/styles/inline/s3/2024-11/2UFC_309_Jones_vs__Miocic_-_Scorecards_-_Gall_vs__Brahimaj_pdfcopy.jpg?itok=kJsYLStO",
            "https://ufc.com/images/styles/inline/s3/2024-11/3UFC_309_Jones_vs__Miocic_-_Scorecards_-_Tybura_vs__Diniz_pdf%20copy.jpg?itok=4dvGm6S9",
            "https://ufc.com/images/styles/inline/s3/2024-11/Onama-Scorecard-309.jpg?itok=QK3vDSxM",
            "https://ufc.com/images/styles/inline/s3/2024-11/5Cursor_and_UFC_309_Jones_vs__Miocic_-_Scorecards_-_Miller_vs__Jackson_pdf-copy.jpg?itok=aBWdEIuU",
            "https://ufc.com/images/styles/inline/s3/2024-11/6UFC_309_Jones_vs__Miocic_-_Scorecards_-_Martinez_vs__McGhee_pdf%20copy.jpg?itok=sGGheida",
            "https://ufc.com/images/styles/inline/s3/2024-11/7UFC_309_Jones_vs__Miocic_-_Scorecards_-_Ruffy_vs__Llontop_pdf%20copy.jpg?itok=7gahH1lq",
            "https://ufc.com/images/styles/inline/s3/2024-11/UFC_309_Jones_vs__Miocic_-_Scorecards_-_Araujo_vs__Silva_pdf-copy.jpg?itok=bhZxV1Av",
            "https://ufc.com/images/styles/inline/s3/2024-11/8UFC_309_Jones_vs__Miocic_-_Scorecards_-_Nickal_vs__Craig_pdf-copy.jpg?itok=4bfa06mW",
            "https://ufc.com/images/styles/inline/s3/2024-11/99UFC_309_Jones_vs__Miocic_-_Scorecards_-_Oliveira_vs__Chandler_pdf--copy.jpg?itok=_Ho0ELrw",
            "https://ufc.com/images/styles/inline/s3/2024-11/01UFC_309_Jones_vs__Miocic_-_Scorecards_-_Jones_vs__Miocic_pdf-copy.jpg?itok=qsxO5UrD",
        ]
        return mock_expected

    def test_parse_event(self, mock_expected_images: List[str]) -> None:
        yielded_responses = self.spider.parse_event(self.mock_response(self.mock_pages["single_event"]))
        unpacked_responses: List[str] = list(yielded_responses)[0]["image_urls"]
        assert unpacked_responses == mock_expected_images
