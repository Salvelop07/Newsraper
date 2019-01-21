from lxml import html
import requests
import os
import pandas as pd
import random
import json


def mkdirs(dir):
    if not os.path.exists(dir):
        os.makedirs(dir)


def save_csv(df, path, fields=None):
    dir = path[:path.rfind("/")]
    mkdirs(dir)
    if fields is None or len(fields) == 0:
        columns = df.columns
    else:
        columns = fields
    df.to_csv(path, index=False, columns=columns)
    print("Save csv data (size = {}) to {} done".format(df.shape[0], path))


def load_list(path):
    data = []
    try:
        with open(path, 'r') as f:
            data = f.readlines()
        data = [e.strip() for e in data]
    except:
        print("Error when load list from ", os.path.abspath(path))

    return data


def save_list(data, path, mode="w"):
    dir = path[:path.rfind("/")]
    mkdirs(dir)

    if mode == "a" or mode == "au":
        archive_data = load_list(path)
        data.extend(archive_data)

        if mode == "au":
            data = list(set(data))

    with open(path, 'w') as f:
        f.write("\n".join(data))
    print("Save list data (size = {}) to {} done".format(len(data), path))


class ProxyManager:
    def __init__(self, proxies_path="./Proxy/proxy_list.txt", proxy_type="https", update=False):
        self.proxies_path = proxies_path
        self.proxies = []
        self.load_proxies()
        if update:
            self.update_latest_proxies(proxy_type)

    @staticmethod
    def crawl_latest_proxies(proxy_type="https"):
        if proxy_type == "https":
            url = "https://www.sslproxies.org/"
        else:
            url = "https://free-proxy-list.net"
        root = html.document_fromstring(requests.get(url).content)

        th_elms = root.cssselect("table#proxylisttable thead tr th")
        columns = [th.text for th in th_elms]
        # print(columns)

        data = []
        tr_elms = root.cssselect("table#proxylisttable tbody tr")
        for tr in tr_elms:
            data.append([td.text for td in tr.cssselect("td")])

        df = pd.DataFrame(data, columns=columns)
        is_https_proxy = "yes" if proxy_type == "https" else "no"
        df = df[df["Https"] == is_https_proxy]

        print("Crawl {} proxies from {} done".format(df.shape[0], url))
        return df

    @staticmethod
    def _extract_proxy_urls(proxy_df):
        proxies = []
        for idx, row in proxy_df.iterrows():
            scheme = "https" if row["Https"] == "yes" else "http"
            url = "{}://{}:{}".format(scheme, row["IP Address"], row["Port"])
            proxies.append(url)

        return proxies

    def load_proxies(self, proxies_path=None):
        if proxies_path is None:
            proxies_path = self.proxies_path
        self.proxies = load_list(proxies_path)

    def save_proxies(self, proxies_path=None, mode="au"):
        if proxies_path is None:
            proxies_path = self.proxies_path
        save_list(self.proxies, proxies_path, mode=mode)
        print("Save {} proxies to {} done".format(len(self.proxies), os.path.abspath(self.proxies_path)))

    def update_latest_proxies(self, proxy_type="https"):
        proxy_df = ProxyManager.crawl_latest_proxies(proxy_type=proxy_type)
        self.proxies.extend(ProxyManager._extract_proxy_urls(proxy_df))
        self.proxies = list(set(self.proxies))
        self.save_proxies()

        print("Update latest proxies done. Number proxies : ", len(self.proxies))

    def generate_proxy_with_scheme(self):
        for proxy in self.proxies:
            if proxy.startswith("https"):
                scheme = "https"
            else:
                scheme = "http"

            yield {scheme: proxy}

    def get_response(self, url, timeout=3):
        random.shuffle(self.proxies)
        test_url = "https://httpbin.org/ip"
        sess = requests.Session()
        for proxy in self.generate_proxy_with_scheme():
            try:
                print("Searching valid proxy ...")
                sess.proxies = proxy
                sess.get(test_url, timeout=timeout)
                response = sess.get(url, proxies=proxy)
                print("Found valid proxy !")
                return response
            except:
                pass

        return None


def test_proxy():
    pm = ProxyManager()
    pm.save_proxies(mode="au")

    url = "https://httpbin.org/ip"
    res = pm.get_response(url)
    print(json.loads(res.content.decode("utf-8")))


if __name__ == "__main__":
    pass
    test_proxy()