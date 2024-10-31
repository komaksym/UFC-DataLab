# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.exporters import CsvItemExporter
import re
import pdb


class UfcstatsScrapingPipeline:

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Stripping whitespaces 
        for fieldname in adapter.field_names():
            value = adapter.get(fieldname, "-")
            
            # Remove %
            if '%' in value:
                value = re.sub("%", "", value)

            # If it's a list, join into a string
            if isinstance(value, list):
                value = " ".join(value)
                value = value.replace("\n", "").split()
                adapter[fieldname] = " ".join(value)

            else:
                adapter[fieldname] = value.strip()

        # Removing extra symbols from fighter nicknames
        fighter_nicknames = ['red_fighter_nickname', 'blue_fighter_nickname']
        for nickname in fighter_nicknames:
            if adapter.get(nickname) is not None:
                adapter[nickname] = re.sub(r'["\\]', '', adapter.get(nickname))

        # Extracting the bonus type from the img src attribute
        if adapter.get('bonus') is not None:
            if adapter.get('bonus') != "-":
                adapter['bonus'] = re.findall(r"\w+(?=\.png)", adapter.get('bonus'))[0]

        return item
