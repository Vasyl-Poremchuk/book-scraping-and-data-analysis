# Book Scraping And Data Analysis

## Description
A simple script that parses book information from a **BookDepository** website. Saves data to the **.csv** files and shows data in and accessible form.

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
- The following information is taken from each detailed page of the book:
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
- All data is saved in the **.csv** format.
- To speed up the parsing process, the following parameters were used:
```python
CONCURRENT_REQUESTS = 64
CONCURRENT_REQUESTS_PER_DOMAIN = 32
DOWNLOAD_DELAY = 0.2
```
- To avoid the **503** status code, the **HEADERS** variable is used with **User-Agent** and other keys.
- **ATTENTION**:
  * You must be courteous when parsing data from a website.
  * If you get a different status code when parsing the BookDepository website, I highly recommend visiting this [website](https://scrapeops.io).<br> Where you can get detailed information and guidance on how to avoid this.
  * Also, you can increase or decrease the parsing speed (it depends on the power of your machine)<br> using these **CONCURRENT_REQUESTS**, **CONCURRENT_REQUESTS_PER_DOMAIN**, and **DOWNLOAD_DELAY** variables.<br> But you have to remember that you can easily block it, keep that in mind.

### Data analysis part
- This part consists of:
  * Data Collection - merge all .csv files and create a dataframe;
  * Data Cleaning - removing duplicate records, basic errors, unexpected results, etc;
  * Data Analysis - get statistical information about each column in the dataframe;
  * Data Visualization - visualize data using a bar, pie chart, etc;
  * Conclusions - draw conclusions from the available data.
