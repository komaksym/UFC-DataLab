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
├── src                                        # Source files
│   ├── EDA                                    # Exploratory Data Analysis
│   ├── datasets                               # Datasets
│   │   ├── merged_stats_n_scorecards          # Merged stats and scorecards dataset
│   │   ├── scorecards                         # Scorecards data
│   │   │   ├── OCR_parsed_scorecards          # OCR parsed scorecards
│   │   │   └── scraped_scorecard_images       # Scraped scorecards
│   │   └── stats                              # Fight stats data
│   ├── scorecard_OCR                          # Scorecard OCR script
│   └── scraping                               # Scraping scripts
│       ├── ufc_scorecards_scraping            # Scorecards scraper
│       │   └── ufc_scorecards_scraping        # Scorecards scraper
│       │       └── spiders                    # Scorecards spider
│       └── ufc_stats_scraping                 # Stats scraper
│           └── ufcstats_scraping              # Stats scraper
│               └── spiders                    # Stats spider
└── tests                                      # Tests
    ├── OCR_parsing                            # OCR tests
    │   └── mock_scorecard                     # Mock data to test OCR on
    └── scrapers                               # Scraper tests
        ├── test_scorecards_scraper            # Scorecard scraper testing
        │   └── mock_pages                     # Mock data to test scorecard scraper on
        │       ├── mock_event_page            # Mock single event page
        │       ├── mock_events_page           # Mock events page
        │       └── mock_scorecard             # Mock scorecard
        └── test_stats_scraper                 # Stats scraper testing
            └── mock_pages                     # Mock data to test stats scraper on
                ├── mock_event_page            # Mock single event page
                ├── mock_events_page           # Mock events page
                └── mock_fight_page            # Mock single fight page
```
