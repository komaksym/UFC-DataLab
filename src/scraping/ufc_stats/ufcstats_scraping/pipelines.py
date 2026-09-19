# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import logging
import re
from typing import Any, Dict

from itemadapter import ItemAdapter

from .identity import (
    LEGACY_FALLBACK_STATUS,
    SOURCE_UFCSTATS,
    STABLE_IDENTITY_STATUS,
    is_missing_id,
)


logger = logging.getLogger(__name__)


class StatsPipeline:
    """Pipeline for processing and cleaning UFC fight data."""

    RESULT_ALIASES = {
        "W": "W",
        "WIN": "W",
        "L": "L",
        "LOSS": "L",
        "D": "D",
        "DRAW": "D",
        "NC": "NC",
        "N/C": "NC",
        "NO CONTEST": "NC",
        "NO-CONTEST": "NC",
    }

    def __init__(self):
        self.items_processed = 0
        self.errors = 0

    def process_item(self, item, spider: Any) -> Dict[str, Any]:
        """
        Process and clean scraped UFC fight data."""

        try:
            adapter = ItemAdapter(item)
            self.clean_text_fields(adapter)
            self.normalize_identity(adapter)
            self.normalize_results(adapter)
            self.process_fight_outcome(adapter)

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

        required_fields = [
            "red_fighter_name",
            "blue_fighter_name",
            "event_name",
            "event_date",
            "fight_outcome",
        ]
        for field in required_fields:
            if adapter.get(field) == "-":
                return False

        return True

    IDENTITY_FIELDS = frozenset(
        {
            "fight_id",
            "event_id",
            "red_fighter_id",
            "blue_fighter_id",
            "fight_url",
            "event_url",
            "red_fighter_url",
            "blue_fighter_url",
            "source",
            "identity_status",
        }
    )

    def clean_text_fields(self, adapter: ItemAdapter) -> None:
        """Clean and normalize text fields."""

        for fieldname in adapter.field_names():
            value = adapter.get(fieldname)
            if value is None:
                # Missing stable identity stays missing so the hard identity
                # check can fail loudly; other missing fields keep the legacy
                # "-" placeholder contract.
                if fieldname in self.IDENTITY_FIELDS:
                    continue
                adapter[fieldname] = "-"
                continue
            if isinstance(value, list):
                # Join lists and clean whitespace
                value = " ".join(value)
                value = " ".join(value.replace("\n", "").split())
            else:
                try:
                    value = value.strip() if isinstance(value, str) else value
                except Exception as e:
                    logger.error(f"Error stripping field: {fieldname}", {str(e)})
                    raise
            adapter[fieldname] = value

    def normalize_identity(self, adapter: ItemAdapter) -> None:
        """Validate stable UFCStats identity for a newly scraped record.

        A new scrape without ``fight_id`` is a hard identity failure and
        raises. ``identity_status=legacy_fallback`` is never assigned here;
        it is reserved for genuinely pre-ID historical records normalized in
        the dataset-processing layer, where it remains visibly warning-level.
        """

        fight_url = adapter.get("fight_url")
        if is_missing_id(fight_url):
            # Preserve provenance even when the spider propagated the URL.
            pass

        fight_id = adapter.get("fight_id")
        if is_missing_id(fight_id):
            raise ValueError(
                "Hard identity failure: newly scraped record without fight_id "
                f"(fight_url={fight_url!r}). legacy_fallback is reserved for "
                "genuinely pre-ID historical records."
            )

        for field in ("event_id", "red_fighter_id", "blue_fighter_id"):
            if is_missing_id(adapter.get(field)):
                raise ValueError(
                    f"Hard identity failure: newly scraped record without {field} "
                    f"(fight_id={fight_id!r})."
                )

        red_id = str(adapter.get("red_fighter_id")).strip()
        blue_id = str(adapter.get("blue_fighter_id")).strip()
        if red_id == blue_id:
            raise ValueError(
                f"Hard identity failure: red/blue corners share fighter_id "
                f"{red_id!r} (fight_id={fight_id!r}). Corners must stay distinct "
                "and aligned with names/results."
            )

        source = adapter.get("source")
        if is_missing_id(source):
            adapter["source"] = SOURCE_UFCSTATS

        # New scrapes with a stable fight_id are stable by construction.
        # Legacy fallback is assigned only in dataset processing for pre-ID rows.
        status = adapter.get("identity_status")
        if is_missing_id(status):
            adapter["identity_status"] = STABLE_IDENTITY_STATUS
        elif status != STABLE_IDENTITY_STATUS:
            raise ValueError(
                f"Hard identity failure: new scraped record must not carry "
                f"identity_status={status!r} (fight_id={fight_id!r}). "
                f"{LEGACY_FALLBACK_STATUS} is reserved for pre-ID history."
            )

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
                if value in {"--", "---", ""}:
                    continue
                try:
                    adapter[field] = str(float(value.replace("%", "")))
                except ValueError:
                    logger.warning(f"Invalid percentage value in {field}: {value}")

    def normalize_results(self, adapter: ItemAdapter) -> None:
        """Normalize source result markers into a small canonical set."""

        for field in ("red_fighter_result", "blue_fighter_result"):
            value = adapter.get(field, "-")
            if value == "-":
                continue

            normalized_value = self.RESULT_ALIASES.get(str(value).upper())
            if normalized_value is None:
                raise ValueError(f"Unsupported result marker for {field}: {value}")

            adapter[field] = normalized_value

    def process_fight_outcome(self, adapter: ItemAdapter) -> None:
        """Derive a fight-level outcome from the normalized red/blue result markers."""

        red_result = adapter.get("red_fighter_result", "-")
        blue_result = adapter.get("blue_fighter_result", "-")

        if red_result == "W" and blue_result == "L":
            adapter["fight_outcome"] = "red_win"
            return

        if red_result == "L" and blue_result == "W":
            adapter["fight_outcome"] = "blue_win"
            return

        if red_result == "D" and blue_result == "D":
            adapter["fight_outcome"] = "draw"
            return

        if red_result == "NC" and blue_result == "NC":
            adapter["fight_outcome"] = "no_contest"
            return

        raise ValueError(f"Unsupported fight outcome combination: {red_result}/{blue_result}")
