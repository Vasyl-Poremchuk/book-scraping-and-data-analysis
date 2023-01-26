import os.path
from typing import Generator, Any
from urllib.parse import urljoin

import scrapy
from datetime import datetime, date

from scrapy.crawler import CrawlerProcess

BASE_URL = "https://www.bookdepository.com"
PATH = "search?searchTerm=books&category="
CATEGORY_URL = urljoin(BASE_URL, PATH)
NUMBER_OF_PAGES = 333
CONCURRENT_REQUESTS = 64
CONCURRENT_REQUESTS_PER_DOMAIN = 32
DOWNLOAD_DELAY = 0.2
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


def parse_all_categories(folder_name: str, categories: dict[str, str]) -> None:
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

    custom_settings = {
        "CONCURRENT_REQUESTS": CONCURRENT_REQUESTS,
        "CONCURRENT_REQUESTS_PER_DOMAIN": CONCURRENT_REQUESTS_PER_DOMAIN,
        "DOWNLOAD_DELAY": DOWNLOAD_DELAY,
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
        for number in range(1, NUMBER_OF_PAGES + 1):
            url = f"{self.endpoint}&page={str(number)}"

            yield scrapy.Request(
                url=url, callback=self.parse_pages, headers=HEADERS
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

            yield scrapy.Request(url=url, callback=self.parse, headers=HEADERS)

    @staticmethod
    def parse_title(response: Any) -> str:
        """
        The method returns the parsed `title`
        from the detailed book page.
        """
        title = response.css("h1[itemprop='name']::text").get()

        return title

    @staticmethod
    def parse_authors(response: Any) -> str:
        """
        The method returns the parsed `authors`
        from the detailed book page.
        """
        authors = ", ".join(
            full_name.strip()
            for full_name in response.css(
                ".author-info > span[itemprop='author'] > a > span[itemprop='name']::text"
            ).getall()
        )

        return authors

    @staticmethod
    def parse_rating(response: Any) -> str:
        """
        The method returns the parsed `rating`
        from the detailed book page.
        """
        rating = (
            response.css("span[itemprop='ratingValue']::text").get().strip()
        )

        return rating

    @staticmethod
    def parse_rating_details(response: Any) -> list[str]:
        """
        The method returns the parsed `rating_details`
        from the detailed book page.
        """
        rating_details = [
            rating.strip().split(" (")[-1].strip(")").replace(",", "")
            for rating in response.css(
                ".rating-distribution-entry::text"
            ).getall()
            if "%" in rating
        ]

        return rating_details

    @staticmethod
    def parse_number_of_votes_goodreads(response: Any) -> str:
        """
        The method returns the parsed `number_of_votes_goodreads`
        from the detailed book page.
        """
        number_of_votes_goodreads = (
            response.css(".rating-count::text")
            .get()
            .strip("\n ()")
            .split()[0]
            .replace(",", "")
        )

        return number_of_votes_goodreads

    @staticmethod
    def parse_price_in_euros(response: Any) -> str:
        """
        The method returns the parsed `price_in_euros`
        from the detailed book page.
        """
        price_in_euros = (
            response.css(".sale-price::text")
            .get()
            .strip(" €")
            .replace(",", ".")
        )

        return price_in_euros

    @staticmethod
    def parse_discount_in_euros(response: Any) -> str:
        """
        The method returns the parsed `discount_in_euros`
        from the detailed book page.
        """
        discount_in_euros = (
            response.css(".price-save::text")
            .get()
            .strip("\n €")
            .split()[-1]
            .replace(",", ".")
        )

        return 0 or discount_in_euros

    @staticmethod
    def parse_number_of_pages(response: Any) -> str:
        """
        The method returns the parsed `number_of_pages`
        from the detailed book page.
        """
        number_of_pages = (
            response.css("span[itemprop='numberOfPages']::text")
            .get()
            .strip(" pages\n")
        )

        return number_of_pages

    @staticmethod
    def parse_publication_date(response: Any) -> date:
        """
        The method returns the parsed `publication_date`
        from detailed book page.
        """
        publication_date = response.css(
            "span[itemprop='datePublished']::text"
        ).get()

        return datetime.strptime(publication_date, "%d %b %Y").date()

    @staticmethod
    def parse_publisher(response: Any) -> str:
        """
        The method returns the parsed `publisher`
        from the detailed book page.
        """
        publisher = (
            response.css(
                "span[itemprop='publisher'] > a > span[itemprop='name']::text"
            )
            .get()
            .strip()
        )

        return publisher

    @staticmethod
    def parse_language(response: Any) -> str:
        """
        The method returns the parsed `language`
        from the detailed book page.
        """
        language = response.css("span[itemprop='inLanguage'] > a::text").get()

        return language

    @staticmethod
    def parse_isbn13(response: Any) -> str:
        """
        The method returns the parsed `isbn13`
        from the detailed book page.
        """
        isbn13 = response.css("span[itemprop='isbn']::text").get()

        return isbn13

    @staticmethod
    def parse_bestsellers_rank(response: Any) -> str:
        """
        The method returns the parsed `bestsellers_rank`
        from the detailed book page.
        """
        bestsellers_rank = (
            response.css(".biblio-info > li > span::text")
            .getall()[-1]
            .strip()
            .replace(",", "")
        )

        return bestsellers_rank

    def get_category(self):
        """
        The method returns the `category` of the book.
        """
        category = self.category.title().replace("_", ", ")

        return category

    def parse(self, response: Any, *args: Any, **kwargs: Any) -> Generator:
        """
        The method is used to extract relevant information from the book
        pages of the website.
        """
        yield {
            "title": self.parse_title(response),
            "authors": self.parse_authors(response),
            "number_of_pages": self.parse_number_of_pages(response),
            "publisher": self.parse_publisher(response),
            "publication_date": self.parse_publication_date(response),
            "price_in_euros": self.parse_price_in_euros(response),
            "discount_in_euros": self.parse_discount_in_euros(response),
            "rating": self.parse_rating(response),
            "number_of_votes_goodreads": self.parse_number_of_votes_goodreads(
                response
            ),
            "number_of_votes_one_star": self.parse_rating_details(response)[4],
            "number_of_votes_two_stars": self.parse_rating_details(response)[
                3
            ],
            "number_of_votes_three_stars": self.parse_rating_details(response)[
                2
            ],
            "number_of_votes_four_stars": self.parse_rating_details(response)[
                1
            ],
            "number_of_votes_five_stars": self.parse_rating_details(response)[
                0
            ],
            "bestsellers_rank": self.parse_bestsellers_rank(response),
            "isbn13": self.parse_isbn13(response),
            "language": self.parse_language(response),
            "category": self.get_category(),
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
