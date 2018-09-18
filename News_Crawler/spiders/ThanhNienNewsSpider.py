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
        ("")
    ]

    def start_requests(self):
        page_idx = 1
        for category_url, category, allowed_prefix_url in self.url_category_list:
            meta = {
                "category": category,
                "category_url_fmt": category_url + "/trang-{}.html",
                "page_idx": page_idx,
                "allowed_prefix_url": allowed_prefix_url
            }
            category_url = meta["category_url_fmt"].format(meta["page_idx"])
            yield Request(category_url, self.parse_category, meta=meta, errback=self.errback)

    def parse_category(self, response):
        meta = response.meta

        # Navigate to article
        article_urls = response.css(".cate-content article>a::attr(href)").extract()

        self.logger.info("Parse url {}, Num Article urls : {}".format(response.url, len(article_urls)))
        for article_url in article_urls:
            allowed_prefix_url = meta["allowed_prefix_url"]
            if len(allowed_prefix_url) == 0 or article_url.startswith(allowed_prefix_url):
                article_url = self.base_url + article_url
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
        title = response.css(".details__headline::text").extract_first()
        if title is None or len(title) == 0:
            title = response.css(".main-title::text").extract_first()

        # Must check code after this line 


        category = response.meta["category"]
        intro = section.css(".description::text").extract_first()
        content = section.css("article.content_detail ::text").extract()
        content = ' '.join(content)
        time = section.css("span.time::text").extract()

        # Transform time to uniform format
        if time is not None:
            time = ", ".join(time)
            time = time.split(", ")
            time[-1] = time[-1][:5]
            time = '_'.join(time[1:])
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
