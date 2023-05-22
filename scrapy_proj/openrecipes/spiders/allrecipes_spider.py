from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from openrecipes.items import RecipeItem, RecipeItemLoader
from openrecipes.util import parse_time
import json
import logging


class AllrecipescrawlSpider(CrawlSpider):
    name = "allrecipes.com"
    allowed_domains = ["allrecipes.com"]
    start_urls = [
        # all of the recipes are linked from this page
        "https://www.allrecipes.com/recipes-a-z-6735880",
    ]

    # http://allrecipes.com/recipe/-applesauce-pumpkin-bread/detail.aspx
    # a tuple of Rules that are used to extract links from the HTML page
    rules = (
        # this rule has no callback, so these links will be followed and mined
        # for more URLs. This lets us page through the recipe archives
        # there are some recipes pages with the word recipes in the middle, which is why we need to allow characters before
        Rule(LinkExtractor(allow=("/.*recipes/.*"))),
        # this rule is for recipe posts themselves. The callback argument will
        # process the HTML on the page, extract the recipe information, and
        # return a RecipeItem object
        # there are some recipe pages with the word recipe in the middle, which is why we need to allow characters before and after (but prevent s after to avoid 'recipes')
        Rule(LinkExtractor(allow=("/.*recipe[^s].*")), callback="parse_item"),
    )

    def parse_item(self, response):
        data = json.loads(
            response.xpath('//script[@type="application/ld+json"]//text()').get()
        )[0]

        # name_path = "//h1/text()"
        # description_path = ".article-subheading::text"
        # image_path = ".primary-image__image::attr(src), img.universal-image__image::attr(src)"  # need second thing for when there is a video
        # rating_path = ".mntl-recipe-review-bar__rating::text"
        # date_path = ".mntl-attribution__item-date::text"
        # creator_path = '//a[@class="mntl-attribution__item-name"]/text()'

        # prepTime_path = '//div[text()="Prep Time:"]/following::div[@class="mntl-recipe-details__value"]/text()'
        # cookTime_path = '//div[text()="Cook Time:"]/following::div[@class="mntl-recipe-details__value"]/text()'
        # totalTime_path = '//div[text()="Total Time:"]/following::div[@class="mntl-recipe-details__value"]/text()'
        # recipeYield_path = '//div[text()="Servings:"]/following::div[@class="mntl-recipe-details__value"]/text()'

        # calories_path = '//span[text()="Calories"]/following::span/text()'
        # carbohydrate_path = '//span[text()="Total Carbohydrate"]/following::text()'
        # cholesterol_path = '//span[text()="Cholesterol"]/following::text()'
        # fat_path = '//span[text()="Total Fat"]/following::text()'
        # fiber_path = '//span[text()="Dietary Fiber"]/following::text()'
        # protein_path = '//span[text()="Protein"]/following::text()'
        # saturatedFat_path = '//span[text()="Saturated Fat"]/following::text()'
        # sodium_path = '//span[text()="Sodium"]/following::text()'
        # sugar_path = '//span[text()="Total Sugars"]/following::text()'

        vitaminC_path = '//span[text()="Vitamin C"]/following::text()'
        calcium_path = '//span[text()="Calcium"]/following::text()'
        iron_path = '//span[text()="Iron"]/following::text()'
        potassium_path = '//span[text()="Potassium"]/following::text()'

        # ingredients_path = '//li[@class="mntl-structured-ingredients__list-item "]//p'

        recipes = []

        il = RecipeItemLoader(item=RecipeItem())
        il.add_value("source", "allrecipes")
        il.add_value("name", data["name"])
        image = data["image"]
        if image != None:
            il.add_value("image", image["url"])
        il.add_value("url", response.url)
        il.add_value("description", data["description"])
        rating = data["aggregateRating"]
        if rating != None:
            il.add_value("ratingValue", rating["ratingValue"])
            il.add_value("ratingCount", rating["ratingCount"])
        # rating_str = response.css(rating_path).get()
        # if rating_str != None:
        #     il.add_value("rating", rating_str[1:])  # need to get rid of space at start
        # date_str = response.css(date_path).get()
        # if date_str != None:
        #     il.add_value(
        #         "datePublished",
        #         date_str.replace("Updated on ", "").replace("Published on ", ""),
        #     )
        il.add_value("datePublished", data["datePublished"])
        il.add_value("dateModified", data["dateModified"])
        il.add_value("creator", data["author"][0]["name"])
        il.add_value("prepTime", data["prepTime"])
        il.add_value("cookTime", data["cookTime"])
        il.add_value("totalTime", data["totalTime"])
        il.add_value("recipeYield", data["recipeYield"])
        il.add_value("recipeCategory", data["recipeCategory"])
        il.add_value("recipeCuisine", data["recipeCuisine"])

        il.add_value("calories", data["nutrition"]["calories"])
        il.add_value("carbohydrateContent", data["nutrition"]["carbohydrateContent"])
        il.add_value("cholesterolContent", data["nutrition"]["cholesterolContent"])
        il.add_value("fatContent", data["nutrition"]["fatContent"])
        il.add_value("fiberContent", data["nutrition"]["fiberContent"])
        il.add_value("proteinContent", data["nutrition"]["proteinContent"])
        il.add_value("saturatedFatContent", data["nutrition"]["saturatedFatContent"])
        il.add_value(
            "unsaturatedFatContent", data["nutrition"]["unsaturatedFatContent"]
        )
        il.add_value("sodiumContent", data["nutrition"]["sodiumContent"])
        il.add_value("sugarContent", data["nutrition"]["sugarContent"])

        il.add_value("vitaminCContent", response.xpath(vitaminC_path).get())
        il.add_value("calciumContent", response.xpath(calcium_path).get())
        il.add_value("ironContent", response.xpath(iron_path).get())
        il.add_value("potassiumContent", response.xpath(potassium_path).get())

        # ingredient_scopes = response.xpath(ingredients_path)
        # ingredients = []
        # for i_scope in ingredient_scopes:
        #     components = i_scope.xpath("span/text()").getall()
        #     ingredients.append(" ".join(components))

        il.add_value("ingredients", data["recipeIngredient"])

        recipes.append(il.load_item())

        return recipes
