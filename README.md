# UFC Data Lab

This repository contains the collection of the UFC fights dataset, consisting of every single UFC fight data, every single UFC fighter's data and all of the UFC fight scorecards. After scraping the data, the scorecard images were OCR parsed with the help of <a href="https://github.com/PaddlePaddle/PaddleOCR">this tool</a> and then the data was further cleaned, and preprocessed. Then, as the time was to start doing EDA on UFC fights dataset, some questions were posed, which were answered in the form of EDA-driven stories by the end of the notebook. In addition, a presentation with findings from the data was created. 

<img src="preview.png">

## Results
Here's something I achieved by the end of this mini project:
* UFC fight stats scraped
* UFC scorecards scraped
* UFC Scorecards OCR-parsed
* UFC Dataset cleaned
* Dataset preprocessed
* Questions posed
* Answers given
* Presentation created


## Features
- Scraping UFC stats and scorecards.
- OCR processing of scorecard images.
- Dataset collection
- Dataset cleaning and preprocessing
- Organized dataset storage for analysis.
- Exploratory Data Anslysis.
- Presentation report on EDA and findings

## Data sources
- <a href="http://ufcstats.com/">Fight statistics</a>
- <a href="https://www.ufc.com/scorecards/">Fight scorecards</a>

## Installation
```bash
1. Clone the repository:
git clone https://github.com/komaksym/UFC-DataLab.git
2. Install miniconda and ensure it is installed:
conda --version
3. Install dependancies and create virtual env:
conda env create -f environment.yml
4. Activate the environment:
conda activate paddle_env
```

## Usage
```bash
1. To scrape  UFC stats:
cd UFC_DataLab/src/scraping/ufc_stats
scrapy crawl stats_spider

2. To scrape UFC scorecards:
cd UFC_DataLab/src/scraping/ufc_scorecards
scrapy crawl scorecards_spider

3. To OCR parse the scraped scorecards:
Move your scraped data to the datasets/scorecards/scraped_scorecard_images/new_version_scorecards/
python src/scorecard_OCR/ocr.py

4. To run tests:
pytest
```

## Directory Structure
```bash 
.
├── data                                       # Datasets & scripts related to working with them
│   ├── external_data                          # External data that we use besides our own scraped datasets
│   ├── merged_stats_n_scorecards              # Final merged dataset 
│   ├── scorecards                             # Scorecards of the fights
│   ├── src                                    # Scripts / notebooks related to working with the data
│   └── stats                                  # Fight statistics
├── src                                        # Source code directory
│   ├── EDA                                    # Exploratory Data Analysis
│   ├── scorecard_OCR                          # Scripts related to OCR parsing the scraped scorecards
│   └── scraping                               # Scraping scripts
└── tests                                      # Unit tests
    ├── OCR_parsing                            # Tests for OCR parsing scripts
    └── scrapers                               # Tests for scrapers
```
## Contribution
In the case of contribution, feel free to open an Issue or a PR! :)