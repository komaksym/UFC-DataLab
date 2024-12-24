import scrapy
from pathlib import Path
from test_scorecards_spider.items import ImageItem


class Scorecards_Spider(scrapy.Spider):
    name = "test_scorecards_spider"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create a method to generate file URLs
        def create_file_url(relative_path):
            full_path = Path(__file__).parents[2] / relative_path
            return f"file://{full_path.resolve()}"
        
        # Storing mock pages
        self.event_paths = {
            'events_page': create_file_url("dummy_pages_to_scrape/dummy_events_page/events_page.html"),
            'single_event': create_file_url("dummy_pages_to_scrape/dummy_event_page/event_page.html")
        }     

        self.start_urls = [self.event_paths['events_page']]

    def parse(self, response):
        # Extract event links from the current page
        event_links = response.xpath('//*[@id="block-mainpagecontent"]/div/div/div[3]/div/div/a/@href').getall()
        
        # Checking if all parsed links are indeed links 
        assert all(link.startswith("/news/official-judges-scorecards-")
                   for link in event_links), (
                       f"Invalid event links format. "
                       f"Expected: URLs starting with '/news/official-judges-scorecards-' ",
                       f"Got: {[link for link in event_links if not link.startswith('/news/official-judges-scorecards-')]}"
                   )

        # Handle pagination more robustly
        next_page_btn = response.xpath("//a[@title='Load more items']/@href").get()

        # Unit testing the next page button link
        assert next_page_btn.startswith("?page="), ("Invalid next page btn link format. ",
               "Expected: URL starting with '?page=' ", f"Got: {next_page_btn}")
        
        return scrapy.Request(url=self.event_paths['single_event'], callback=self.parse_event)
        
    def parse_event(self, response):
        # Robust image extraction with multiple XPath attempts
        image_path = '//*[@id="block-mainpagecontent"]/div/div[2]/div/div/div[2]/div/div/div[1]/div/div/img/@src'
        
        # Try multiple XPath expressions to find images
        found_images = response.xpath(image_path).getall()
        if found_images:
            # Unit testing the image links
            assert all(image.startswith("https://ufc.com/images/") for image in found_images), (
            "Invalid scorecard image link format. " "Expected: URL starting with 'https://ufc.com/images/'"
            f"Got: {[image for image in found_images if not image.startswith("https://ufc.com/images/")]}")
            
            # Debug log the URLs
            self.logger.info(f"Found image URLs: {found_images}")
            
            scorecards_item = ImageItem()
            scorecards_item['image_urls'] = found_images
            yield scorecards_item

        else:
            self.logger.info("No image URLs found in response")