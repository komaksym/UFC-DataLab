import scrapy
from pathlib import Path


class Test_Stats_Spider(scrapy.Spider):
    name = "tester"

    r
    events_page_path = Path(__file__).parents[2] / "dummy_pages_to_scrape/dummy_events_page/events_page.html"
    start_urls = [f"file://{events_page_path.resolve()}"]
    events_page_path = Path(__file__).parents[2] / "dummy_pages_to_scrape/dummy_events_page/events_page.html"
    start_urls = [f"file://{events_page_path.resolve()}"]
    events_page_path = Path(__file__).parents[2] / "dummy_pages_to_scrape/dummy_events_page/events_page.html"
    start_urls = [f"file://{events_page_path.resolve()}"]

    def parse(self, response):
        """Extract and follow links to all UFC events."""
        events_links = response.css("a.b-link.b-link_style_black::attr(href)").getall()

        # Checking if all parsed events links are indeed links
        assert all(link.startswith("http://ufcstats.com/event-details/") for link in events_links), "Not all scraped events links are links"

        yield scrapy.Request()

    def parse_event(self, response):




    def parse_fight(self, response):
