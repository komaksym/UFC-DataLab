# UFC Fights Dataset Collection

This repo collects and organizes UFC Fight data, including stats, scorecards, and OCR-processed results. It provides tools for scraping, parsing, and analyzing fight information, making it useful for sports analytics, machine learning and research.

## Features
- Scraping UFC stats and scorecards.
- OCR processing of scorecard images.
- Organized dataset storage for analysis.

## Installation
```bash
1. Clone the repository:
git clone https://github.com/komaksym/UFC_fights_dataset_collection.git

2. Install dependancies:
pip install -r requirements.txt
```

## Usage
```bash
1. To scrape  UFC stats:
cd scraping/ufc_stats_scraping
scrapy crawl ufc_spider -O results.json

2. To scrape UFC scorecards:
cd scraping/ufc_scorecards_scraping
scrapy crawl ufc_scorecards

3. To OCR parse the scraped scorecards:
python scorecard_OCR/app.py

## Directory Structure
.
├- datasets			                    # Contains collected and processed data
│       
├── merged_stats_n_scorecards                    # Merged scorecard images and stats
│   ├── scorecards                               # Scorecard images and OCR results
│   │   ├── OCR_parsed_scorecards                # OCR parsed scorecards into .csv
│   │   └── scraped_scorecard_images             # Scraped scorecards (images in .jpg format)
│   │       ├── new_version_scorecards           # New version scorecards (.jpg)
│   │       ├── old_version_scorecards           # Old version scorecards (.jpg)
│   │       └── pre-new_version_scorecards       # Pre-new version scorecards (.jpg)
│   └── stats                                    # Fight stats (.csv)
├── scorecard_OCR                                # Script for OCR parsing the scorecards images
└── scraping                                     # Scraping folder
    ├── ufc_scorecards_scraping                  # Scorecard scraper
    │   └── ufc_scorecards_scraping              # Scorecard scraper sub-folder
    │       └── spiders                          # Scorecard spiders
    └── ufc_stats_scraping                       # Stats scraper
        └── ufcstats_scraping                    # Stats scraper sub-folder
            └── spiders                          # Stats spiders
