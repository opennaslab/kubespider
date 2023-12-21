import functools
import inspect
import re
import uuid
import hashlib
import logging
import cgi
import os
import time
from urllib.parse import urlparse

import requests

from utils import values
from utils.global_config import Config
from utils.types import LinkType, ProviderType


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


def get_request_controller(cookie: str = None, use_proxy=True) -> requests.Session:
    proxy_addr = Config.PROXY
    session = requests.Session()
    proxies = {"http": proxy_addr, "https": proxy_addr} if all([proxy_addr, use_proxy]) else {}
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE"
    }
    session.headers = headers
    session.proxies = proxies
    if cookie is None:
        return session

    coockie_dict = parse_cookie_string(cookie)
    for cookie_name, cookie_value in coockie_dict.items():
        session.cookies.set(cookie_name, cookie_value)
    return session


def get_link_type(url: str, controller: requests.Session) -> str:
    if url.startswith('magnet:'):
        return LinkType.magnet
    if urlparse(url).path.endswith('torrent'):
        return LinkType.torrent
    if not url.startswith('http'):
        # such as ed2k://xxx, we treat it as general
        # whether it could be downloaded depeneds on the download softwear
        return LinkType.general
    # rfc6266: guess link type
    try:
        resp = controller.head(url, timeout=30, allow_redirects=True)
        if resp.status_code == 200 and resp.headers.get('content-disposition'):
            content_disposition = resp.headers.get('content-disposition')
            _, params = cgi.parse_header(content_disposition)
            if params['filename'] and params['filename'].endswith('torrent'):
                return LinkType.torrent
    except Exception as err:
        logging.warning('Rfc6266 get link type error:%s', err)

    # TODO: implement other type, like music mv or short video
    return LinkType.general


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


def is_running_in_docker() -> bool:
    # check is running in docker container
    return os.path.exists('/.dockerenv')


def retry(attempt_times=3, delay=1, exception=Exception):
    """
    try serval times to invoke the target method.

    params:
        attempt_times: The number of attempts, default 3.
        delay: The time between each attempt, time unit is second, default 1 second.
        exception: The exception to catch while invoking the method, default Exception.
    """

    def decorator(function):
        @functools.wraps(function)
        def retry_handle(*args, **kwargs):
            total_attempt_times = 1
            while total_attempt_times <= attempt_times:
                try:
                    return function(*args, **kwargs)
                except exception as err:
                    logging.error('Error happened, func: %s, err: %s, retrying...', function.__name__, err)
                    time.sleep(delay)
                    total_attempt_times += 1
            return None

        return retry_handle

    return decorator


def extract_doc(obj):
    return inspect.getdoc(obj)


def parse_func_doc(func):
    doc = extract_doc(func)
    if not doc:
        return {}
    data = re.findall(r':param[ ]*([^\W]*)[ ]*:[ ]*([^\n]*)', doc)
    return {item[0]: item[1] for item in data if all(item)}


def get_provider_conf_base_path(provider_type):
    if provider_type == ProviderType.download_provider:
        base_path = values.Config.DOWNLOAD_PROVIDERS_CONF.config_path()
    elif provider_type == ProviderType.notification_provider:
        base_path = values.Config.NOTIFICATION_PROVIDERS_CONF.config_path()
    elif provider_type == ProviderType.source_provider:
        base_path = values.Config.SOURCE_PROVIDERS_CONF.config_path()
    else:
        raise Exception(f"Unknown Provider Type: {provider_type}")
    return base_path
