# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging
from typing import Iterator, List, Tuple

from itemadapter import ItemAdapter
from scrapy.exceptions import DropItem
from scrapy.http import Request
from scrapy.pipelines.images import ImagesPipeline
from scrapy.pipelines.media import MediaPipeline

from .items import ScorecardImagesItem


class ScorecardImagesPipeline(ImagesPipeline):
    def __init__(self, store_url, download_func=None, settings=None) -> None:
        super().__init__(store_url, settings=settings, download_func=download_func)
        self.counter: int = 0
        self.logger: logging.Logger = logging.getLogger(__name__)

    
    def get_media_requests(  # pyright: ignore[reportIncompatibleMethodOverride] (the return type follows scrapy docs)
        self, item: ScorecardImagesItem, info: MediaPipeline.SpiderInfo
    ) -> Iterator[Request]:
        """Gets the URLs of the images."""

        for image_url in item["image_urls"]:
            # Add logging to debug URL processing
            info.spider.logger.info(f"Requesting image: {image_url}")
            yield Request(
                image_url, meta={"img_index": self.counter}, errback=self.handle_error, dont_filter=True
            )
            self.counter += 1

    def file_path(self, request: Request, response=None, info=None, *, item=None) -> str:
        """Names images by their index count."""

        img_index: int = request.meta["img_index"]
        return f"downloaded_images/{img_index}.jpg"

    def item_completed(
        self,
        results: List[Tuple[bool, dict]],
        item: ScorecardImagesItem,
        info: MediaPipeline.SpiderInfo,
    ) -> ScorecardImagesItem:
        """
        Saves images when all image requests for an item are completed.
        """

        image_paths: List[str] = [x["path"] for ok, x in results if ok]
        if not image_paths:
            info.spider.logger.error("No images were downloaded!")
            raise DropItem("Item contains no images")

        adapter: ItemAdapter = ItemAdapter(item)
        adapter["images"] = image_paths
        return item

    def handle_error(self, failure) -> None:
        self.logger.error(f"Image download failed: {failure.value}")
