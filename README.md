# Book Scraping And Data Analysis

## Description
A simple script that parses book information from a **BookDepository** website. Saves data to the **.csv** files and shows data in adn accessible form.

## Installation
NOTE: Python3 must be already installed.
```shell
git clone https://github.com/Vasyl-Poremchuk/book-scraping-and-data-analysis
cd book_scraping_and_data_analysis
python -m venv venv
venv\Scripts\activate (Windows) or source venv/bin/activate (Linux or macOS)
pip install -r requirements.txt
```

## Features
### Parse part
- The site is parsed using the **Scrapy** framework.
- The following information is extracted from each detailed page of the book:
  * Title;
  * Authors;
  * NumberOfPages;
  * Publisher;
  * PublicationDate;
  * PriceInEuros;
  * DiscountInEuros;
  * Rating;
  * NumberOfVotesGoodreads;
  * NumberOfVotesOneStar;
  * NumberOfVotesTwoStars;
  * NumberOfVotesThreeStars;
  * NumberOfVotesFourStars;
  * NumberOfVotesFiveStars;
  * BestsellersRank;
  * ISBN13;
  * Language;
  * Category.
- All data is stored in the **.csv** format.
- The following setting were used to speed up the parsing process:
`custom_settings = {"CONCURRENT_REQUESTS": 64, "CONCURRENT_REQUESTS_PER_DOMAIN": 32, "DOWNLOAD_DELAY": 0.2}`.
- **ATTENTION**: You must be polite when parsing data from the site.

### Data analysis part
- This part consists of:
  * Data Collection;
  * Data Cleaning;
  * Data Analysis;
  * Data Visualization;
  * Conclusions.
