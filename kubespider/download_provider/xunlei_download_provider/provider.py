# This code is quite ugly becase the logic in xunlei is disgusting.
# encoding:utf-8
import logging
import re
import time
import json

import hashlib
import base64
from urllib.parse import quote

import execjs
import bencodepy

from utils.config_reader import AbsConfigReader
from utils.helper import get_request_controller
from utils.version_parser import check_version_at_lest
from download_provider import provider
from api.values import Task


class XunleiDownloadProvider(provider.DownloadProvider):
    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        super().__init__(name, config_reader)
        self.provider_name = name
        self.provider_type = 'xunlei_download_provider'
        self.http_endpoint = ''
        self._device_id = None
        self._token_str = None
        self._token_time = 0
        self.js_ctx = execjs.compile('')
        self.request_handler = get_request_controller(use_proxy=False)

    def get_provider_type(self) -> str:
        return self.provider_type

    def provider_enabled(self) -> bool:
        return self.config_reader.read()['enable']

    def provide_priority(self) -> int:
        return self.config_reader.read()['priority']

    def get_defective_task(self) -> list[Task]:
        # if xunlei doesn't work, it means other tools couldn't, so just ignore it.
        return []

    def send_torrent_task(self, task: Task) -> TypeError:
        logging.info('Start torrent download:%s', task.url)
        token = self.get_pan_token()
        if token == "":
            return None
        magnet_url = self.convert_torrent_to_magnet(task.url)
        file_info = self.list_files(token, magnet_url)
        return self.send_task(token, file_info, magnet_url, task.path)

    def device_id(self, url_encode: bool = False):
        if self._device_id is None:
            info_watch = "/webman/3rdparty/pan-xunlei-com/index.cgi/device/info/watch"
            token = self.get_pan_token()
            req = self.request_handler.post(self.http_endpoint + info_watch,
                                            headers={'pan-auth': token}, timeout=30)
            self._device_id = str(json.loads(req.text).get("target"))
            logging.info('Get xunlei device_id: %s', self._device_id)
        return self._device_id if not url_encode else quote(self._device_id)

    def send_magnet_task(self, task: Task) -> TypeError:
        logging.info('Start magnet download:%s', task.url)
        token = self.get_pan_token()
        if token == "":
            return None
        file_info = self.list_files(token, task.url)
        return self.send_task(token, file_info, task.url, task.path)

    def send_general_task(self, task: Task) -> TypeError:
        logging.info('Start general file download:%s', task.url)
        token = self.get_pan_token()
        if token == "":
            return None
        file_info = self.list_files(token, task.url)
        return self.send_task(token, file_info, task.url, task.path)

    def remove_tasks(self, tasks: list[Task]):
        # TODO: Implement it
        pass

    def load_config(self) -> TypeError:
        cfg = self.config_reader.read()
        self.http_endpoint = cfg.get('http_endpoint', 'http://127.0.0.1:2345')
        try:
            token_js_path = cfg.get('token_js_path', '/app/.config/dependencies/xunlei_download_provider/get_token.js')
            with open(token_js_path, 'r', encoding='utf-8') as js_file:
                js_text = js_file.read()
            self.js_ctx = execjs.compile(js_text)
        except Exception as err:
            logging.error("Cannot read .config/dependencies/xunlei_download_provider/get_token.js: %s", err)

    def list_files(self, token: str, url: str) -> dict:
        try:
            list_files_path = '/webman/3rdparty/pan-xunlei-com/index.cgi/drive/v1/resource/list?pan_auth=' + token + '&device_space='
            req_data = {'urls': url}
            req = self.request_handler.post(self.http_endpoint + list_files_path, json=req_data,
                                            headers={'pan-auth': token}, timeout=30)
            return json.loads(req.text)
        except Exception as err:
            logging.error("List files error:%s", err)
            return None

    def send_task(self, token: str, file_info: dict, url: str, path: str) -> TypeError:
        try:
            path_id = self.get_path_id(token, path)
            if path_id is None:
                raise Exception('Get path id error')
            path = '/webman/3rdparty/pan-xunlei-com/index.cgi/drive/v1/task?pan_auth=' + token + 'device_space='
            file_size = 0
            if 'file_size' in file_info['list']['resources'][0]:
                file_size = file_info['list']['resources'][0]['file_size']
            req_payload = {
                "type": "user#download-url",
                "name": file_info['list']['resources'][0]['name'],
                "file_name": file_info['list']['resources'][0]['name'],
                "file_size": str(file_size),
                "space": self.device_id(),
                "params": {
                    "target": self.device_id(),
                    "url": url,
                    "total_file_count": str(file_info['list']['resources'][0]['file_count']),
                    "sub_file_index": str(self.get_file_index(file_info)),
                    "file_id": "",
                    "parent_folder_id": path_id
                }
            }
            req = self.request_handler.post(self.http_endpoint + path, json=req_payload, headers={'pan-auth': token},
                                            timeout=30)
            if req.status_code != 200:
                logging.error("Create tasks error:%s", req.text)
                return ValueError("Create task error")
            return None
        except Exception as err:
            logging.error('Send download task error:%s', err)
            return err

    def convert_torrent_to_magnet(self, torrent_file_path: str) -> str:
        # https://github.com/DanySK/torrent2magnet/blob/develop/torrent2magnet.py
        metadata = bencodepy.decode_from_file(torrent_file_path)
        subj = metadata[b'info']
        hashcontents = bencodepy.encode(subj)
        digest = hashlib.sha1(hashcontents).digest()
        b32hash = base64.b32encode(digest).decode()
        return 'magnet:?'\
                 + 'xt=urn:btih:' + b32hash\
                 + '&dn=' + metadata[b'info'][b'name'].decode()

    def create_sub_path(self, token: str, dir_name: str, parent_id: str) -> TypeError:
        try:
            path = '/webman/3rdparty/pan-xunlei-com/index.cgi/drive/v1/files?pan_auth=' + token + '&device_space='
            rep = self.request_handler.get(self.http_endpoint + path, headers={'pan-auth': token}, timeout=30)
            data = {
                "parent_id": parent_id,
                "name": dir_name,
                "space": self.device_id(),
                "kind": "drive#folder"
            }
            rep = self.request_handler.post(self.http_endpoint + path, headers={'pan-auth': token}, timeout=30,
                                            json=data)
            return json.loads(rep.text)['file']['id']
        except Exception as err:
            logging.error('Create dir error:%s', err)
            return err

    def get_path_id(self, token: str, path: str) -> str:
        try:
            parent_id = ""
            dir_list = path.split('/')
            # ncessary to remove empty value, or will failed
            if '' in dir_list:
                dir_list.remove('')
            cnt = 0
            while 1:
                if len(dir_list) == cnt:
                    return parent_id
                file_path = ('/webman/3rdparty/pan-xunlei-com/index.cgi/drive/v1/files?space=' +
                             self.device_id(url_encode=True) + '&limit=200&' +
                             'filters=%7B%22kind%22%3A%7B%22eq%22%3A%22drive%23folder%22%7D%7D&page_token=&' +
                             'pan_auth=' + token + '&device_space=&parent_id=' + parent_id)
                rep = self.request_handler.get(self.http_endpoint + file_path, headers={'pan-auth': token}, timeout=30)
                if rep.status_code != 200:
                    raise Exception('Get files id error:' + rep.text)
                dirs = json.loads(rep.text)
                if parent_id == "":
                    parent_id = dirs['files'][0]['id']
                    continue

                exists = False
                if 'files' in dirs.keys():
                    for dir_now in dirs['files']:
                        if dir_now['name'] == dir_list[cnt]:
                            cnt += 1
                            exists = True
                            parent_id = dir_now['id']
                            break

                if exists:
                    continue

                parent_id = self.create_sub_path(token, dir_list[cnt], parent_id)
                if parent_id is None:
                    return None
                cnt += 1

        except Exception as err:
            logging.error("get path id error:%s", err)
            return ""

    def get_server_version(self) -> str:
        try:
            rep = self.request_handler.get(self.http_endpoint + '/webman/3rdparty/pan-xunlei-com/index.cgi/launcher/status',
                                           timeout=30)
            return str(json.loads(rep.text).get('running_version'))
        except Exception as err:
            logging.error("get xunlei server version error:%s", err)
            return ""

    def get_file_index(self, file_info: dict) -> str:
        file_count = int(file_info['list']['resources'][0]['file_count'])
        if file_count == 1:
            return '--1,'
        return '0-' + str(file_count - 1)

    def get_pan_token(self) -> str:
        server_version = self.get_server_version()
        if check_version_at_lest(server_version, "3.21.0"):
            if self._token_str is not None and self._token_time + 600 > int(time.time()):
                return self._token_str
            resp = self.request_handler.get(self.http_endpoint + '/webman/3rdparty/pan-xunlei-com/index.cgi/',
                                           timeout=30)
            uiauth = r'function uiauth\(value\){ return "(.*)" }'
            for script in re.findall(uiauth, resp.text):
                self._token_str = script
                self._token_time = int(time.time())
                logging.info('Get xunlei token from html:%s', self._token_str)
                return self._token_str
            logging.error('Get xunlei token from html error')
            return ""

        xunlei_e = int(time.time())
        xunlei_cn = int(time.time())
        try:
            rep = self.request_handler.get(self.http_endpoint + '/webman/3rdparty/pan-xunlei-com/index.cgi/device/now',
                                           timeout=30)
            xunlei_a1 = int(json.loads(rep.text).get('now'))
            xunlei_kn = xunlei_a1 - xunlei_cn
            token = self.js_ctx.call('GetXunLeiToken', xunlei_e + xunlei_kn)
            logging.info('Get xunlei token:%s', token)
            return token
        except Exception as err:
            logging.error("Get xunlei token error:%s", err)
            return ""
