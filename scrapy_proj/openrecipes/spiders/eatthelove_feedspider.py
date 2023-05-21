from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from openrecipes.spiders.eatthelove_spider import EattheloveMixin


class EatthelovefeedSpider(Spider, EattheloveMixin):
    name = "eatthelove.feed"
    allowed_domains = [
        "www.eatthelove.com",
        "feeds.feedburner.com",
        "feedproxy.google.com",
    ]
    start_urls = [
        "http://feeds.feedburner.com/eatthelove/feed",
    ]

    def parse(self, response):
        xxs = Selector(response)
        links = xxs.select("//link/text()").extract()

        return [Request(x, callback=self.parse_item) for x in links]
