import scrapy
from scrapy import Request
from News_Crawler.spiders.NewsSpider import NewsSpider
from News_Crawler.items import Article
from News_Crawler import utils


class TapChiHangKhongNewsSpider(NewsSpider):
    name = "TapChiHangKhong"
    allowed_domains = ["tapchihangkhong.com"]

    url_category_list = [
        # ("https://www.tapchihangkhong.com/quoc-noi", "Hàng không"),
        # ("https://www.tapchihangkhong.com/quoc-te", "Hàng không"),
    ]

    def __init__(self):
        super().__init__(name=self.name)

    def start_requests(self):
        page_idx = 1
        for category_url, category in self.url_category_list:
            meta = {
                "category": category,
                "category_url_fmt": category_url + "/page/{}/",
                "page_idx": page_idx
            }
            category_url = meta["category_url_fmt"].format(meta["page_idx"])
            yield Request(category_url, self.parse_category, meta=meta, errback=self.errback)

    def parse_category(self, response):
        meta = dict(response.meta)

        # Navigate to article
        article_urls = response.css(
            "#main-content article.item-list .post-box-title a::attr(href)").extract()

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
        article_div = response.css("#main-content article")

        url = response.url
        lang = self.lang
        title = article_div.css(".post-title ::text").extract_first()
        category = response.meta["category"]
        intro = ''
        content = ' '.join(article_div.xpath(
            ".//div[@class='entry']//text()[not(ancestor::script)]").extract())
        time = article_div.css(".updated ::text").extract_first()

        # Transform time to uniform format
        if time is not None:
            time = self.transform_time_fmt(time, src_fmt="%Y-%m-%d")

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
