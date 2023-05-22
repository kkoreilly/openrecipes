from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from openrecipes.items import RecipeItem, RecipeItemLoader


class BBCfoodMixin(object):
    # this is the source string we'll store in the DB to aggregate stuff
    # from a single source
    source = "bbcfood"

    def parse_item(self, response):
        name_path = "//h1/text()"
        description_path = '//p[@class="recipe-description__text"]/text()'
        image_path = '//div[@class="recipe-media"]//div//img/@src'
        prepTime_path = '//p[@class="recipe-metadata__prep-time"]/@content'
        cookTime_path = '//p[@class="recipe-metadata__cook-time"]/@content'
        recipeYield_path = '//p[@class="recipe-metadata__serving"]/text()'
        ingredients_path = '//li[@class="recipe-ingredients__list-item"]'

        recipes = []

        il = RecipeItemLoader(item=RecipeItem())
        il.add_value("source", self.source)
        il.add_value("url", response.url)
        il.add_value("name", response.xpath(name_path).get())
        il.add_value("description", response.xpath(description_path).get())
        il.add_value("image", response.xpath(image_path).get())

        il.add_value("prepTime", response.xpath(prepTime_path).get())
        il.add_value("cookTime", response.xpath(cookTime_path).get())
        il.add_value("recipeYield", response.xpath(recipeYield_path).get())

        ingredient_scopes = response.xpath(ingredients_path)
        ingredients = []
        for i_scope in ingredient_scopes:
            amount = i_scope.xpath("text()[1]").getall()
            name = i_scope.xpath("a/text()").getall()
            amount = "".join(amount).strip()
            name = "".join(name).strip()
            ingredients.append("%s %s" % (amount, name))
        il.add_value("ingredients", ingredients)
        recipes.append(il.load_item())

        # for r_scope in recipes_scopes:
        #     il = RecipeItemLoader(item=RecipeItem())

        #     il.add_value("source", self.source)
        #     il.add_value("name", r_scope.xpath(name_path).extract())
        #     il.add_value("image", r_scope.xpath(image_path).extract())
        #     il.add_value("url", response.url)
        #     il.add_value("description", r_scope.xpath(description_path).extract())

        #     il.add_value("prepTime", r_scope.xpath(prepTime_path).extract())
        #     il.add_value("cookTime", r_scope.xpath(cookTime_path).extract())
        #     il.add_value("recipeYield", r_scope.xpath(recipeYield_path).extract())

        #     ingredient_scopes = r_scope.xpath(ingredients_path)
        #     ingredients = []
        #     for i_scope in ingredient_scopes:
        #         amount = i_scope.xpath("text()[1]").extract()
        #         name = i_scope.xpath("a/text()").extract()
        #         amount = "".join(amount).strip()
        #         name = "".join(name).strip()
        #         ingredients.append("%s %s" % (amount, name))
        #     il.add_value("ingredients", ingredients)

        #     recipes.append(il.load_item())

        return recipes


class BBCfoodcrawlSpider(CrawlSpider, BBCfoodMixin):
    name = "bbcfood"
    allowed_domains = ["bbc.co.uk"]
    start_urls = [
        "https://www.bbc.co.uk/food/chefs",
    ]

    rules = (
        Rule(LinkExtractor(allow=("/food/chefs/.+"))),
        Rule(
            LinkExtractor(allow=("food/recipes/(?!search).+")),
            callback="parse_item",
        ),
    )
