from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from openrecipes.spiders.pickypalate_spider import PickypalateMixin


class PickypalatefeedSpider(Spider, PickypalateMixin):
    name = "pickypalate.feed"
    allowed_domains = [
        "picky-palate.com",
        "feeds.feedburner.com",
        "feedproxy.google.com",
    ]
    start_urls = [
        "http://feeds.feedburner.com/PickyPalate",
    ]

    def parse(self, response):
        xxs = Selector(response)
        links = xxs.select("//item/*[local-name()='origLink']/text()").extract()

        return [Request(x, callback=self.parse_item) for x in links]
