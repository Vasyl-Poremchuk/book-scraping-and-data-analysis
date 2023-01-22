import os.path
from typing import Generator, Any
from urllib.parse import urljoin

import scrapy
from datetime import datetime

from scrapy.crawler import CrawlerProcess

BASE_URL = "https://www.bookdepository.com"
PATH = "search?searchTerm=books&category="
CATEGORY_URL = urljoin(BASE_URL, PATH)


def parse_all_categories(
    folder_name: str, categories: dict[str, str],
) -> None:
    """
    The function checks if the folder exists, runs the spider,
    and saves the parsed data to a file.
    """
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)

    for category, identifier in categories.items():
        process = CrawlerProcess(
            {
                "FEED_URI": f"{folder_name}/{category}.csv",
                "FEED_FORMAT": "csv",
            }
        )
        process.crawl(
            BookSpider,
            category=category,
            endpoint=f"{CATEGORY_URL}{identifier}",
        )
        process.start()


class BookSpider(scrapy.Spider):
    name = "bookdepository"
    allowed_domains = ["bookdepository.com"]
    number_of_pages = 333

    HEADERS = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:98.0) "
        "Gecko/20100101 Firefox/98.0",
        "Accept": "text/html,application/xhtml+xml,"
        "application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Accept-Encoding": "gzip, deflate",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    custom_settings = {
        "CONCURRENT_REQUESTS": 64,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 32,
        "DOWNLOAD_DELAY": 0.2,
    }

    def __init__(
        self, category: str, endpoint: str, *args: Any, **kwargs: Any
    ) -> None:
        super().__init__(*args, **kwargs)
        self.category = category
        self.endpoint = endpoint

    def start_requests(self) -> Generator:
        """
        The method is defined as a generator function that yields instances
        of the `scrapy.Request` class, which is used to initiate web requests.
        """
        for number in range(1, self.number_of_pages + 1):
            url = f"{self.endpoint}&page={str(number)}"

            yield scrapy.Request(
                url=url, callback=self.parse_pages, headers=self.HEADERS,
            )

    def parse_pages(
        self, response: Any, *args: Any, **kwargs: Any
    ) -> Generator:
        """
        The method is called by the `start_requests` method and is used
        to parse the pages returned by the web scraper.
        """
        for href in response.css(".title > a::attr(href)").getall():
            url = response.urljoin(href)

            yield scrapy.Request(
                url=url, callback=self.parse, headers=self.HEADERS,
            )

    def parse(self, response: Any, *args: Any, **kwargs: Any) -> Generator:
        """
        The method is used to extract relevant information from the book
        pages of the website.
        """
        title = response.css("h1[itemprop='name']::text").get()
        authors = ", ".join(
            full_name.strip()
            for full_name in response.css(
                ".author-info > span[itemprop='author'] > a > span[itemprop='name']::text"
            ).getall()
        )
        rating = (
            response.css("span[itemprop='ratingValue']::text").get().strip()
        )
        rating_details = [
            rating.strip().split(" (")[-1].strip(")").replace(",", "")
            for rating in response.css(
                ".rating-distribution-entry::text"
            ).getall()
            if "%" in rating
        ]
        number_of_votes_goodreads = (
            response.css(".rating-count::text")
            .get()
            .strip("\n ()")
            .split()[0]
            .replace(",", "")
        )
        price_in_euros = (
            response.css(".sale-price::text")
            .get()
            .strip(" €")
            .replace(",", ".")
        )
        discount_in_euros = (
            response.css(".price-save::text")
            .get()
            .strip("\n €")
            .split()[-1]
            .replace(",", ".")
        )
        number_of_pages = (
            response.css("span[itemprop='numberOfPages']::text")
            .get()
            .strip(" pages\n")
        )
        publication_date = response.css(
            "span[itemprop='datePublished']::text"
        ).get()
        publisher = (
            response.css(
                "span[itemprop='publisher'] > a > span[itemprop='name']::text"
            )
            .get()
            .strip()
        )
        language = response.css("span[itemprop='inLanguage'] > a::text").get()
        isbn13 = response.css("span[itemprop='isbn']::text").get()
        bestsellers_rank = (
            response.css(".biblio-info > li > span::text")
            .getall()[-1]
            .strip()
            .replace(",", "")
        )

        yield {
            "title": title,
            "authors": authors,
            "number_of_pages": number_of_pages,
            "publisher": publisher,
            "publication_date": datetime.strptime(
                publication_date, "%d %b %Y"
            ).date(),
            "price_in_euros": price_in_euros,
            "discount_in_euros": 0 or discount_in_euros,
            "rating": rating,
            "number_of_votes_goodreads": number_of_votes_goodreads,
            "number_of_votes_one_star": rating_details[4],
            "number_of_votes_two_stars": rating_details[3],
            "number_of_votes_three_stars": rating_details[2],
            "number_of_votes_four_stars": rating_details[1],
            "number_of_votes_five_stars": rating_details[0],
            "bestsellers_rank": bestsellers_rank,
            "isbn13": isbn13,
            "language": language,
            "category": self.category.title().replace("_", ", "),
        }


if __name__ == "__main__":
    parse_all_categories("books_data", {"art_photography": "2"})
    parse_all_categories("books_data", {"biography": "213"})
    parse_all_categories("books_data", {"business_finance_law": "928"})
    parse_all_categories("books_data", {"children_books": "2455"})
    parse_all_categories("books_data", {"computing": "1897"})
    parse_all_categories("books_data", {"crafts_hobbies": "2492"})
    parse_all_categories("books_data", {"crime_thriller": "2616"})
    parse_all_categories("books_data", {"dictionaries_languages": "240"})
    parse_all_categories("books_data", {"entertainment": "3245"})
    parse_all_categories("books_data", {"fiction": "333"})
    parse_all_categories("books_data", {"food_drink": "2858"})
    parse_all_categories("books_data", {"graphic_novels_anime_manga": "2633"})
    parse_all_categories("books_data", {"health": "2770"})
    parse_all_categories("books_data", {"history_archaeology": "2638"})
    parse_all_categories("books_data", {"home_garden": "2892"})
    parse_all_categories("books_data", {"humour": "2978"})
    parse_all_categories("books_data", {"medical": "1279"})
    parse_all_categories("books_data", {"mind_body_spirit": "2819"})
    parse_all_categories("books_data", {"natural_history": "2985"})
    parse_all_categories("books_data", {"personal_development": "2802"})
    parse_all_categories("books_data", {"poetry_drama": "283"})
    parse_all_categories("books_data", {"reference": "375"})
    parse_all_categories("books_data", {"religion": "3120"})
    parse_all_categories("books_data", {"romance": "2630"})
    parse_all_categories("books_data", {"science_geography": "1476"})
    parse_all_categories(
        "books_data", {"science_fiction_fantasy_horror": "2623"}
    )
    parse_all_categories("books_data", {"society_social_sciences": "632"})
    parse_all_categories("books_data", {"sport": "3013"})
    parse_all_categories("books_data", {"stationery": "3385"})
    parse_all_categories(
        "books_data", {"teaching_resources_education": "3328"}
    )
    parse_all_categories("books_data", {"technology_engineering": "1708"})
    parse_all_categories("books_data", {"transport": "2967"})
    parse_all_categories("books_data", {"travel_holiday_guides": "3098"})
