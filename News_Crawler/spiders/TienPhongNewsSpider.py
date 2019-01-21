import scrapy
from scrapy import Request
from News_Crawler.spiders.NewsSpider import NewsSpider
from News_Crawler.items import Article
from News_Crawler import utils


class TienPhongNewsSpider(NewsSpider):
    name = "TienPhong"
    allowed_domains = ["tienphong.vn"]

    url_category_list = [
        # ("https://www.tienphong.vn/kinh-te-thi-truong/", "Tài chính"),
        # ("https://www.tienphong.vn/du-lich/", "Du lịch"),
        # ("https://www.tienphong.vn/nha-dep-phong-thuy/", "Nhà đẹp"),
        # ("https://www.tienphong.vn/lam-dep/", "Thời trang"),        
        # ("https://www.tienphong.vn/kinh-te-chung-khoan/", "Chứng khoán"),
        # ("https://www.tienphong.vn/thi-truong/", "Bất động sản"),
        # ("https://www.tienphong.vn/phap-luat/", "Pháp luật"),
        # ("https://www.tienphong.vn/giao-duc/", "Giáo dục"),
        # ("https://www.tienphong.vn/the-thao/", "Thể thao"),
        # ("https://www.tienphong.vn/xe/", "Xe"),
        ("https://www.tienphong.vn/cong-nghe-khoa-hoc/", "Công nghệ")
    ]

    def __init__(self):
        super().__init__(name=self.name)

    def start_requests(self):
        page_idx = 1
        for category_url, category in self.url_category_list:
            meta = {
                "category": category,
                "category_url_fmt": category_url + "?trang={}",
                "page_idx": page_idx
            }
            category_url = meta["category_url_fmt"].format(meta["page_idx"])
            yield Request(category_url, self.parse_category, meta=meta, errback=self.errback)

    def parse_category(self, response):
        meta = response.meta

        # Navigate to article
        article_urls = response.css("div.cate-list-news div.other-news article>a::attr(href)").extract()

        self.logger.info("Parse url {}, Num Article urls : {}".format(response.url, len(article_urls)))
        for article_url in article_urls:
            if utils.is_valid_url(article_url):
                yield Request(article_url, self.parse_article, meta={"category": meta["category"]}, errback=self.errback)

        # Navigate to next page
        if meta["page_idx"] < self.page_per_category_limit and len(article_urls) > 0:
            meta["page_idx"] += 1
            next_page = meta["category_url_fmt"].format(meta["page_idx"])
            yield Request(next_page, self.parse_category, meta=meta, errback=self.errback)

    def parse_article(self, response):
        article_div = response.css("#main-article-body article.main-article")

        url = response.url
        lang = self.lang
        title = article_div.css("#headline ::text").extract_first()
        category = response.meta["category"]
        intro = article_div.css(".cms-desc ::text").extract_first()
        content = ' '.join(article_div.css("#article-body ::text").extract())
        time = article_div.css("#article-meta .byline-dateline time::text").extract_first()

        # Transform time to uniform format
        if time is not None:
            time = self.transform_time_fmt(time, src_fmt="%d/%m/%Y %H:%M")

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
