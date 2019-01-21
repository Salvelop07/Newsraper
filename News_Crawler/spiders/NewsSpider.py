import scrapy
from News_Crawler import utils
from News_Crawler.crawl_proxy import ProxyManager
import requests
import random
import time


class NewsSpider(scrapy.Spider):
    def __init__(self, name=None, **kwargs):
        super(NewsSpider, self).__init__(name=name, **kwargs)
        self.page_per_category_limit = utils.get_crawl_limit_setting(name)
        self.article_scraped_count = 0
        self.lang = "vi"
        self.pm = ProxyManager(proxies_path="./News_Crawler/Proxy/proxy_list.txt", update=True)

    def parse(self, response):
        raise NotImplementedError()

    def parse_category(self, response):
        raise NotImplementedError()

    def parse_article(self, response):
        raise NotImplementedError()

    def transform_time_fmt(self, time_str, src_fmt):
        try:
            return utils.transform_time_fmt(time_str, src_fmt=src_fmt)
        except:
            self.logger.debug("Exception when parse time_str : ", time_str)
            return ""

    def print_num_scraped_items(self, every=50):
        if self.article_scraped_count % every == 0:
            self.logger.info("\nSpider {}: Crawl {} items\n".format(self.name, self.article_scraped_count))

    def get_response(self, url, timeout=1.5):

        x = random.randint(1, 11)
        if x <= 5:
            print("Sleeping ... to send direct request from my ip ! ...")
            time_sleep = random.random() * 3 + 0.2
            time.sleep(time_sleep)
            res = requests.get(url)
        else:
            res = self.pm.get_response(url, timeout=timeout)
            if res is None:
                res = requests.get(url)
                print("Send direct request from my ip !")

        return res
