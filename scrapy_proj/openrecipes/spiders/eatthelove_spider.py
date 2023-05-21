from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from openrecipes.items import RecipeItem
from openrecipes.schema_org_parser import parse_recipes


class EattheloveMixin(object):
    source = "eatthelove"

    def parse_item(self, response):
        hxs = Selector(response)
        raw_recipes = parse_recipes(hxs, {"source": self.source, "url": response.url})

        return [RecipeItem.from_dict(recipe) for recipe in raw_recipes]


class EatthelovecrawlSpider(CrawlSpider, EattheloveMixin):
    name = "eatthelove.com"

    allowed_domains = ["www.eatthelove.com"]

    start_urls = [
        "http://www.eatthelove.com/recipe-archive/",
    ]

    rules = (Rule(LinkExtractor(allow=("/\d\d\d\d/\d\d/.+/")), callback="parse_item"),)
