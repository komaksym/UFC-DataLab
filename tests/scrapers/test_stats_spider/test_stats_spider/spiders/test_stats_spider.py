import scrapy
from pathlib import Path


class Test_Stats_Spider(scrapy.Spider):
    name = "tester"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Create a method to generate file URLs
        def create_file_url(relative_path):
            full_path = Path(__file__).parents[2] / relative_path
            return f"file://{full_path.resolve()}"
        
        # Storing mock pages
        self.event_paths = {
            'events_page': create_file_url("dummy_pages_to_scrape/dummy_events_page/events_page.html"),
            'single_event': create_file_url("dummy_pages_to_scrape/dummy_event_page/single_event_page.html"),
            'single_fight': create_file_url("dummy_pages_to_scrape/dummy_fight_page/fight_page.html")
        }        
        print(f"\n\n{self.event_paths['single_event']}\n\n")
    
        self.start_urls = [self.event_paths['events_page']]
                           
    def parse(self, response):
        """Extract and follow links to all UFC events."""
        events_links = response.css("a.b-link.b-link_style_black::attr(href)").getall()
        print('\n' + events_links[0] + '\n')

        # Checking if all parsed events links are indeed links
        assert all(link.startswith("http://ufcstats.com/event-details/") for link in events_links), "Not all scraped events links are links"

        return scrapy.Request(url=self.event_paths['single_event'], callback=self.parse_event, errback=self.handle_error)

    def parse_event(self, response):
        """Extract event data and follow links to individual fights."""
        event_data = {
            "name": response.css("h2.b-content__title span::text").get("-"),
            "date": response.css("li.b-list__box-list-item:nth-child(1)::text").get("-").strip(),
            "location": response.css("li.b-list__box-list-item:nth-child(2)::text").get("-").strip()
        }

        fights_links = response.css("a.b-flag.b-flag_style_green::attr(href)").getall()

        # Checking if all parsed fights links are indeed links
        #assert(all(link..))
        

    def parse_fight(self, response):
        pass

    def handle_error(self, failure):
        """Handle request failures"""
        self.logger.error(f"Request failed: {failure.request.url}")
        self.logger.error(f"Error: {failure.value}")