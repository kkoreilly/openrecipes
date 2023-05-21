from scrapy.spiders import Spider
from scrapy.http import Request
from scrapy.selector import Selector
from openrecipes.spiders.thevintagemixer_spider import TheVintageMixerMixin


class TheVintageMixerFeedSpider(Spider, TheVintageMixerMixin):
    name = "thevintagemixer.feed"
    allowed_domains = ["thevintagemixer.com"]
    start_urls = [
        "http://www.thevintagemixer.com/category/vintage-mixer/feed/",
    ]

    def parse(self, response):
        xxs = Selector(response)
        links = xxs.select('//item/*[local-name()="link"]/text()').extract()

        return [Request(x, callback=self.parse_item) for x in links]
