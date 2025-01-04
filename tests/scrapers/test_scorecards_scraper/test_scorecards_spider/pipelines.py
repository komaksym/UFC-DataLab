# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import scrapy
from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline


class TestScorecardImagesPipeline(ImagesPipeline):
    def __init__(self, store_url, download_func=None, settings=None):
        super().__init__(store_url, settings=settings, download_func=download_func)
        self.counter = 0

    # Gets the URLs of the images
    def get_media_requests(self, item, info): 
        for image_url in item['image_urls']:
            # Logging to debug URL processing
            info.spider.logger.info(f"Requesting image: {image_url}")
            yield scrapy.Request(image_url, meta={"img_index": self.counter},
                                 errback=self.handle_error, dont_filter=True)
            self.counter += 1

    # Specifies a custom path & name
    def file_path(self, request, response=None, info=None, *, item=None):
        img_index = request.meta["img_index"]
        # Unit testing the index
        assert isinstance(img_index, int), ("Invalid image index. "
               "Expected an integer. " f"Got: {img_index}")
        
        return f"scorecard_images_results/{img_index}.jpg"

    def item_completed(self, results, item, info):
        """
        Is called when all image requests for an item are completed,
        where we store the download paths
        """
        image_paths = [x["path"] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        adapter = ItemAdapter(item)
        adapter["images"] = image_paths
        return item

    def handle_error(self, error):
        self.logger.error(f"Image download failed: {error.value}")