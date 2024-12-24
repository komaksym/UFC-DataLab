# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import pdb
import scrapy
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline


class ScorecardImagesPipeline(ImagesPipeline):
    def __init__(self, store_url, download_func=None, settings=None):
        super().__init__(store_url, settings=settings, download_func=download_func)
        self.counter = 0

    def get_media_requests(self, item, info):
        # Add logging to debug URL processing
        for image_url in item['image_urls']:
            info.spider.logger.info(f"Requesting image: {image_url}")
            yield scrapy.Request(image_url, meta={"img_index": self.counter}, 
                                 errback=self.handle_error, dont_filter=True)
            self.counter += 1

    def file_path(self, request, response=None, info=None, *, item=None):
        img_index = request.meta["img_index"]
        return f"downloaded_images/{img_index}.jpg"

    def item_completed(self, results, item, info):
        """
        Is called when all image requests for an item are completed
        """
        image_paths = [x["path"] for ok, x in results if ok]
        if not image_paths:
            info.spider.logger.error("No images were downloaded!")
            raise DropItem("Item contains no images")
        
        adapter = ItemAdapter(item)
        adapter["images"] = image_paths
        return item
    
    def handle_error(self, failure):
        self.logger.error(f"Image download failed: {failure.value}")