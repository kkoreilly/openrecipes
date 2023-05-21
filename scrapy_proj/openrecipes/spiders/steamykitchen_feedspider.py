from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from openrecipes.spiders.steamykitchen_spider import SteamykitchenMixin


class SteamykitchenfeedSpider(Spider, SteamykitchenMixin):
    name = "steamykitchen.feed"

    allowed_domains = [
        "steamykitchen.com",
        "feeds.feedburner.com",
        "feedproxy.google.com",
    ]
    start_urls = [
        "http://feeds.feedburner.com/SteamyKitchen",
    ]

    def parse(self, response):
        xxs = Selector(response)
        links = xxs.select("//item/*[local-name()='origLink']/text()").extract()

        return [Request(x, callback=self.parse_item) for x in links]
