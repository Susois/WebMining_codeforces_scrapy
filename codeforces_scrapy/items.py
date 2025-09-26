# ...existing code...
import scrapy


class CodeforcesProblem(scrapy.Item):
    contest_id = scrapy.Field()
    index = scrapy.Field()
    problem_id = scrapy.Field()
    title = scrapy.Field()
    tags = scrapy.Field()
    rating = scrapy.Field()
    solved_count = scrapy.Field()
    url = scrapy.Field()
# ...existing code...