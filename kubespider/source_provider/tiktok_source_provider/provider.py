# encoding:utf-8
import re
import logging

from urllib.parse import urlparse
from source_provider import provider
from utils import types
from utils.values import Event, Resource
from utils.config_reader import AbsConfigReader


class TiktokSourceProvider(provider.SourceProvider):

    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        super().__init__(config_reader)
        self.provider_listen_type = types.ProviderTypes.parser
        self.webhook_enable = True
        self.provider_type = 'tiktok_source_provider'
        self.provider_name = name

    def get_provider_name(self) -> str:
        return self.provider_name

    def get_provider_type(self) -> str:
        return self.provider_type

    def get_provider_listen_type(self) -> str:
        return self.provider_listen_type

    def get_download_provider_type(self) -> str:
        return 'tiktok_download_provider'

    def get_prefer_download_provider(self) -> list:
        downloader_names = self.config_reader.read().get('downloader', None)
        if downloader_names is None:
            return None
        if isinstance(downloader_names, list):
            return downloader_names
        return [downloader_names]

    def get_download_param(self) -> dict:
        return self.config_reader.read().get('download_param')

    def get_link_type(self) -> str:
        return types.LinkType.general

    def provider_enabled(self) -> bool:
        return self.config_reader.read().get('enable', True)

    def is_webhook_enable(self) -> bool:
        return True

    def should_handle(self, event: Event) -> bool:
        # regex get the real url, example: https://v.douyin.com/JJY5q5Y/
        link = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+',
                          event.source)[0]
        parse_url = urlparse(link)
        if parse_url.hostname == 'v.douyin.com':
            logging.info('%s belongs to tiktok_source_provider', link)
            return True
        return False

    def get_links(self, event: Event) -> list[Resource]:
        return [Resource(
            url=event.source,
            path='',
            file_type=types.FileType.video_mixed,
            link_type=self.get_link_type(),
        )]

    def update_config(self, event: Event) -> None:
        pass

    def load_config(self) -> None:
        pass
