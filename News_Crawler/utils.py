import os, time, json, sys
import pandas as pd
from datetime import datetime
import News_Crawler.project_settings as settings
from News_Crawler.project_settings import DEFAULT_TIME_FORMAT


def get_time_str(time=datetime.now(), fmt=DEFAULT_TIME_FORMAT):
    return time.strftime(fmt)


def get_time_obj(time_str, fmt=DEFAULT_TIME_FORMAT):
    return datetime.strptime(time_str, fmt)


def transform_time_fmt(time_str, src_fmt, dst_fmt=DEFAULT_TIME_FORMAT):
    time_obj = get_time_obj(time_str, src_fmt)
    return get_time_str(time_obj, dst_fmt)


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


def save_csv(data, path, fields=None):
    if fields is None or len(fields) == 0:
        df = pd.DataFrame(data)
    else:
        df = pd.DataFrame(data, columns=fields)
    df.to_csv(path, index=False)


def save_list(data, path):
    dir = path[:path.rfind("/")]
    mkdirs(dir)

    with open(path, 'w') as f:
        f.write("\n".join(data))
    print("Save list data (size = {}) to {} done".format(len(data), path))


def get_crawl_limit_setting(domain):
    crawl_limit = settings.CRAWL_LIMIT
    default = crawl_limit.get("default_crawl_limit")
    limit = crawl_limit.get(domain, 5) if default is None else default
    if limit < 0:
        limit = sys.maxsize

    return limit


def get_export_fields_setting():
    return settings.EXPORT_FIELDS


def get_export_format_setting():
    return settings.EXPORT_FORMAT


# def get_file_chunk_size():
#     return settings.file_chunk_size


# if __name__ == "__main__":
    # domain = "Nhân dân"
    # crawl_limit = get_crawl_limit(domain)

    # save_path = "../Data/Temp/01/tmp.json"
    # save_json([], save_path)
