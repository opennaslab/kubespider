# This works for: https://www.bilibili.com/
# Function: download single video link
# encoding:utf-8
import logging
from urllib.parse import urlparse

from source_provider import provider
from api import types


class YouTubeSourceProvider(provider.SourceProvider):
    def __init__(self, name: str) -> None:
        self.provider_listen_type = types.SOURCE_PROVIDER_DISPOSABLE_TYPE
        self.link_type = types.LINK_TYPE_GENERAL
        self.webhook_enable = True
        self.provider_type = 'youtube_source_provider'
        self.provider_name = name

    def get_provider_name(self) -> str:
        return self.provider_name

    def get_provider_type(self) -> str:
        return self.provider_type

    def get_provider_listen_type(self) -> str:
        return self.provider_listen_type

    def get_download_provider_type(self) -> str:
        return "yt-dlp"

    def get_download_param(self) -> list:
        cfg = provider.load_source_provide_config(self.provider_name)
        return cfg.get('download_param')

    def get_prefer_download_provider(self) -> list:
        cfg = provider.load_source_provide_config(self.provider_name)
        return cfg.get('downloader')

    def get_link_type(self) -> str:
        return self.link_type

    def provider_enabled(self) -> bool:
        cfg = provider.load_source_provide_config(self.provider_name)
        return cfg.get('enable', True)

    def is_webhook_enable(self) -> bool:
        return self.webhook_enable

    def should_handle(self, data_source_url: str) -> bool:
        parse_url = urlparse(data_source_url)
        if parse_url.hostname == 'https://www.youtube.com/':
            logging.info('%s belongs to youtube_source_provider', data_source_url)
            return True
        return False

    def get_links(self, data_source_url: str) -> dict:
        return [{'path': '', 'link': data_source_url, 'file_type': types.FILE_TYPE_VIDEO_MIXED}]

    def update_config(self, req_para: str) -> None:
        pass

    def load_config(self) -> None:
        pass
