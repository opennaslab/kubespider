# This works for: https://www.bilibili.com/
# Function: subscribe a bilibili vlogger
# encoding:utf-8
import logging
from api import types
from api.values import Event, Resource
from utils.config_reader import AbsConfigReader
from utils import helper
from source_provider import provider


from functools import reduce
from hashlib import md5
import urllib.parse
import time
import requests

mixinKeyEncTab = [
    46, 47, 18, 2, 53, 8, 23, 32, 15, 50, 10, 31, 58, 3, 45, 35, 27, 43, 5, 49,
    33, 9, 42, 19, 29, 28, 14, 39, 12, 38, 41, 13, 37, 48, 7, 16, 24, 55, 40,
    61, 26, 17, 0, 1, 60, 51, 30, 4, 22, 25, 54, 21, 56, 59, 6, 63, 57, 62, 11,
    36, 20, 34, 44, 52
]

def getMixinKey(orig: str):
    return reduce(lambda s, i: s + orig[i], mixinKeyEncTab, '')[:32]

def encWbi(params: dict, img_key: str, sub_key: str):
    mixin_key = getMixinKey(img_key + sub_key)
    curr_time = round(time.time())
    params['wts'] = curr_time                                   # 添加 wts 字段
    params = dict(sorted(params.items()))                       # 按照 key 重排参数
    params = {
        k : ''.join(filter(lambda chr: chr not in "!'()*", str(v)))
        for k, v 
        in params.items()
    }
    query = urllib.parse.urlencode(params)                      # 序列化参数
    wbi_sign = md5((query + mixin_key).encode()).hexdigest()    # 计算 w_rid
    params['w_rid'] = wbi_sign
    return params

def getWbiKeys() -> tuple[str, str]:
    resp = requests.get('https://api.bilibili.com/x/web-interface/nav')
    resp.raise_for_status()
    json_content = resp.json()
    img_url: str = json_content['data']['wbi_img']['img_url']
    sub_url: str = json_content['data']['wbi_img']['sub_url']
    img_key = img_url.rsplit('/', 1)[1].split('.')[0]
    sub_key = sub_url.rsplit('/', 1)[1].split('.')[0]
    return img_key, sub_key

# img_key, sub_key = getWbiKeys()
#
# signed_params = encWbi(
#     params={
#         'foo': '114',
#         'bar': '514',
#         'baz': 1919810
#     },
#     img_key=img_key,
#     sub_key=sub_key
# )
# query = urllib.parse.urlencode(signed_params)
# print(signed_params)
# print(query)

class BilibiliVloggerSubscribeSourceProvider(provider.SourceProvider):
    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        super().__init__(config_reader)
        self.provider_listen_type = types.SOURCE_PROVIDER_PERIOD_TYPE
        self.link_type = types.LINK_TYPE_GENERAL
        self.webhook_enable = True
        self.provider_type = 'bilibili_vlogger_subscribe_source_provider'
        self.provider_name = name
        self.sessdata = ""

    def get_provider_name(self) -> str:
        return self.provider_name

    def get_provider_type(self) -> str:
        return self.provider_type

    def get_provider_listen_type(self) -> str:
        return self.provider_listen_type

    def get_download_provider_type(self) -> str:
        return "yutto_download_provider"

    def get_prefer_download_provider(self) -> list:
        downloader_names = self.config_reader.read().get('downloader', None)
        if downloader_names is None:
            return None
        if isinstance(downloader_names, list):
            return downloader_names
        return [downloader_names]

    def get_download_param(self) -> dict:
        return self.config_reader.read().get('download_param', {})

    def get_link_type(self) -> str:
        return self.link_type

    def provider_enabled(self) -> bool:
        return self.config_reader.read().get('enable', True)

    def is_webhook_enable(self) -> bool:
        return False

    def should_handle(self, event: Event) -> bool:
        return False

    def get_links(self, event: Event) -> list[Resource]:
        vloggers = self.config_reader.read().get('vlogger', None)
        if vloggers is None:
            return None
        if isinstance(vloggers, str):
            vloggers = [vloggers]

        controller = helper.get_request_controller(cookie="SESSDATA={}".format(self.sessdata))
        ret = []

        resp = controller.get('https://api.bilibili.com/x/web-interface/nav')
        resp.raise_for_status()
        json_content = resp.json()
        img_url: str = json_content['data']['wbi_img']['img_url']
        sub_url: str = json_content['data']['wbi_img']['sub_url']
        img_key = img_url.rsplit('/', 1)[1].split('.')[0]
        sub_key = sub_url.rsplit('/', 1)[1].split('.')[0]

        for vlogger in vloggers:
            try:
                signed_params = encWbi(
                    params={"mid": int(vlogger)},
                    img_key=img_key,
                    sub_key=sub_key,
                )
                query = urllib.parse.urlencode(signed_params)
                data_link = "https://api.bilibili.com/x/space/wbi/arc/search?" + query
                resp = controller.get(data_link, timeout=30).json()
                for video in resp['data']['list']['vlist']:
                    path = video['title']
                    link = "https://www.bilibili.com/video/" + video['bvid']
                    file_type = types.FILE_TYPE_VIDEO_MIXED
                    ret.append(Resource(
                        url=link,
                        path=path,
                        file_type=file_type,
                        link_type=self.get_link_type(),
                    ))
                    logging.info("BilibiliVloggerSubscribeSourceProvider get links %s", link)
            except Exception as err:
                logging.error("BilibiliVloggerSubscribeSourceProvider get links error:%s", err)
                return None
        return ret

    def update_config(self, event: Event) -> None:
        pass

    def load_config(self) -> None:
        cfg = self.config_reader.read()
        self.sessdata = cfg.get("sessdata", "")
        if self.sessdata == "":
            logging.error("SESS_DATA is empty, bilibili_vlogger_subscribe_source_provider will not work")
