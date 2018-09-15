import scrapy
from scrapy import Request
from News_Crawler.spiders.NewsSpider import NewsSpider
from News_Crawler.items import Article
from News_Crawler import utils
import json


class QuangCao24hSpider(NewsSpider):
    name = "QuangCao24h"
    allowed_domains = ["quangcao24h.com.vn"]
    base_url = "http://www.quangcao24h.com.vn"

    category_list = [
        ("Địa điểm kinh doanh", 48),
        # ("Đồ dùng nội ngoại thất", 14)
    ]

    def start_requests(self):
        page_idx = 1
        for category, category_id in self.category_list:
            meta = {
                "category": category,
                "category_id": category_id,
                "category_url_fmt": "http://www.quangcao24h.com.vn/index_ajax.php?module_name=product_detail&action=viewlistAjax&category_id={}&provinces_id=&limit=&page={}",
                "page_idx": page_idx
            }
            category_url = meta["category_url_fmt"].format(meta["category_id"], meta["page_idx"])
            yield Request(category_url, self.parse_category, meta=meta, errback=self.errback)

    def parse_category(self, response):
        meta = response.meta

        articles_urls = response.css("li>div> a::attr(href)").extract()

        # Navigate to article
        self.logger.info("Parse url {}, Num Article urls : {}".format(response.url, len(articles_urls)))
        for article_url in articles_urls:
            article_url = self.base_url + article_url

            if utils.is_valid_url(article_url):
                yield Request(article_url, self.parse_article, meta=meta, errback=self.errback)

        # Navigate to next page
        if meta["page_idx"] < self.page_per_category_limit and len(articles_urls) > 0:
            meta["page_idx"] += 1
            next_page = meta["category_url_fmt"].format(meta["category_id"], meta["page_idx"])
            yield Request(next_page, self.parse_category, meta=meta, errback=self.errback)

    def parse_article(self, response):
        meta = response.meta

        url = response.url
        lang = self.lang
        title = response.css(".postDetail>.detail_product .product_name::text").extract_first()
        category = meta["category"]
        intro = ""
        content = ' '.join(response.css(".postDetail .full_description_inside ::text").extract())
        time = ""

        self.article_scraped_count += 1
        if self.article_scraped_count % 100 == 0:
            self.logger.info("Spider {}: Crawl {} items".format(self.name, self.article_scraped_count))
        
        yield Article(
            url=url,
            lang=lang,
            title=title,
            category=category,
            intro=intro,
            content=content,
            time=time
        )

    def errback(self, failure):
        self.logger.error("Error when send requests : ", failure.request)
