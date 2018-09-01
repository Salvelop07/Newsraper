import scrapy
from News_Crawler.utils import get_crawl_limit


class NewsSpider(scrapy.Spider):
    def __init__(self, name=None, **kwargs):
        super(NewsSpider, self).__init__(name=name, **kwargs)
        self.page_per_category_limit = get_crawl_limit(name)
        self.article_scraped_count = 0
        self.lang = "vi"

    def parse(self, response):
        raise NotImplementedError()

    def parse_category(self, response):
        raise NotImplementedError()

    def parse_article(self, response):
        raise NotImplementedError()

