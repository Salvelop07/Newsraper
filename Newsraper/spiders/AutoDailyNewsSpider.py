import scrapy
from scrapy import Request
from Newsraper.spiders.NewsSpider import NewsSpider
from Newsraper.items import Article
from Newsraper import utils


class AutoDailyNewsSpider(NewsSpider):
    name = "AutoDaily"
    allowed_domains = ["autodaily.vn"]
    base_url = "https://autodaily.vn"

    url_category_list = [
        ("https://autodaily.vn/chuyen-muc/xe-moi/xe-may/14", "Xe máy"),
        ("https://autodaily.vn/chuyen-muc/xe-moi/o-to/13", "Ô tô"),
        # ("", ""),
    ]

    def __init__(self):
        super().__init__(name=self.name)

    def start_requests(self):
        page_idx = 1
        for category_url, category in self.url_category_list:
            meta = {
                "category": category,
                "category_url_fmt": category_url + "/page/{}",
                "page_idx": page_idx
            }
            category_url = meta["category_url_fmt"].format(meta["page_idx"])
            yield Request(category_url, self.parse_category, meta=meta, errback=self.errback)

    def parse_category(self, response):
        meta = dict(response.meta)

        # Navigate to article
        article_urls = response.css(
            "div.main-content .late-news-lst li .late-news-tit a::attr(href)").extract()

        self.logger.info("Parse url {}, Num Article urls : {}".format(
            response.url, len(article_urls)))
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
        category = response.meta["category"]
        title = response.css(".article-title ::text").extract_first()
        intro = ' '.join(response.css(".article-detail-hd>p ::text").extract())
        content = ' '.join(response.xpath("//div[@class='article-detail']//"
                                          "p[not(ancestor::div[@class='article-detail-hd'])]//text()").extract()[:-2])
        time = response.css(".datetime span::text").extract()

        # Transform time to uniform format
        if time is not None:
            time = "".join(time)
            time = self.transform_time_fmt(time, src_fmt="%H:%M %d/%m/%Y")

        self.article_scraped_count += 1
        self.print_num_scraped_items(every=20)

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
