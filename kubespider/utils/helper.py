import os
import uuid
import hashlib
import logging
import threading
import cgi
from enum import Enum
from urllib.parse import urlparse
from utils.config_reader import YamlFileConfigReader

import urllib
from urllib import request
import yaml

from api import types

class Config(str, Enum):
    SOURCE_PROVIDER = 'source_provider.yaml'
    DOWNLOAD_PROVIDER = 'download_provider.yaml'
    KUBESPIDER_CONFIG = 'kubespider.yaml'
    STATE = 'state.yaml'

    def __str__(self) -> str:
        return str(self.value)
    
    def config_path(self) -> str:
        return os.path.join(cfg_base_path, self)

locks = { i.value: threading.Lock() for i in Config }
cfg_base_path = config_path = os.path.join(os.getenv('HOME'), '.config/')

def get_tmp_file_name(url):
    file_name = os.path.basename(url)
    if file_name is None or file_name == '':
        file_name = uuid.uuid4().hex
    return '/tmp/' + file_name


def get_unique_hash(data):
    return hashlib.md5(data.encode('utf-8')).hexdigest()

def load_config(cfg_type: Config):
    lock = locks.get(cfg_type)
    lock.acquire()
    try:
        return load_yaml_config(os.path.join(cfg_base_path, cfg_type))
    finally:
        lock.release()


def load_yaml_config(cfg_path):
    if not os.path.exists(cfg_path):
        return {}

    with open(cfg_path, 'r', encoding='utf-8') as config_file:
        cfg = yaml.safe_load(config_file)
        return cfg

def dump_yaml_config(cfg_path, cfg):
    with open(cfg_path, 'w', encoding='utf-8') as config_file:
        yaml.dump(cfg, config_file, encoding='utf-8')

def convert_file_type_to_path(file_type: str):
    if file_type in types.file_type_to_path.keys():
        return types.file_type_to_path[file_type]
    logging.warning('%s file file is not recorded', file_type)
    return file_type

def format_long_string(longstr: str) -> str:
    if len(longstr) > 40:
        return longstr[:40] + '...'
    return longstr

global_config = YamlFileConfigReader(Config.KUBESPIDER_CONFIG.config_path())

def get_proxy() -> str:
    cfg = global_config.read()
    if cfg is not None:
        return cfg.get('proxy', None)
    return None

def get_request_controller() -> request.OpenerDirector:
    proxy_addr = get_proxy()

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
