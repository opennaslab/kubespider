import hashlib

import requests


def get_request_controller(proxy_addr: str = "", cookie: str = None, use_proxy=True) -> requests.Session:
    session = requests.Session()
    proxies = {"http": proxy_addr, "https": proxy_addr} if all(
        [proxy_addr, use_proxy]) else {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE"
    }
    session.headers = headers
    session.proxies = proxies
    if cookie is None:
        return session

    cookie_dict = parse_cookie_string(cookie)
    for cookie_name, cookie_value in cookie_dict.items():
        session.cookies.set(cookie_name, cookie_value)
    return session


def parse_cookie_string(cookie: str) -> dict:
    cookie_dict = {}
    # fix: cookie may be None or empty
    if cookie is None or not cookie:
        return cookie_dict
    for item in cookie.split(';'):
        # fix: cookie value may contain '='
        key, value = item.strip().split('=', 1)
        cookie_dict[key] = value
    return cookie_dict


def get_unique_hash(data):
    return hashlib.md5(data.encode('utf-8')).hexdigest()
