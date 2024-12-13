import scrapy
import pytest
from pathlib import Path




class Test_Stats_Spider(scrapy.Spider):
    name = "tester"
    file_path = Path(__file__).parent / "dummy_pages_to_scrape/dummy_events_page/events_page.html"
    start_urls = [f"file://{file_path.resolve()}"]

    #def parse(self, response):

