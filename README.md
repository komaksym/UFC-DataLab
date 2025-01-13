# UFC Data Lab

This repo collects, preprocesses and does EDA on UFC Fight data, including stats, scorecards, and OCR-processed results.

## Features
- Scraping UFC stats and scorecards.
- OCR processing of scorecard images.
- Organized dataset storage for analysis.
- Exploratory Data Anslysis.

## Installation
```bash
1. Clone the repository:
git clone https://github.com/komaksym/UFC-DataLab.git
2. Ensure conda is installed:
conda --version
3. Install dependancies and create virtual env:
conda env create -f environment.txt
4. Activate the environment:
conda activate paddle_env
```

## Usage
```bash
1. To scrape  UFC stats:
cd src/scraping/ufc_stats_scraping
scrapy crawl stats_spider

2. To scrape UFC scorecards:
cd src/scraping/ufc_scorecards_scraping
scrapy crawl scorecards_spider

3. To OCR parse the scraped scorecards:
Move your scraped data to the datasets/scorecards/scraped_scorecard_images/new_version_scorecards/
python src/scorecard_OCR/app.py

4. To run tests:
pytest
```

## Directory Structure
```bash 
. 
├── src
│   ├── EDA
│   ├── datasets
│   │   ├── merged_stats_n_scorecards
│   │   ├── scorecards
│   │   │   ├── OCR_parsed_scorecards
│   │   │   └── scraped_scorecard_images
│   │   └── stats
│   ├── scorecard_OCR
│   └── scraping
│       ├── ufc_scorecards_scraping
│       │   └── ufc_scorecards_scraping
│       │       └── spiders
│       └── ufc_stats_scraping
│           └── ufcstats_scraping
│               └── spiders
└── tests
    ├── OCR_parsing
    │   └── mock_scorecard
    └── scrapers
        ├── test_scorecards_scraper
        │   └── mock_pages
        │       ├── mock_event_page
        │       ├── mock_events_page
        │       └── mock_scorecard
        └── test_stats_scraper
            └── mock_pages
                ├── mock_event_page
                ├── mock_events_page
                └── mock_fight_page.
```
