# This code is quite ugly becase the logic in xunlei is disgusting.
# encoding:utf-8
import logging
import time
import json
import requests

import execjs
import libtorrent as lb

from download_provider import provider


class XunleiDownloadProvider(provider.DownloadProvider):
    def __init__(self, name: str) -> None:
        self.provider_name = name
        self.provider_type = 'xunlei_download_provider'
        self.http_endpoint = ''
        self.device_id = ''
        self.js_ctx = execjs.compile('')

    def get_provider_name(self) -> str:
        return self.provider_name

    def get_provider_type(self) -> str:
        return self.provider_type

    def provider_enabled(self) -> bool:
        cfg = provider.load_download_provider_config(self.provider_name)
        return cfg['enable']

    def provide_priority(self) -> int:
        cfg = provider.load_download_provider_config(self.provider_name)
        return cfg['priority']

    def get_defective_task(self) -> dict:
        # if xunlei doesn't work, it means other tools couldn't, so just ignore it.
        return []

    def send_torrent_task(self, torrent_file_path: str, download_path: str, extra_param=None) -> TypeError:
        logging.info('Start torrent download:%s', torrent_file_path)
        token = self.get_pan_token()
        if token == "":
            return None
        magnet_url = self.convert_torrent_to_magnet(torrent_file_path)
        file_info = self.list_files(token, magnet_url)
        return self.send_task(token, file_info, magnet_url, download_path)

    def send_magnet_task(self, url: str, path: str, extra_param=None) -> TypeError:
        logging.info('Start magnet download:%s', url)
        token = self.get_pan_token()
        if token == "":
            return None
        file_info = self.list_files(token, url)
        return self.send_task(token, file_info, url, path)

    def send_general_task(self, url: str, path: str, extra_param=None) -> TypeError:
        logging.info('Start general file download:%s', url)
        token = self.get_pan_token()
        if token == "":
            return None
        file_info = self.list_files(token, url)
        return self.send_task(token, file_info, url, path)

    def load_config(self) -> TypeError:
        cfg = provider.load_download_provider_config(self.provider_name)
        self.http_endpoint = cfg['http_endpoint']
        token_js_path = cfg['token_js_path']
        with open(token_js_path, 'r', encoding='utf-8') as js_file:
            js_text = js_file.read()
        self.js_ctx = execjs.compile(js_text)
        self.device_id = cfg['device_id']

    def list_files(self, token: str, url: str) -> dict:
        try:
            list_files_path = '/webman/3rdparty/pan-xunlei-com/index.cgi/drive/v1/resource/list?pan_auth=' + token + '&device_space='
            req_data = {'urls': url}
            req = requests.post(self.http_endpoint+list_files_path, json=req_data, headers={'pan-auth': token}, timeout=30)
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
                "type":"user#download-url",
                "name": file_info['list']['resources'][0]['name'],
                "file_name": file_info['list']['resources'][0]['name'],
                "file_size": str(file_size),
                "space": "device_id#" + self.device_id,
                "params": {
                    "target": "device_id#" + self.device_id,
                    "url": url,
                    "total_file_count": str(file_info['list']['resources'][0]['file_count']),
                    "sub_file_index": str(self.get_file_index(file_info)),
                    "file_id": "",
                    "parent_folder_id": path_id
                }
            }
            req = requests.post(self.http_endpoint + path, json=req_payload, headers={'pan-auth': token}, timeout=30)
            if req.status_code != 200:
                logging.error("Create tasks error:%s", req.text)
                return ValueError("Create task error")
            return None
        except Exception as err:
            logging.error('Send download task error:%s', err)
            return err

    def convert_torrent_to_magnet(self, torrent_file_path: str) -> str:
        info = lb.torrent_info(torrent_file_path)
        return 'magnet:?xt=urn:btih:' + str(info.info_hash()) + '&dn=' + info.name()

    def create_sub_path(self, token: str, dir_name: str, parent_id: str) -> TypeError:
        try:
            path = '/webman/3rdparty/pan-xunlei-com/index.cgi/drive/v1/files?pan_auth='+ token +'&device_space='
            rep = requests.get(self.http_endpoint + path, headers={'pan-auth': token}, timeout=30)
            data = {
                "parent_id": parent_id,
                "name": dir_name,
                "space": "device_id#" + self.device_id,
                "kind": "drive#folder"
            }
            rep = requests.post(self.http_endpoint + path, headers={'pan-auth': token}, timeout=30, json=data)
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
                file_path = '/webman/3rdparty/pan-xunlei-com/index.cgi/drive/v1/files?space=device_id%23' + \
                    self.device_id + '&limit=200&filters=%7B%22kind%22%3A%7B%22eq%22%3A%22drive%23folder%22%7D%7D&page_token=&' + \
                        'pan_auth=' + token + '&device_space=&parent_id=' + parent_id
                rep = requests.get(self.http_endpoint + file_path, headers={'pan-auth': token}, timeout=30)
                if rep.status_code != 200:
                    raise Exception('Get files id error:'+rep.text)
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

    def get_file_index(self, file_info: dict) -> str:
        file_count = int(file_info['list']['resources'][0]['file_count'])
        if file_count == 1:
            return '--1,'
        return '0-' + str(file_count-1)

    def get_pan_token(self) -> str:
        xunlei_e = int(time.time())
        xunlei_cn = int(time.time())
        try:
            rep = requests.get(self.http_endpoint+'/webman/3rdparty/pan-xunlei-com/index.cgi/device/now', timeout=30)
            xunlei_a1 = int(json.loads(rep.text).get('now'))
            xunlei_kn = xunlei_a1 - xunlei_cn
            token = self.js_ctx.call('GetXunLeiToken', xunlei_e + xunlei_kn)
            logging.info('Get xunlei token:%s', token)
            return token
        except Exception as err:
            logging.error("Get xunlei token error:%s", err)
            return ""
