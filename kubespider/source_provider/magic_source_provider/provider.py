# encoding:utf-8
import os
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
        self.cookie = cfg.get('cookie', None)
        self.pre_download = bool(cfg.get('pre_download', False))

    def get_provider_name(self) -> str:
        return self.provider_name

    def get_provider_type(self) -> str:
        return self.provider_type

    def get_provider_listen_type(self) -> str:
        return self.provider_listen_type

    def get_download_provider_type(self) -> str:
        pass

    def get_prefer_download_provider(self) -> list:
        downloader_names = self.config_reader.read().get('downloader', None)
        if downloader_names is None:
            return None
        if isinstance(downloader_names, list):
            return downloader_names
        return [downloader_names]

    def get_download_param(self) -> list:
        return self.config_reader.read().get('download_param')

    def get_link_type(self) -> str:
        return self.link_type

    def provider_enabled(self) -> bool:
        return self.config_reader.read().get('enable', False)

    def is_webhook_enable(self) -> bool:
        return True

    def should_handle(self, data_source_url: str) -> bool:
        if urlparse(data_source_url).hostname in self.handle_host:
            logging.info('%s belongs to %s', data_source_url, self.provider_name)
            return True
        return False

    def get_links(self, data_source_url: str) -> dict:
        ret = []
        try:
            controller = helper.get_request_controller(self.cookie)
            resp = controller.open(data_source_url, timeout=30).read()
        except Exception as err:
            logging.warning('MagicSourceProvider get links error:%s', err)
            return ret

        # decode html content, default utf-8, config in source_provider.yaml
        dom = etree.HTML(resp.decode(self.charset, 'ignore'))

        links = []
        # $URL is a builtin value, used to represent the original url
        if '$URL' == self.link_selector:
            links = [data_source_url]
        else:
            # Some website's link is not always at the same place.
            # So if not, you can define multiple selectors
            if isinstance(self.link_selector, list):
                for selector in self.link_selector:
                    links.extend([i.strip() for i in dom.xpath(selector)])
            else:
                links = [i.strip() for i in dom.xpath(self.link_selector)]

        links = self.filter_links(data_source_url, links)

        if self.link_type == types.LINK_TYPE_TORRENT:
            links = self.pre_download_file(links)

        if len(links) < 1:
            logging.info("MagicSourceProvider get no links for %s", data_source_url)
            return ret
        titles = dom.xpath(self.title_selector)
        if len(titles) < 1:
            path = ''
        else:
            path = titles[0].strip()

        for link in links:
            logging.info('MagicSourceProvider find %s', helper.format_long_string(link))
            ret.append({'path': path, 'link': link, 'file_type': self.file_type})

        return ret

    def update_config(self, req_para: str) -> None:
        pass

    def load_config(self) -> None:
        pass

    def pre_download_file(self, links: list) -> list:
        ret = []
        controller = helper.get_request_controller(self.cookie)
        for link in links:
            file = helper.download_torrent_file(link, controller)
            if file is not None:
                ret.append(file)

        return ret

    def filter_links(self, data_source_url: str, links: list) -> list:
        ret = []

        controller = helper.get_request_controller(self.cookie)
        for link in links:
            #For this situation(the href is "text.torrent"), we need to construct the link
            link_current = link
            if not link.startswith('magnet:') and \
                not link.startswith('http'):
                url_data = urlparse(data_source_url)
                link_current = os.path.join(url_data.scheme + "://" + url_data.netloc, link_current)

            link_type = helper.get_link_type(link_current, controller)
            if link_type != self.link_type:
                logging.info('MagicSourceProvider skip %s, the link type does not match', helper.format_long_string(link_current))
                continue
            ret.append(link_current)

        return ret
