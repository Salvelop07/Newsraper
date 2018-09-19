import scrapy
from scrapy import Request
from News_Crawler.spiders.NewsSpider import NewsSpider
from News_Crawler.items import Article
from News_Crawler import utils


class RongBayNewsSpider(NewsSpider):
    name = "RongBay"
    allowed_domains = ["rongbay.com"]
    # base_url = "https://rongbay.com"

    url_category_list = [
        ("https://rongbay.com/Ha-Noi/Dien-lanh-Dien-may-Gia-dung-c280", "QC - Điện lạnh, điện máy gia dụng"),
        # ("https://rongbay.com/Ha-Noi/Cho-Sim-c278.html", "QC - Sim"),
        # ("https://rongbay.com/Ha-Noi/Do-noi-that-c291.html", "QC - Đồ nội thất"),
        # ("https://rongbay.com/Ha-Noi/Thoi-trang-c304.html", "QC - Thời trang"),
        # ("https://rongbay.com/Ha-Noi/My-pham-nu-c298.html", "QC - Mỹ phẩm"),
    ]

    def start_requests(self):
        page_idx = 1
        for category_url, category in self.url_category_list:
            meta = {
                "category": category,
                "category_url_fmt": category_url + "-trang{}.html",
                "page_idx": page_idx
            }
            category_url = meta["category_url_fmt"].format(meta["page_idx"])
            yield Request(category_url, self.parse_category, meta=meta, errback=self.errback)

    def parse_category(self, response):
        meta = dict(response.meta)

        # Navigate to article
        article_urls = response.css(".NewsList a.newsTitle::attr(href)").extract()

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

        url = response.url
        lang = self.lang
        title = response.css(".header .title::text").extract_first()
        category = response.meta["category"]
        intro = ' '
        content = ' '.join(response.xpath("//div[@id='NewsContent']//text()").extract())
        time = response.css(
            ".header .info_item_popup .note_gera:first-child span::text").extract_first()


        # Transform time to uniform format
        if time is not None:
            time = self.transform_time_fmt(time, src_fmt="%d/%m/%Y")

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
