from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from openrecipes.spiders.smittenkitchen_spider import SmittenkitchenMixin


class SmittenkitchenfeedSpider(Spider, SmittenkitchenMixin):
    name = "smittenkitchen.feed"
    allowed_domains = [
        "smittenkitchen.com",
        "feeds.feedburner.com",
        "feedproxy.google.com",
    ]
    start_urls = [
        "http://feeds.feedburner.com/smittenkitchen",
    ]

    def parse(self, response):
        xxs = Selector(response)
        links = xxs.select("TODO").extract()

        return [Request(x, callback=self.parse_item) for x in links]
