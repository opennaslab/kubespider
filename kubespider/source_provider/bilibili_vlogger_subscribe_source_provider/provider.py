# This works for: https://www.bilibili.com/
# Function: subscribe a bilibili vlogger
# encoding:utf-8
import logging
from api import types
from utils.config_reader import AbsConfigReader
from utils import helper
from source_provider import provider


class BilibiliVloggerSubscribeSourceProvider(provider.SourceProvider):
    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        super().__init__(config_reader)
        self.provider_listen_type = types.SOURCE_PROVIDER_PERIOD_TYPE
        self.link_type = types.LINK_TYPE_GENERAL
        self.webhook_enable = True
        self.provider_type = 'bilibili_vlogger_subscribe_source_provider'
        self.provider_name = name

    def get_provider_name(self) -> str:
        return self.provider_name

    def get_provider_type(self) -> str:
        return self.provider_type

    def get_provider_listen_type(self) -> str:
        return self.provider_listen_type

    def get_download_provider_type(self) -> str:
        return "youget_download_provider"

    def get_prefer_download_provider(self) -> list:
        downloader_names = self.config_reader.read().get('downloader', None)
        if downloader_names is None:
            return None
        if isinstance(downloader_names, list):
            return downloader_names
        return [downloader_names]

    def get_download_param(self) -> list:
        return self.config_reader.read().get('download_param', [])

    def get_link_type(self) -> str:
        return self.link_type

    def provider_enabled(self) -> bool:
        return self.config_reader.read().get('enable', True)

    def is_webhook_enable(self) -> bool:
        return False

    def should_handle(self, data_source_url: str) -> bool:
        return False

    def get_links(self, data_source_url: str) -> list:
        vloggers = self.config_reader.read().get('vlogger', None)
        if vloggers is None:
            return None
        if isinstance(vloggers, str):
            vloggers = [vloggers]

        controller = helper.get_request_controller()
        ret = []

        for vlogger in vloggers:
            try:
                data_link = "https://api.bilibili.com/x/space/wbi/arc/search?mid=" + str(vlogger)
                resp = controller.get(data_link, timeout=30).json()

                for video in resp['data']['list']['vlist']:
                    path = video['title']
                    link = "https://www.bilibili.com/video/" + video['bvid']
                    file_type = types.FILE_TYPE_VIDEO_MIXED
                    logging.info("BilibiliVloggerSubscribeSourceProvider get links %s", link)
                    ret.append({'path': path, 'link': link, 'file_type': file_type})
            except Exception as err:
                logging.error("BilibiliVloggerSubscribeSourceProvider get links error:%s", err)
                return None
        return ret

    def update_config(self, req_para: str) -> None:
        pass

    def load_config(self) -> None:
        pass
