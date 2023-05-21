from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.selector import Selector
from openrecipes.items import RecipeItem, RecipeItemLoader


class BiggirlssmallkitchenMixin(object):

    """
    Using this as a mixin lets us reuse the parse_item method more easily
    """

    # this is the source string we'll store in the DB to aggregate stuff
    # from a single source
    source = "biggirlssmallkitchen"

    def parse_item(self, response):
        # we use this to run XPath commands against the HTML in the response
        hxs = Selector(response)

        # this is the base XPath string for the element that contains the recipe
        # info
        base_path = (
            """//*[@id="container"]/*[@class="onepage"]/div[1]/div[@class="content"]"""
        )

        # the select() method will return a list of Selector objects.
        # On this site we will almost certainly either get back just one, if
        # any exist on the page
        recipes_scopes = hxs.select(base_path)

        # it's easier to define these XPath strings outside of the loop below
        name_path = '//h1[@class="title"]/text() | //*[@class="content"]/p[@style="text-align: center;"]/following-sibling::p[strong]/strong/text()'
        image_path = (
            '//*[@class="content"]/p[1]/img[contains(@class, "size-full")]/@src'
        )
        recipeYield_path = '//*[@class="content"]/p[@style="text-align: center;"]/following-sibling::p[em and strong]/em/text()'
        datePublished = (
            '//*[@class="phn-date"]/a[@rel="author"]/following-sibling::text()'
        )

        # This site contains Ingredients and Garnishes, both "lists" are inside a <p> and separated
        # using <br>s. Also, we skip the <p> containing "EVENT VENUE PARTY SIZE TYPE MENU" by
        # grabbing <p>s that do not have <strong>, <a>, or <img> child elements
        ingredients_path = (
            '//*[@class="content"]/p[not(strong or a or img) and br]/text()'
        )

        # init an empty list
        recipes = []

        # loop through our recipe scopes and extract the recipe data from each
        for r_scope in recipes_scopes:
            # make an empty RecipeItem
            il = RecipeItemLoader(item=RecipeItem())

            il.add_value("source", self.source)

            il.add_value("name", r_scope.select(name_path).extract())
            il.add_value("image", r_scope.select(image_path).extract())
            il.add_value("url", response.url)

            il.add_value("recipeYield", r_scope.select(recipeYield_path).extract())

            # date returns something like this: "ON SATURDAY NOV 28TH, 2009 |"
            date = r_scope.select(datePublished).extract()
            if len(date) > 0:
                date = date[0].replace("on", "", 1).replace("|", "").strip()
                il.add_value("datePublished", date)

            il.add_value("ingredients", r_scope.select(ingredients_path).extract())

            # stick this RecipeItem in the array of recipes we will return
            recipes.append(il.load_item())

        # more processing is done by the openrecipes.pipelines. Look at that
        # file to see transforms that are applied to each RecipeItem
        return recipes


class BiggirlssmallkitchencrawlSpider(CrawlSpider, BiggirlssmallkitchenMixin):
    # this is the name you'll use to run this spider from the CLI
    name = "biggirlssmallkitchen.com"

    # URLs not under this set of domains will be ignored
    allowed_domains = ["biggirlssmallkitchen.com"]

    # the set of URLs the crawler with start with. We're starting on the first
    # page of the site's recipe archive
    start_urls = [
        "http://biggirlssmallkitchen.com/recipe-index",
    ]

    # a tuple of Rules that are used to extract links from the HTML page
    rules = (
        # this rule has no callback, so these links will be followed and mined
        # for more URLs. This lets us page through the recipe archives
        Rule(LinkExtractor(allow=("/type/.+"))),
        Rule(LinkExtractor(allow=("/course/.+"))),
        Rule(LinkExtractor(allow=("/for_when_youre_low_on/.+"))),
        Rule(LinkExtractor(allow=("/occasion/.+"))),
        Rule(LinkExtractor(allow=("/holiday/.+"))),
        Rule(LinkExtractor(allow=("/dietary_restriction/.+"))),
        Rule(LinkExtractor(allow=("/cooking_method/.+"))),
        Rule(LinkExtractor(allow=("/cuisine/.+"))),
        Rule(LinkExtractor(allow=("/main_ingredient/.+"))),
        # this rule is for recipe posts themselves. The callback argument will
        # process the HTML on the page, extract the recipe information, and
        # return a RecipeItem object
        Rule(LinkExtractor(allow=("/\d{4}/\d{2}/.+")), callback="parse_item"),
    )
