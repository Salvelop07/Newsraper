import scrapy
from scrapy import Request
from News_Crawler.spiders.NewsSpider import NewsSpider
from News_Crawler.items import Article
from News_Crawler import utils


class DanTriNewsSpider(NewsSpider):
    name = "DanTri"
    allowed_domains = ["dantri.com.vn"]
    base_url = "https://dantri.com.vn"

    url_category_list = [
        # ("https://dantri.com.vn/giai-tri/thoi-trang", "Thời trang"),
        # ("https://dantri.com.vn/the-thao", "Thể thao"),
        # ("https://dantri.com.vn/xa-hoi/giao-thong", "Giao thông"),
        # ("https://dantri.com.vn/giao-duc-khuyen-hoc", "Giáo dục"),
        # ("https://dantri.com.vn/kinh-doanh/nha-dat", "Bất động sản"),
        # ("https://dantri.com.vn/kinh-doanh/tai-chinh-dau-tu", "Tài chính"),
        # ("https://dantri.com.vn/phap-luat", "Pháp luật"),
        # ("https://dantri.com.vn/suc-khoe/lam-dep", "Làm đẹp"),
        # ("https://dulich.dantri.com.vn/du-lich/vong-quay-du-lich", "")
    ]

    def __init__(self):
        super().__init__(name=self.name)

    def start_requests(self):
        page_idx = 1
        for category_url, category in self.url_category_list:
            meta = {
                "category": category,
                "category_url_fmt": category_url + "/trang-{}.htm",
                "page_idx": page_idx
            }
            category_url = meta["category_url_fmt"].format(meta["page_idx"])
            yield Request(category_url, self.parse_category, meta=meta, errback=self.errback)

    def parse_category(self, response):
        meta = dict(response.meta)

        # Navigate to article
        article_urls = response.css("div#listcheckepl > div > a::attr(href)").extract()

        self.logger.info("Parse url {}, Num Article urls : {}".format(response.url, len(article_urls)))
        for article_url in article_urls:
            article_url = self.base_url + article_url
            if utils.is_valid_url(article_url):
                yield Request(article_url, self.parse_article, meta={"category": meta["category"]}, errback=self.errback)

        # Navigate to next page
        if meta["page_idx"] < self.page_per_category_limit and len(article_urls) > 0:
            meta["page_idx"] += 1
            next_page = meta["category_url_fmt"].format(meta["page_idx"])
            yield Request(next_page, self.parse_category, meta=meta, errback=self.errback)

    def parse_article(self, response):
        content_div = response.xpath("//div[@id='ctl00_IDContent_ctl00_divContent']")

        url = response.url
        lang = self.lang
        title = content_div.css("h1.fon31.mgb15::text").extract_first()
        category = response.meta["category"]
        intro = ' '.join(content_div.css("h2.fon33::text").extract())
        content = ' '.join(content_div.css("#divNewsContent ::text").extract())
        time = content_div.css("div.box26>span::text").extract_first()

        # Transform time to uniform format
        if time is not None:
            time = time[time.find(", ") + 2:]
            time = '_'.join(time.split(" - "))
            time = self.transform_time_fmt(time, src_fmt="%d/%m/%Y_%H:%M")

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
