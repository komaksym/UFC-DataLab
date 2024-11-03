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
    def get_media_requests(self, item, info): 
        for i, image_url in enumerate(item['image_urls']):
            yield scrapy.Request(image_url, meta={"img_index": i})

    def file_path(self, request, response=None, info=None, *, item=None):
        img_index = request.meta["img_index"]
        return f"scorecard_images_results/{img_index}.jpg"

    def item_completed(self, results, item, info):
        #pdb.set_trace()
        image_paths = [x["path"] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        adapter = ItemAdapter(item)
        adapter["images"] = image_paths
        return item
    