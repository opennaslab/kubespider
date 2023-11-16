# This works for: https://www.bilibili.com/
# Function: download single video link
# encoding:utf-8
import logging
from urllib.parse import urlparse

from source_provider import provider
from api import types
from api.values import Event, Resource
from utils.config_reader import AbsConfigReader


class YouTubeSourceProvider(provider.SourceProvider):
    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        super().__init__(config_reader)
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
        return "ytdlp_download_provider"

    def get_download_param(self) -> dict:
        return self.config_reader.read().get('download_param', {})

    def get_prefer_download_provider(self) -> list:
        downloader_names = self.config_reader.read().get('downloader', None)
        if downloader_names is None:
            return None
        if isinstance(downloader_names, list):
            return downloader_names
        return [downloader_names]

    def get_link_type(self) -> str:
        return self.link_type

    def provider_enabled(self) -> bool:
        return self.config_reader.read().get('enable', True)

    def is_webhook_enable(self) -> bool:
        return self.webhook_enable

    def should_handle(self, event: Event) -> bool:
        parse_url = urlparse(event.source)
        if parse_url.hostname in ('www.youtube.com', 'youtube.com', 'm.youtube.com', 'youtu.be'):
            logging.info('%s belongs to youtube_source_provider', event.source)
            return True
        return False

    def get_links(self, event: Event) -> list[Resource]:
        return [Resource(
            url=event.source,
            path='',
            file_type=types.FILE_TYPE_VIDEO_MIXED,
            link_type=self.get_link_type(),
        )]

    def update_config(self, event: Event) -> None:
        pass

    def load_config(self) -> None:
        pass
