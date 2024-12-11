"""import scrapy
import pytest


class Test_Stats_Spider(scrapy.Spider):
    name = "test_stats_spider"
    start_urls = ["file:///Users/koval/dev/UFC_DataLab/tests/scrapers/stats/dummy_events_page/events_page.html"]

    def parse(self, response):"""

from pathlib import Path

import scrapy


class QuotesSpider(scrapy.Spider):
    name = "quotes"

    def start_requests(self):
        urls = [
            "https://quotes.toscrape.com/page/1/",
            "https://quotes.toscrape.com/page/2/",
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = response.url.split("/")[-2]
        filename = f"quotes-{page}.html"
        Path(filename).write_bytes(response.body)
        self.log(f"Saved file {filename}")
