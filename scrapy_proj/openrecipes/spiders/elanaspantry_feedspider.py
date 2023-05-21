from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from openrecipes.spiders.elanaspantry_spider import ElanaspantryMixin


class ElanaspantryfeedSpider(Spider, ElanaspantryMixin):
    name = "elanaspantry.feed"
    allowed_domains = [
        "www.elanaspantry.com",
        "feeds.feedburner.com",
        "feedproxy.google.com",
    ]
    start_urls = [
        "http://feeds.feedburner.com/elanaspantry",
    ]

    def parse(self, response):
        xxs = Selector(response)
        links = xxs.select("//item/*[local-name()='origLink']/text()").extract()

        return [Request(x, callback=self.parse_item) for x in links]
