import scrapy
from ufc_scorecards_scraping.items import ScorecardImagesItem


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
                                meta={'dont_redirect': True, 'handle_httpstatus_list': [302]})
    
    def parse_event(self, response):
        # Robust image extraction with multiple XPath attempts
        image_paths = [
            '//*[@id="block-mainpagecontent"]/div/div[2]/div/div/div[2]/div/div/div[1]/div/div/img/@src',
            '//div[contains(@class, "scorecard-image")]//img/@src',
            '//img[contains(@class, "scorecard-image")]/@src'
        ]
        
        # Try multiple XPath expressions to find images
        image_urls = []
        for path in image_paths:
            found_images = response.xpath(path).getall()
            if found_images:
                image_urls.extend(found_images)
        
        # Remove duplicates and reverse if needed
        image_urls = list(dict.fromkeys(image_urls))[::-1]
        
        # Only yield if images are found
        if image_urls:
            scorecards_item = ScorecardImagesItem()
            scorecards_item['image_urls'] = image_urls
            yield scorecards_item