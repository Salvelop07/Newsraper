import scrapy
from scrapy import Request
from News_Crawler.spiders.NewsSpider import NewsSpider
from News_Crawler.items import Article
from News_Crawler import utils


class ThanhNienNewsSpider(NewsSpider):
    name = "ThanhNien"
    allowed_domains = ["thanhnien.vn"]
    base_url = "https://thanhnien.vn"

    url_category_list = [
        # ("https://game.thanhnien.vn", "tin-tuc", "Game"),
        # ("https://thanhnien.vn/doi-song", "am-thuc", "Ẩm thực")
    ]

    def start_requests(self):
        page_idx = 1
        for base_url, category_id, category_name in self.url_category_list:
            meta = {
                "base_url": base_url,
                "category": category_name,
                "category_url_fmt": base_url + "/" + category_id + "/trang-{}.html",
                "page_idx": page_idx,
            }
            category_url = meta["category_url_fmt"].format(meta["page_idx"])
            if meta["base_url"].startswith("https://thanhnien.vn"):
                parse_category = self.parse_category_type2
            else:
                parse_category = self.parse_category_type1
            yield Request(category_url, parse_category, meta=meta, errback=self.errback)

    def parse_category_type1(self, response):
        # Example: game.thanhnien.vn
        meta = response.meta

        # Navigate to article
        article_urls = response.css(".cate-content article>a::attr(href)").extract()

        self.logger.info("Parse url {}, Num Article urls : {}".format(response.url, len(article_urls)))
        for article_url in article_urls:
            article_url = meta["base_url"] + article_url
            if utils.is_valid_url(article_url):
                yield Request(article_url, self.parse_article_type1, meta={"category": meta["category"]}, errback=self.errback)

        # Navigate to next page
        if meta["page_idx"] < self.page_per_category_limit and len(article_urls) > 0:
            meta["page_idx"] += 1
            next_page = meta["category_url_fmt"].format(meta["page_idx"])
            yield Request(next_page, self.parse_category_type1, meta=meta, errback=self.errback)

    def parse_category_type2(self, response):
        # Example: thanhnien.vn/giao-duc
        meta = response.meta

        # Navigate to article
        article_urls = response.css(".cate-content .zone--timeline article>a::attr(href)").extract()

        self.logger.info("Parse url {}, Num Article urls : {}".format(response.url, len(article_urls)))
        for article_url in article_urls:
            article_url = meta["base_url"] + article_url
            if utils.is_valid_url(article_url):
                yield Request(article_url, self.parse_article_type2, meta={"category": meta["category"]}, errback=self.errback)

        # Navigate to next page
        if meta["page_idx"] < self.page_per_category_limit and len(article_urls) > 0:
            meta["page_idx"] += 1
            next_page = meta["category_url_fmt"].format(meta["page_idx"])
            yield Request(next_page, self.parse_category_type2, meta=meta, errback=self.errback)

    def parse_article_type1(self, response):
        # Example: game.thanhnien.vn

        url = response.url
        lang = self.lang
        title = response.css(".main-title::text").extract_first()
        category = response.meta["category"]
        intro = ' '.join(response.css(".details-content .sapo ::text").extract())
        content = ' '.join(response.xpath(
            "//div[@id='abody']//text()[not(ancestor::script)]").extract())
        time = response.css(".details-heading time ::text").extract_first()

        # Transform time to uniform format
        if time is not None:
            time = time.split()
            time = ' '.join([time[0], time[-1]])
            time = self.transform_time_fmt(time, src_fmt="%H:%M %d/%m/%Y")

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

    def parse_article_type2(self, response):
        # Example: thanhnien.vn/giao-duc

        url = response.url
        lang = self.lang
        title = response.css(".details__headline::text").extract_first()
        category = response.meta["category"]
        intro = ' '.join(response.css(".l-content .sapo ::text").extract())
        content = ' '.join(response.xpath(
            "//div[@id='abody']//text()[not(ancestor::script)]").extract())

        time = response.css(".details__meta time::text").extract_first()

        # Transform time to uniform format
        if time is not None:
            time = self.transform_time_fmt(time, src_fmt="%H:%M - %d/%m/%Y")

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
