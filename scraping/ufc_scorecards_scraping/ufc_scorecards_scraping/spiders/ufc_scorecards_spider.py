import scrapy 
from ..items import ScorecardImagesItem


class MySpider(scrapy.Spider):
    name = "scorecards_spider"
    allowed_domains = ["www.ufc.com", "cloudfront.net"]
    start_urls = ["https://www.ufc.com/news/official-judges-scorecards-ufc-308-topuria-vs-holloway"]

    def parse(self, response):
        scorecards_item = ScorecardImagesItem()
        scorecards_item['image_urls'] = response.xpath('//*[@id="block-mainpagecontent"]/div/div[2]/div/div/div[2]/div/div/div[1]/div/div/img/@src').getall()[::-1]
        yield scorecards_item

