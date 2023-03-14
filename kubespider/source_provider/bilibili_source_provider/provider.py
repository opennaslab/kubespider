# This works for: https://www.bilibili.com/
# Function: download single video link
# encoding:utf-8
import logging
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from source_provider import provider
from api import types


class BilibiliSourceProvider(provider.SourceProvider):
    def __init__(self) -> None:
        self.provider_type = types.SOURCE_PROVIDER_DISPOSABLE_TYPE
        self.link_type = types.LINK_TYPE_GENERAL
        self.webhook_enable = True
        self.provider_name = 'bilibili_source_provider'

    def get_provider_name(self):
        return self.provider_name

    def get_provider_type(self):
        return self.provider_type

    def get_download_provider():
        return "youget_download_provider"

    def get_link_type(self):
        return self.link_type

    def provider_enabled(self):
        cfg = provider.load_source_provide_config(self.provider_name)
        return cfg['enable']

    def is_webhook_enable(self):
        return self.webhook_enable

    def should_handle(self, data_source_url: str):
        parse_url = urlparse(data_source_url)
        if parse_url.hostname == 'www.bilibili.com':
            logging.info('%s belongs to BilibiliSourceProvider', data_source_url)
            return True
        return False

    def get_links(self, data_source_url: str):
        return [{'path': '', 'link': data_source_url, 'file_type': ''}]

    def update_config(self, req_para: str):
        pass

    def load_config(self):
        pass
