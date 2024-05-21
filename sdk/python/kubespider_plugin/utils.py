import cgi
import hashlib
import logging
import uuid
from urllib.parse import urlparse
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


def get_link_type(url: str, controller: requests.Session) -> str:
    if url.startswith('magnet:'):
        return "magnet"
    if urlparse(url).path.endswith('torrent'):
        return "torrent"
    if not url.startswith('http'):
        # such as ed2k://xxx, we treat it as general
        # whether it could be downloaded depeneds on the download softwear
        return "general"
    # rfc6266: guess link type
    try:
        resp = controller.head(url, timeout=30, allow_redirects=True)
        if resp.status_code == 200 and resp.headers.get('content-disposition'):
            content_disposition = resp.headers.get('content-disposition')
            _, params = cgi.parse_header(content_disposition)
            if params['filename'] and params['filename'].endswith('torrent'):
                return "torrent"
    except Exception as err:
        logging.warning('Rfc6266 get link type error:%s', err)

    # TODO: implement other type, like music mv or short video
    return "general"


def download_torrent_file(url: str, controller: requests.Session) -> str:
    try:
        resp = controller.get(url, timeout=30).content
        file = get_tmp_file_name(url) + '.torrent'
        with open(file, 'wb') as file_write:
            file_write.write(resp)
        return file
    except Exception as err:
        logging.error("Download torrent file error:%s", err)
        return None


def get_tmp_file_name(url):
    file_name = get_unique_hash(url)
    if file_name is None or file_name == '':
        file_name = uuid.uuid4().hex
    return '/tmp/' + file_name


def format_long_string(longstr: str) -> str:
    if len(longstr) > 40:
        return longstr[:40] + '...'
    return longstr
