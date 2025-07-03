# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
import re
import logging
from typing import Any, Dict


logger = logging.getLogger(__name__)


class StatsPipeline:
    """Pipeline for processing and cleaning UFC fight data."""

    def __init__(self):
        self.items_processed = 0
        self.errors = 0

    def process_item(self, item, spider: Any) -> Dict[str, Any]:
        """
        Process and clean scraped UFC fight data.

        Args:
            item: Scraped item containing fight data
            spider: Spider instance that generated this item

        Returns:
            Processed item with cleaned data
        """
        try:
            adapter = ItemAdapter(item)
            self.clean_text_fields(adapter)

            # Check if the critical data is parsed
            if not self.validate_data(adapter):
                raise ValueError(f"Critical data is missing: {adapter}")

            self.process_nicknames(adapter)
            self.process_bonus(adapter)
            self.convert_percentages(adapter)

            self.items_processed += 1

            return item

        except Exception as e:
            self.errors += 1
            logger.error(f"Error processing item: {str(e)}")
            raise

    def validate_data(self, adapter: ItemAdapter) -> bool:
        """Validate critical data fields."""
        required_fields = ["red_fighter_name", "blue_fighter_name", "event_name", "event_date"]
        for field in required_fields:
            if adapter.get(field) == "-":
                return False

        return True

    def clean_text_fields(self, adapter: ItemAdapter) -> None:
        """Clean and normalize text fields."""
        for fieldname in adapter.field_names():
            value = adapter.get(fieldname, "-")
            if isinstance(value, list):
                # Join lists and clean whitespace
                value = " ".join(value)
                value = " ".join(value.replace("\n", "").split())
            else:
                try:
                    value = value.strip()
                except Exception as e:
                    logger.error(f"Error stripping field: {fieldname}", {str(e)})
                    raise
            adapter[fieldname] = value

    def process_nicknames(self, adapter: ItemAdapter) -> None:
        """Clean fighter nicknames."""
        for nickname in ["red_fighter_nickname", "blue_fighter_nickname"]:
            if adapter.get(nickname):
                adapter[nickname] = re.sub(r'["\\]', "", adapter.get(nickname) or "")

    def process_bonus(self, adapter: ItemAdapter) -> None:
        """Extract bonus type from image source."""
        bonus = adapter.get("bonus")
        if bonus and bonus != "-":
            try:
                adapter["bonus"] = re.findall(r"\w+(?=\.png)", bonus)[0]
            except IndexError:
                logger.warning(f"Could not extract bonus type from: {bonus}")
                adapter["bonus"] = "-"

    def convert_percentages(self, adapter: ItemAdapter) -> None:
        """Convert percentage strings to numeric values."""
        percentage_fields = [field for field in adapter.field_names() if field.endswith("_pct")]
        for field in percentage_fields:
            value = adapter.get(field, "-")
            if value != "-":
                try:
                    adapter[field] = str(float(value.replace("%", "")))
                except ValueError:
                    logger.warning(f"Invalid percentage value in {field}: {value}")
