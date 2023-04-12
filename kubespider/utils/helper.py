import os
import uuid
import hashlib
import json
import logging
import threading
from enum import Enum

import yaml
from api import types

class Config(str, Enum):
    SOURCE_PROVIDER = 'source_provider'
    DOWNLOAD_PROVIDER = 'download_provider'
    STATE = 'state'

    def __str__(self) -> str:
        return str(self.value)

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
    yaml_file = cfg_type + '.yaml'
    json_file = cfg_type + '.cfg'
    try:
        if os.path.exists(os.path.join(cfg_base_path, yaml_file)):
            # yaml config exists, read it
            return load_yaml_config(os.path.join(cfg_base_path, yaml_file))
        # read origin json config, or failed if both not exists
        return load_json_config(os.path.join(cfg_base_path, json_file))
    finally:
        lock.release()

def dump_config(cfg_type: Config, cfg):
    lock = locks.get(cfg_type)
    lock.acquire()
    yaml_file = cfg_type + '.yaml'
    json_file = cfg_type + '.cfg'
    # if json config file exists, dump there
    if os.path.exists(os.path.join(cfg_base_path, json_file)):
        dump_json_config(os.path.join(cfg_base_path, json_file), cfg)
    else:
        dump_yaml_config(os.path.join(cfg_base_path, yaml_file), cfg)
    lock.release()

def load_json_config(cfg_path):
    if not os.path.exists(cfg_path):
        return {}

    with open(cfg_path, 'r', encoding='utf-8') as config_file:
        cfg = json.load(config_file)
        return cfg

def dump_json_config(cfg_path, cfg):
    with open(cfg_path, 'w', encoding='utf-8') as config_file:
        json.dump(cfg, config_file, check_circular=False,
            indent=4, separators=(',', ':'), ensure_ascii=False)

def load_yaml_config(cfg_path):
    if not os.path.exists(cfg_path):
        return {}

    with open(cfg_path, 'r', encoding='utf-8') as config_file:
        cfg = yaml.load(config_file)
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
