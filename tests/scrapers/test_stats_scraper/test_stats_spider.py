import pytest
from pathlib import Path
import scrapy
from scrapy.http import HtmlResponse
from src.scraping.ufc_stats_scraping.ufcstats_scraping \
        .spiders.stats_spider import Stats_Spider
from src.scraping.ufc_stats_scraping.ufcstats_scraping.items import FightData


def mock_response(path, metadata=None):
    """Creating a mock html response"""
    with open(path, "rb") as f:
        html_content = f.read()

    # Mock url
    url = f"file://{path}"

    # Ensuring metadata is a dictionary
    if metadata is None:
        metadata = {}

    # Mock request
    request = scrapy.Request(url=url, meta=metadata)
    # Mock response
    response = HtmlResponse(url=url, request=request, body=html_content, encoding='utf-8')

    return response
    

class TestStatsSpider:
    def setup_method(self):
        self.spider = Stats_Spider()

        def create_full_path(relative_path):
            """Method for finding paths to mock pages"""
            full_path = Path(__file__).parents[0] / relative_path
            return full_path.resolve()
        
        # Storing mock pages
        self.mock_pages = {
            'events_page': create_full_path("mock_pages/dummy_events_page/events_page.html"),
            'single_event': create_full_path("mock_pages/dummy_event_page/single_event_page.html"),
            'single_fight': create_full_path("mock_pages/dummy_fight_page/fight_page.html")
        }     

        self.start_urls = self.mock_pages['events_page']

    def test_parse(self):
        """Test parse events method"""
        responses = self.spider.parse(mock_response(self.start_urls))
        # Checking if all parsed events links are indeed links
        assert all(response.url.startswith("http://ufcstats.com/event-details/") 
               for response in responses), (
               f"Invalid event links format. "
               f"Expected: URLs starting with 'http://ufcstats.com/event-details/', "
               f"Got: {[response.url for response in responses if not response.url.startswith('http://ufcstats.com/event-details/')]}")

    @pytest.fixture
    def mock_metadata(self):
        metadata = {'event_data': {'name': '\n              UFC 309: Jones vs. Miocic\n            ', 'date': ['\n      ', '\n      November 16, 2024\n    '], 'location': ['\n      ', '\n\n      New York City, New York, USA\n    ']}}
        return metadata

    def test_parse_event(self, mock_metadata):
        """Test parse event method"""
        responses = self.spider.parse_event(mock_response(self.mock_pages['single_event']))
        # Unpacking generator
        responses = list(responses)

        # Testing whether the metadata was scraped
        assert responses[0].meta == mock_metadata
        # Checking if all parsed events links are indeed links
        assert all(response.url.startswith("http://ufcstats.com/fight-details/") 
                   for response in responses), (f"Invalid fight links format. "
                      f"Expected: URLs starting with 'http://ufcstats.com/fight-details/', "
                      f"Got: {[response.url for response in responses if not response.url.startswith('http://ufcstats.com/fight-details/')]}")

    def test_parse_fight(self, mock_metadata):
        response = self.spider.parse_fight(mock_response(self.mock_pages['single_fight'], mock_metadata))
        # Unpacking generator
        response = list(response)
        # Testing whether the yielded result is a scrapy item
        assert isinstance(response[0], FightData)