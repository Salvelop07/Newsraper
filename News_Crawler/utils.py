import os, time
from datetime import datetime


def get_time_str(time=datetime.now(), fmt="%d-%m-%Y_%H%M%S"):
    return time.strftime(fmt)


def get_time_obj(time_str, fmt="%d-%m-%Y_%H%M%S"):
    return datetime.strptime(time_str, fmt)


def mkdirs(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)

