import os
import uuid
import hashlib


def get_tmp_file_name(url):
    file_name = os.path.basename(url)
    if file_name is None or file_name == '':
        file_name = uuid.uuid4().hex
    return '/tmp/' + file_name


def get_unique_hash(data):
    return hashlib.md5(data.encode('utf-8')).hexdigest()
