from News_Crawler import utils
from lxml import html
import requests
import pandas as pd


def crawl_latest_proxies():
    url = "https://free-proxy-list.net"
    root = html.document_fromstring(requests.get(url).content)

    th_elms = root.cssselect("table#proxylisttable thead tr th")
    columns = [th.text for th in th_elms]
    print(columns)

    data = []

    tr_elms = root.cssselect("table#proxylisttable tbody tr")
    for tr in tr_elms:
        data.append([td.text for td in tr.cssselect("td")])

    print("Crawl {} proxies from {} done".format(len(data), url))
    return pd.DataFrame(data, columns=columns)


def get_proxy_urls(df):
    proxies = []
    for idx, row in df.iterrows():
        scheme = "https" if row["Https"] == "yes" else "http"
        url = "{}://{}:{}".format(scheme, row["IP Address"], row["Port"])
        proxies.append(url)

    return proxies


if __name__ == "__main__":
    proxies = crawl_latest_proxies()
    proxies.to_csv("./proxies.csv", index=False)

    proxy_urls = get_proxy_urls(proxies)
    utils.save_list(proxy_urls, path="./proxy_list.txt")
    print(proxies.head())

    print("\n".join(proxy_urls[:10]))
