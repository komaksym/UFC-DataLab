# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import re
import pdb


class UfcstatsScrapingPipeline:

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)

        # Stripping whitespaces 
        for fieldname in adapter.field_names():
            value = adapter.get(fieldname)
            
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

        # Removing extra symbols from the nicknames
        if adapter.get('red_fighter_nickname') is not None:
            adapter['red_fighter_nickname'] = re.sub(r'["\\]', '', adapter.get('red_fighter_nickname'))

        if adapter.get('blue_fighter_nickname') is not None:
            adapter['blue_fighter_nickname'] = re.sub(r'["\\]', '', adapter.get('blue_fighter_nickname'))

        # Extracting the bonus type from the img src attribute
        if adapter.get('bonus') is not None:
            if adapter.get('bonus') != "-":
                adapter['bonus'] = re.findall(r"\w+(?=\.png)", adapter.get('bonus'))[0]

        return item
