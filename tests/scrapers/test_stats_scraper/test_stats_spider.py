import pytest
import scrapy
from pathlib import Path
from scrapy.http import HtmlResponse
from src.scraping.ufc_stats_scraping.ufcstats_scraping.spiders.stats_spider import Stats_Spider
from src.scraping.ufc_stats_scraping.ufcstats_scraping.items import FightData


class TestStatsSpider:
    """Test suite for the UFC Stats Spider.
    
    Tests the spider's ability to:
    - Parse event listing pages
    - Extract fight data from event pages
    - Process individual fight details
    """

    def setup_method(self):
        """Initialize spider and set up mock data paths before each test."""
        self.spider = Stats_Spider()

        def create_full_path(relative_path):
            """Method for finding paths to mock pages"""
            full_path = Path(__file__).parents[0] / relative_path
            return full_path.resolve()
        
        # Storing mock pages
        self.mock_pages = {
            'events_page': create_full_path("mock_pages/mock_events_page/events_page.html"),
            'single_event': create_full_path("mock_pages/mock_event_page/single_event_page.html"),
            'single_fight': create_full_path("mock_pages/mock_fight_page/fight_page.html")
        }     

        self.start_urls = self.mock_pages['events_page']

    def mock_response(self, path, metadata=None):
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
        response = HtmlResponse(url=url, request=request, body=html_content, encoding='utf-8')

        return response

    def test_parse(self):
        """Test the main parse method for correct event link extraction.
        
        Verifies that:
        - All extracted links are valid event URLs
        - Links follow the expected UFC Stats format
        """
        responses = self.spider.parse(self.mock_response(self.start_urls))
        assert all(response.url.startswith("http://ufcstats.com/event-details/") 
               for response in responses), (
            f"Invalid event links detected.\n"
            f"All URLs should start with 'http://ufcstats.com/event-details/'\n"
            f"Invalid URLs: {[r.url for r in responses if not r.url.startswith('http://ufcstats.com/event-details/')]}"
        )

    @pytest.fixture
    def mock_metadata(self):
        """Fixture providing sample event metadata for testing."""
        metadata = {'event_data': {'name': '\n              UFC 309: Jones vs. Miocic\n            ', 'date': ['\n      ', '\n      November 16, 2024\n    '], 'location': ['\n      ', '\n\n      New York City, New York, USA\n    ']}}
        return metadata

    def test_parse_event(self, mock_metadata):
        """Test event page parsing for correct fight link extraction.
        
        Verifies that:
        - Event metadata is correctly extracted
        - All fight links are valid URLs
        - Links maintain expected format
        """
        responses = list(self.spider.parse_event(
            self.mock_response(self.mock_pages['single_event'])
        ))

        assert responses[0].meta == mock_metadata, (
            f"Event metadata mismatch.\n"
            f"Expected: {mock_metadata}\n"
            f"Got: {responses[0].meta}"
        )
        
        assert all(response.url.startswith("http://ufcstats.com/fight-details/") 
                   for response in responses), (
            f"Invalid fight links detected.\n"
            f"All URLs should start with 'http://ufcstats.com/fight-details/'\n"
            f"Invalid URLs: {[r.url for r in responses if not r.url.startswith('http://ufcstats.com/fight-details/')]}"
        )

    def test_parse_fight(self, mock_metadata):
        """Test individual fight page parsing.
        
        Verifies that:
        - Fight data is correctly extracted
        - Output is properly formatted as FightData item
        """
        response = list(self.spider.parse_fight(
            self.mock_response(self.mock_pages['single_fight'], mock_metadata)
        ))
        
        assert isinstance(response[0], FightData), (
            f"Invalid response type.\n"
            f"Expected: FightData\n"
            f"Got: {type(response[0])}"
        )