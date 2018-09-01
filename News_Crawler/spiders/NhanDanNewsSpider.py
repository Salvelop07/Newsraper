import scrapy
from scrapy import Request
from News_Crawler.spiders.NewsSpider import NewsSpider
from News_Crawler.items import Article


class NhanDanNewsSpider(NewsSpider):
    name = "Nhân dân"
    allowed_domains = ["nhandan.com.vn"]
    start_urls = ["http://www.nhandan.com.vn"]

    def parse(self, response):
        for a in response.css("div#topnav li.tn_menu a"):
            category_url = a.xpath("@href").extract_first()
            category_url_fmt = response.urljoin(category_url) + "?limitstart={}"

            category = a.xpath("./span/text()").extract_first()
            limit_start = 0
            meta = {
                "category": category,
                "category_url_fmt": category_url_fmt,
                "limit_start": limit_start,
                "page_idx": 0
            }

            category_url = category_url_fmt.format(limit_start)
            yield Request(category_url, self.parse_category, meta=meta)

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
        title = table.css("div.ndtitle ::text").extract()
        category = response.meta["category"]
        intro = table.css("div.ndcontent.ndb p ::text").extract()
        content = table.css("div[class=ndcontent] p ::text").extract()
        time = table.css("div.icon_date_top>div.pull-left::text").extract()

        self.article_scraped_count += 1
        yield Article(
            url=url,
            lang=lang,
            title=' '.join(title),
            category=' '.join(category),
            intro=' '.join(intro),
            content=' '.join(content),
            time=time
        )
