import os
import uuid
import hashlib
import json
import logging

from api import types


def get_tmp_file_name(url):
    file_name = os.path.basename(url)
    if file_name is None or file_name == '':
        file_name = uuid.uuid4().hex
    return '/tmp/' + file_name


def get_unique_hash(data):
    return hashlib.md5(data.encode('utf-8')).hexdigest()

def load_json_config(cfg_path, lock):
    lock.acquire()
    if not os.path.exists(cfg_path):
        lock.release()
        return {}

    with open(cfg_path, 'r', encoding='utf-8') as config_file:
        cfg = json.load(config_file)
        lock.release()
        return cfg

def dump_json_config(cfg_path, cfg, lock):
    lock.acquire()
    with open(cfg_path, 'w', encoding='utf-8') as config_file:
        json.dump(cfg, config_file, check_circular=False,
            indent=4, separators=(',', ':'), ensure_ascii=False)
        lock.release()

def convert_file_type_to_path(file_type: str):
    if file_type in types.file_type_to_path.keys():
        return types.file_type_to_path[file_type]
    logging.warning('%s file file is not recorded', file_type)
    return file_type
