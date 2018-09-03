import scrapy
from scrapy import Request
from News_Crawler.spiders.NewsSpider import NewsSpider
from News_Crawler.items import Article


class NhanDanNewsSpider(NewsSpider):
    name = "NhanDan"
    allowed_domains = ["nhandan.com.vn"]
    # start_urls = ["http://www.nhandan.com.vn"]
    # start_urls = ["http://www.nhandan.com.vn/congnghe"]
    # categories = ["CÔNG NGHỆ"]
    url_category_list = [
        # ("http://www.nhandan.com.vn/suckhoe", "Sức khỏe")
        # ("http://www.nhandan.com.vn/phapluat", "Pháp luật"),

        ("http://www.nhandan.com.vn/vanhoa/du_lich", "Du lịch"),
        
        # ("http://www.nhandan.com.vn/xahoi/bhxh-va-cuoc-song", "BHXH và cuộc sống"),
        # ("http://www.nhandan.com.vn/xahoi/giao-thong", "Giao thông"),
        # ("http://www.nhandan.com.vn/congnghe/vien-thong", "Viễn thông"),
        # ("http://www.nhandan.com.vn/thethao", "Thể thao")
    ]

    def start_requests(self):
        limit_start = 0
        for category_url, category in self.url_category_list:
            meta = {
                "category": category,
                "category_url_fmt": category_url + "?limitstart={}",
                "limit_start": limit_start,
                "page_idx": 0
            }
            category_url = meta["category_url_fmt"].format(meta["limit_start"])
            yield Request(category_url, self.parse_category, meta=meta)

    # def parse(self, response):
    #     for a in response.css("div#topnav li.tn_menu a"):
    #         category_url = a.xpath("@href").extract_first()
    #         category_url_fmt = response.urljoin(category_url) + "?limitstart={}"

    #         category = a.xpath("./span/text()").extract_first()
    #         limit_start = 0
    #         meta = {
    #             "category": category,
    #             "category_url_fmt": category_url_fmt,
    #             "limit_start": limit_start,
    #             "page_idx": 0
    #         }

    #         category_url = category_url_fmt.format(limit_start)
    #         yield Request(category_url, self.parse_category, meta=meta)

    def parse_category(self, response):
        meta = response.meta

        # Navigate to article
        article_urls = response.css(".media-body a.pull-left::attr(href)").extract()
        for article_url in article_urls:
            article_url = response.urljoin(article_url)
            yield Request(article_url, self.parse_article, meta={"category": meta["category"]})

        # Navigate to next page
        if meta["page_idx"] + 1 < self.page_per_category_limit and len(article_urls) > 0:
            meta["limit_start"] += 15
            meta["page_idx"] += 1
            next_page = meta["category_url_fmt"].format(meta["limit_start"])
            yield Request(next_page, self.parse_category, meta=meta)

    def parse_article(self, response):
        table = response.css("div.media table")

        url = response.url
        lang = self.lang
        title = table.css("div.ndtitle ::text").extract_first()
        category = response.meta["category"]
        intro = table.css("div.ndcontent.ndb p ::text").extract_first()
        content = table.css("div[class=ndcontent] ::text").extract()
        content = ' '.join(content)
        time = table.css("div.icon_date_top>div.pull-left::text").extract_first()

        # Transform time to uniform format
        if time is not None:
            time = '_'.join(time.split(", ")[1:])
            time = self.transform_time_fmt(time, src_fmt="%d/%m/%Y_%H:%M:%S")

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
