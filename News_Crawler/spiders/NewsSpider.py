import scrapy
from News_Crawler.project_settings import get_crawl_limit


class NewsSpider(scrapy.Spider):
    def __init__(self, name="News", **kwargs):
        super(NewsSpider, self).__init__(name=name, **kwargs)
        self.article_limit = get_crawl_limit(name)
        self.article_scraped_count = 0
        self.lang = "vi"

    def parse(self, response):
        raise NotImplementedError()

    def parse_category(self, response):
        raise NotImplementedError()

    def parse_article(self, response):
        raise NotImplementedError()

