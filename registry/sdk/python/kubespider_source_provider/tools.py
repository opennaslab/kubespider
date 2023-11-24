import functools
import hashlib
import logging
import time
import uuid

import requests


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


def get_request_controller(proxy_addr, cookie: str = None, use_proxy=True) -> requests.Session:
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


def get_unique_hash(data):
    return hashlib.md5(data.encode('utf-8')).hexdigest()


def get_tmp_file_name(url):
    file_name = get_unique_hash(url)
    if file_name is None or file_name == '':
        file_name = uuid.uuid4().hex
    return '/tmp/' + file_name


def format_long_string(longstr: str) -> str:
    if len(longstr) > 40:
        return longstr[:40] + '...'
    return longstr
