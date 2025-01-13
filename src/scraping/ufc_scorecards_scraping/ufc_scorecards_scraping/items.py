# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html
import scrapy


class ScorecardImagesItem(scrapy.Item):
    """Item class for storing UFC scorecard image data."""
    image_urls: scrapy.Field = scrapy.Field()  # List of image URLs to download
    images: scrapy.Field = scrapy.Field()      # List of downloaded image paths
