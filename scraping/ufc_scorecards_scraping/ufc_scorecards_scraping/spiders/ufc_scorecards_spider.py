import pdb
import scrapy 
from ..items import ScorecardImagesItem


class MySpider(scrapy.Spider):
    name = "images_spider"
    allowed_domains = ["www.ufc.com", "cloudfront.net"]
    start_urls = ["https://www.ufc.com/scorecards"]

    def parse(self, response):
        event_links = response.xpath('//*[@id="block-mainpagecontent"]/div/div/div[3]/div/div/a/@href').getall()
        for event_link in event_links:
            yield scrapy.Request(url=f"https://www.ufc.com{event_link}", callback=self.parse_event)

        next_page_btn = response.xpath("//a[@title='Load more items']/@href").get()
        if next_page_btn is not None:
            next_page = response.urljoin(next_page_btn)
            yield scrapy.Request(url=next_page, callback=self.parse)

    def parse_event(self, response):
        scorecards_item = ScorecardImagesItem()
        scorecards_item['image_urls'] = response.xpath('//*[@id="block-mainpagecontent"]/div/div[2]/div/div/div[2]/div/div/div[1]/div/div/img/@src').getall()[::-1]
        yield scorecards_item
