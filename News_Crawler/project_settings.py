crawl_limit = {
    "Nhân dân": 3,
    "Em đẹp": 0
}

default_crawl_limit = 5


def get_crawl_limit(domain):
    return default_crawl_limit if default_crawl_limit > 0 else crawl_limit.get(domain, 2)
