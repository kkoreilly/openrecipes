from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from openrecipes.items import RecipeItem, RecipeItemLoader
from openrecipes.schema_org_parser import parse_recipes
from openrecipes.util import flatten


class FoodnetworkMixin(object):
    source = "food"

    def parse_item(self, response):
        # skip review pages, which are hard to distinguish from recipe pages
        # in the link extractor regex
        if response.url.endswith("/review"):
            return []

        hxs = Selector(response)
        raw_recipes = parse_recipes(hxs, {"source": self.source})
        for recipe in raw_recipes:
            if "photo" in recipe:
                recipe["photo"] = flatten(recipe["photo"])
            if "image" in recipe:
                recipe["image"] = flatten(recipe["image"])

        return [RecipeItem.from_dict(recipe) for recipe in raw_recipes]


class FoodnetworkcrawlSpider(CrawlSpider, FoodnetworkMixin):
    name = "food.com"

    allowed_domains = ["www.food.com"]

    start_urls = [
        "http://www.food.com/recipe-finder/all?pn=1",
    ]

    rules = (
        Rule(LinkExtractor(allow=("/recipe-finder/all?pn=\d+"))),
        Rule(LinkExtractor(allow=("/recipe/.+")), callback="parse_item"),
    )
