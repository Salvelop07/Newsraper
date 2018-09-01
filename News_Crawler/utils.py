import os, time, json
from datetime import datetime
import News_Crawler.project_settings as settings


def get_time_str(time=datetime.now(), fmt="%d-%m-%Y_%H-%M-%S"):
    return time.strftime(fmt)


def get_time_obj(time_str, fmt="%d-%m-%Y_%H%M%S"):
    return datetime.strptime(time_str, fmt)


def mkdirs(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def load_json(path):
    with open(path, 'r') as f:
        data = json.load(f)
    return data


def save_json(data, path):
    dir = path[:path.rfind("/")]
    mkdirs(dir)

    with open(path, 'w') as f:
        json.dump(data, f, ensure_ascii=False)
    print("Save json data (size = {}) to {} done".format(len(data), path))


def get_crawl_limit(domain):
    crawl_limit = settings.crawl_limit
    default = crawl_limit.get("default_crawl_limit")
    return crawl_limit.get(domain, 5) if default is None else default


def get_file_chunk_size():
    return settings.file_chunk_size


if __name__ == "__main__":
    # domain = "Nhân dân"
    # crawl_limit = get_crawl_limit(domain)

    save_path = "../Data/Temp/01/tmp.json"
    save_json([], save_path)
