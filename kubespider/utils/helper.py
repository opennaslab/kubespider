import uuid
import hashlib
import logging
import cgi
import urllib
from urllib.parse import urlparse
from urllib import request

from api import types
from api import values
from utils import global_config


def get_tmp_file_name(url):
    file_name = get_unique_hash(url)
    if file_name is None or file_name == '':
        file_name = uuid.uuid4().hex
    return '/tmp/' + file_name


def get_unique_hash(data):
    return hashlib.md5(data.encode('utf-8')).hexdigest()

def convert_file_type_to_path(file_type: str):
    if file_type in values.FILE_TYPE_TO_PATH.keys():
        return values.FILE_TYPE_TO_PATH[file_type]
    logging.warning('%s file file is not recorded', file_type)
    return file_type

def format_long_string(longstr: str) -> str:
    if len(longstr) > 40:
        return longstr[:40] + '...'
    return longstr

def get_request_controller() -> request.OpenerDirector:
    proxy_addr = global_config.get_proxy()

    proxy_handler = None
    handler: request.OpenerDirector = None
    if proxy_addr is not None:
        logging.info('Kubespider uses proxy:%s', proxy_addr)
        proxy_handler = urllib.request.ProxyHandler({'http': proxy_addr, 'https': proxy_addr})
        handler = request.build_opener(proxy_handler)
    else:
        handler = request.build_opener()

    headers = ("User-Agent", "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE")
    handler.addheaders = [headers]
    return handler

def get_link_type(url):
    if url.startswith('magnet:'):
        return types.LINK_TYPE_MAGNET
    if urlparse(url).path.endswith('torrent'):
        return types.LINK_TYPE_TORRENT
    # rfc6266: guess link type
    req = get_request_controller()
    try:
        resp = req.open(url, timeout=30)
        if resp.code == 200 and resp.headers.get('content-disposition'):
            content_disposition = resp.headers.get('content-disposition')
            _, params = cgi.parse_header(content_disposition)
            if params['filename'] and params['filename'].endswith('torrent'):
                return types.LINK_TYPE_TORRENT
    except Exception as err:
        logging.warning('Rfc6266 get link type error:%s', err)

    # TODO: implement other type, like music mv or short video
    return types.LINK_TYPE_GENERAL

def parse_cookie_string(cookie: str) -> dict:
    cookie_dict = {}
    for item in cookie.split(';'):
        key, value = item.strip().split('=')
        cookie_dict[key] = value
    return cookie_dict
