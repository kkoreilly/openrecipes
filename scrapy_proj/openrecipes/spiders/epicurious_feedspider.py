from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from openrecipes.spiders.epicurious_spider import EpicuriousMixin


class EpicuriousfeedSpider(Spider, EpicuriousMixin):
    """
    Uses the Epicurious recipes feed to get newly added items.
    """

    name = "epicurious.feed"
    allowed_domains = ["epicurious.com"]
    start_urls = [
        "http://feeds.epicurious.com/newrecipes",
    ]

    def parse(self, response):
        xxs = Selector(response)
        links = xxs.select("//item/*[local-name()='origLink']/text()").extract()

        return [Request(x, callback=self.parse_item) for x in links]
