import scrapy
from scrapy import Request
from News_Crawler.spiders.NewsSpider import NewsSpider
from News_Crawler.items import Article


class VNExpressNewsSpider(NewsSpider):
    name = "VNExpress"
    allowed_domains = ["vnexpress.net"]
    # start_urls = ["https://vnexpress.net"]

    url_category_list = [
        # ("https://vnexpress.net/tin-tuc/oto-xe-may", "Xe"),
        # ("https://suckhoe.vnexpress.net/tin-tuc/dinh-duong", "Dinh dưỡng"),
        ("https://vnexpress.net/tin-tuc/thoi-su/giao-thong", "Giao thông"),
        # ("https://suckhoe.vnexpress.net/tin-tuc/suc-khoe", "Sức khỏe"),

        # ("https://kinhdoanh.vnexpress.net/tin-tuc/bat-dong-san", "Bất động sản"),
        # ("https://kinhdoanh.vnexpress.net/tin-tuc/chung-khoan", "Chứng khoán"),
        # ("https://giaitri.vnexpress.net/tin-tuc/lam-dep", "Làm đẹp"),
        # ("https://giaitri.vnexpress.net/tin-tuc/thoi-trang", "Thời trang"),
        # ("https://thethao.vnexpress.net", "Thể thao"),
        # ("https://vnexpress.net/tin-tuc/giao-duc", "Giáo dục"),
        # ("https://doisong.vnexpress.net/tin-tuc/nha", "Nhà"),
        # ("https://dulich.vnexpress.net", "Du lịch")
        # ("https://sohoa.vnexpress.net/tin-tuc/dien-tu-gia-dung", "Điện tử gia dụng")
    ]

    def start_requests(self):
        page_idx = 1
        for category_url, category in self.url_category_list:
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
            yield Request(article_url, self.parse_article, meta={"category": meta["category"]})

        # Navigate to next page
        if meta["page_idx"] < self.page_per_category_limit and len(article_urls) > 0:
            meta["page_idx"] += 1
            next_page = meta["category_url_fmt"].format(meta["page_idx"])
            yield Request(next_page, self.parse_category, meta=meta)

    def parse_article(self, response):
        section = response.css("section.sidebar_1")

        url = response.url
        lang = self.lang
        title = section.css(".title_news_detail::text").extract_first()
        category = response.meta["category"]
        intro = section.css(".description::text").extract_first()
        content = section.css("article.content_detail ::text").extract()
        content = ' '.join(content)
        time = section.css("span.time::text").extract_first()

        # Transform time to uniform format
        if time is not None:
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
