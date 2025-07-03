from typing import Iterator, List

import scrapy
from scrapy.http import Request, Response

from ..items import ScorecardImagesItem


class ScorecardsSpider(scrapy.Spider):
    name: str = "scorecards_spider"
    allowed_domains: List[str] = ["www.ufc.com", "cloudfront.net"]
    start_urls: List[str] = ["https://www.ufc.com/scorecards"]

    def parse(self, response: Response, **kwargs) -> Iterator[Request]:
        # Extract event links from the current page
        event_links: List[str] = response.xpath(
            '//*[@id="block-mainpagecontent"]/div/div/div[3]/div/div/a/@href'
        ).getall()

        # Process each event link
        for event_link in event_links:
            full_url: str = response.urljoin(event_link)
            yield scrapy.Request(url=full_url, callback=self.parse_event)

        # Handle pagination more robustly
        next_page_btn: str = response.xpath("//a[@title='Load more items']/@href").get()

        # If there are multiple next page buttons or a single next page button
        next_page: str = response.urljoin(next_page_btn)
        yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_event(self, response: Response) -> Iterator[ScorecardImagesItem]:
        # Robust image extraction with multiple XPath attempts
        image_path: str = (
            '//*[@id="block-mainpagecontent"]/div/div[2]/div/div/div[2]/div/div/div[1]/div/div/img/@src'
        )

        # Try multiple XPath expressions to find images
        found_images: List[str] = response.xpath(image_path).getall()
        if found_images:
            # Debug log the URLs
            self.logger.info(f"Found image URLs: {found_images}")

            scorecards_item: ScorecardImagesItem = ScorecardImagesItem()
            scorecards_item["image_urls"] = found_images
            yield scorecards_item
        else:
            self.logger.info("No image URLs found in response")
