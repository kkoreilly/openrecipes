from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from openrecipes.spiders.thelittlekitchen_spider import ThelittlekitchenMixin


class ThelittlekitchenfeedSpider(Spider, ThelittlekitchenMixin):
    name = "thelittlekitchen.feed"
    allowed_domains = [
        "www.thelittlekitchen.net",
    ]
    start_urls = [
        "http://www.thelittlekitchen.net/feed/",
    ]

    def parse(self, response):
        xxs = Selector(response)
        links = xxs.select("//item/*[local-name()='link']/text()").extract()

        return [Request(x, callback=self.parse_item) for x in links]
