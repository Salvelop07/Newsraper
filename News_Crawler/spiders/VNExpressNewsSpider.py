import scrapy
from scrapy import Request
from News_Crawler.spiders.NewsSpider import NewsSpider
from News_Crawler.items import Article


class VNExpressNewsSpider(NewsSpider):
    name = "VNExpress"
    allowed_domains = ["vnexpress.net"]
    # start_urls = ["https://vnexpress.net"]
    start_urls = ["https://vnexpress.net/tin-tuc/oto-xe-may"]
    categories = ["XE"]

    def start_requests(self):
        page_idx = 1
        for category_url, category in zip(self.start_urls, self.categories):
            meta = {
                "category": category,
                "category_url_fmt": category_url + "/page/{}.html",
                "page_idx": page_idx
            }
            category_url = meta["category_url_fmt"].format(meta["page_idx"])
            yield Request(category_url, self.parse_category, meta=meta)

    def parse_category(self, response):
        meta = response.meta

        # Navigate to article
        article_urls = response.css(
            "section.featured .title_news a:first-child::attr(href)").extract()
        article_urls.extend(response.css(
            "section.sidebar_1 .title_news a:first-child::attr(href)").extract())
        article_urls = list(set(article_urls))

        # Dont check code after this line ...

        for article_url in article_urls:
            article_url = response.urljoin(article_url)
            yield Request(article_url, self.parse_article, meta={"category": meta["category"]})

        # Navigate to next page
        if meta["page_idx"] < self.page_per_category_limit and len(article_urls) > 0:
            meta["page_idx"] += 1
            next_page = meta["category_url_fmt"].format(meta["page_idx"])
            yield Request(next_page, self.parse_category, meta=meta)

    def parse_article(self, response):
        table = response.css("div.media table")

        url = response.url
        lang = self.lang
        title = table.css("div.ndtitle ::text").extract()
        category = response.meta["category"]
        intro = table.css("div.ndcontent.ndb p ::text").extract()
        content = table.css("div[class=ndcontent] p ::text").extract()
        time = table.css("div.icon_date_top>div.pull-left::text").extract_first()

        # Transform time to uniform format
        time = '_'.join(time.split(", ")[1:])
        time = self.transform_time_fmt(time, src_fmt="%d/%m/%Y_%H:%M:%S")

        self.article_scraped_count += 1
        if self.article_scraped_count % 100 == 0:
            self.log("Spider {}: Crawl {} items".format(self.name, self.article_scraped_count))
        
        yield Article(
            url=url,
            lang=lang,
            title=' '.join(title),
            category=category,
            intro=' '.join(intro),
            content=' '.join(content),
            time=time
        )
