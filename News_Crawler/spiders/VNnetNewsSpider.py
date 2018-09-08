import scrapy
from scrapy import Request
from News_Crawler.spiders.NewsSpider import NewsSpider
from News_Crawler.items import Article
from News_Crawler import utils
import json


class VNnetNewsSpider(NewsSpider):
    name = "VNnet"
    allowed_domains = ["vietnamnet.vn"]

    category_list = [
        # ("Giáo dục", "giao-duc"),
        # ("Giao thông", "thoi-su-an-toan-giao-thong"),
        # ("Thời trang", "giai-tri-thoi-trang"),
        # ("Bảo hiểm", "thoi-su-bhxh-bhyt"),
        # ("Tài chính", "kinh-doanh-tai-chinh"),
        ("Mẹ và bé", "doi-song-me-va-be"),
        # ("Du lịch", "doi-song-du-lich"),
        # ("Ẩm thực", "doi-song-am-thuc"),
        # ("Pháp luật", "phap-luat")
    ]

    def start_requests(self):
        page_idx = 1
        for category, c_query in self.category_list:
            meta = {
                "category": category,
                "c_query": c_query,
                "category_url_fmt": "http://vietnamnet.vn/jsx/loadmore/?domain=desktop&c={}&p={}&s=25&a=6",
                "page_idx": page_idx
            }
            category_url = meta["category_url_fmt"].format(meta["c_query"], meta["page_idx"])
            yield Request(category_url, self.parse_category, meta=meta, errback=self.errback)

    def parse_category(self, response):
        meta = response.meta

        prefix_str = "retvar ="
        data = response.css("::text").extract_first()
        data = json.loads(data[len(prefix_str):])

        # Navigate to article
        self.logger.info("Parse url {}, Num Article urls : {}".format(response.url, len(data)))
        for article in data:
            time = '_'.join([article["publishdate"], article["publishtime"]])
            time = self.transform_time_fmt(time, src_fmt="%d/%m/%Y_%H:%M")
            article_info = {
                "category": meta["category"],
                "title": article["title"],
                "intro": article["lead"],
                "time": time
            }
            article_url = article["link"]
            if utils.is_valid_url(article_url):
                yield Request(article_url, self.parse_article, meta=article_info, errback=self.errback)

        # Navigate to next page
        if meta["page_idx"] < self.page_per_category_limit and len(data) > 0:
            meta["page_idx"] += 1
            next_page = meta["category_url_fmt"].format(meta["c_query"], meta["page_idx"])
            yield Request(next_page, self.parse_category, meta=meta, errback=self.errback)

    def parse_article(self, response):
        meta = response.meta
        section = response.css("section.sidebar_1")

        url = response.url
        lang = self.lang
        title = meta["title"]
        category = meta["category"]
        intro = meta["intro"]
        content = ' '.join(response.xpath("//div[@id='ArticleContent']//text()").extract())
        time = meta["time"]

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
