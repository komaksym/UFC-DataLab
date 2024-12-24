import scrapy
from ufc_scorecards_scraping.items import ScorecardImagesItem
import pdb


class Scorecards_Spider(scrapy.Spider):
    name = "scorecards_spider"
    allowed_domains = ["www.ufc.com", "cloudfront.net"]
    start_urls = ["https://www.ufc.com/scorecards"]

    def parse(self, response):
        # Extract event links from the current page
        event_links = response.xpath('//*[@id="block-mainpagecontent"]/div/div/div[3]/div/div/a/@href').getall()
        
        # Process each event link
        for event_link in event_links:
            full_url = response.urljoin(event_link)
            yield scrapy.Request(url=full_url, callback=self.parse_event)
        
        # Handle pagination more robustly
        next_page_btn = response.xpath("//a[@title='Load more items']/@href").get()
        
        # If there are multiple next page buttons or a single next page button
        next_page = response.urljoin(next_page_btn)
        yield scrapy.Request(url=next_page, callback=self.parse, 
                                meta={'dont_redirect': True})
    
    def parse_event(self, response):
        # Robust image extraction with multiple XPath attempts
        image_path = '//*[@id="block-mainpagecontent"]/div/div[2]/div/div/div[2]/div/div/div[1]/div/div/img/@src'
        
        # Try multiple XPath expressions to find images
        found_images = response.xpath(image_path).getall()
        if found_images:
            # Debug log the URLs
            self.logger.info(f"Found image URLs: {found_images}")

            scorecards_item = ScorecardImagesItem()
            scorecards_item['image_urls'] = found_images
            yield scorecards_item
        else:
            self.logger.info("No image URLs found in response")