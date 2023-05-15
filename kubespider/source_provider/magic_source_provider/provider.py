# encoding:utf-8
import logging
from urllib.parse import urlparse
from lxml import etree

from source_provider import provider
from api import types
from utils import helper
from utils.config_reader import AbsConfigReader


class MagicSourceProvider(provider.SourceProvider):

    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        super().__init__(config_reader)
        self.provider_listen_type = types.SOURCE_PROVIDER_DISPOSABLE_TYPE
        self.webhook_enable = True
        self.provider_type = 'magic_source_provider'
        self.provider_name = name
        cfg = config_reader.read()
        self.handle_host = cfg['handle_host']
        self.link_selector = cfg['link_selector']
        self.title_selector = cfg['title_selector']
        # optional config
        self.link_type = cfg.get('link_type', 'magnet')
        self.file_type = cfg.get('file_type', 'video_mixed')
        self.charset = cfg.get('charset', 'utf-8')

    def get_provider_name(self) -> str:
        return self.provider_name

    def get_provider_type(self) -> str:
        return self.provider_type

    def get_provider_listen_type(self) -> str:
        return self.provider_listen_type

    def get_download_provider_type(self) -> str:
        pass

    def get_prefer_download_provider(self) -> list:
        return self.config_reader.read().get('downloader', None)

    def get_download_param(self) -> list:
        return self.config_reader.read().get('download_param')

    def get_link_type(self) -> str:
        return self.link_type

    def provider_enabled(self) -> bool:
        return self.config_reader.read().get('enable', False)

    def is_webhook_enable(self) -> bool:
        return True

    def should_handle(self, data_source_url: str) -> bool:
        if urlparse(data_source_url).hostname == self.handle_host:
            logging.info('%s belongs to MagicSourceProvider', data_source_url)
            return True
        return False

    def get_links(self, data_source_url: str) -> dict:
        ret = []
        try:
            controller = helper.get_request_controller()
            resp = controller.open(data_source_url, timeout=30).read()
        except Exception as err:
            logging.warning('MagicSourceProvider get links error:%s', err)
            return ret

        # decode html content, default utf-8, config on source_provider.yaml
        dom = etree.HTML(resp.decode(self.charset, 'ignore'))
        links = dom.xpath(self.link_selector)
        if len(links) < 1:
            return ret
        titles = dom.xpath(self.title_selector)
        if len(titles) < 1:
            path = helper.get_tmp_file_name(data_source_url)
        else:
            path = titles[0].strip()
        for link in links:
            url = link.strip()
            link_type = helper.get_link_type(url)
            if link_type != self.link_type:
                continue
            logging.info('MagicSourceProvider find %s', helper.format_long_string(url))
            ret.append({'path': path, 'link': url, 'file_type': self.file_type})

        return ret

    def update_config(self, req_para: str) -> None:
        pass

    def load_config(self) -> None:
        pass
