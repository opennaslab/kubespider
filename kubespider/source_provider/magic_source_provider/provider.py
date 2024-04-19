# encoding:utf-8
import os
import logging
from urllib.parse import urlparse
from lxml import etree

from source_provider import provider
from utils.values import Event, Resource
from utils import helper, types
from utils.config_reader import AbsConfigReader


class MagicSourceProvider(provider.SourceProvider):

    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        super().__init__(config_reader)
        self.provider_listen_type = types.ProviderTypes.parser
        self.webhook_enable = True
        self.provider_type = 'magic_source_provider'
        self.provider_name = name
        cfg = config_reader.read()
        self.handle_host = cfg.get('handle_host')
        self.link_selector = cfg.get('link_selector')
        self.title_selector = cfg.get('title_selector')
        # optional config
        self.link_type = cfg.get('link_type', types.LinkType.magnet)
        self.file_type = cfg.get('file_type', types.FileType.video_mixed)
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

    def get_download_param(self) -> dict:
        return self.config_reader.read().get('download_param')

    def get_link_type(self) -> str:
        return self.link_type

    def provider_enabled(self) -> bool:
        return self.config_reader.read().get('enable', False)

    def is_webhook_enable(self) -> bool:
        return True

    def should_handle(self, event: Event) -> bool:
        data_source_url = event.source
        if urlparse(data_source_url).hostname in self.handle_host:
            logging.info('%s belongs to %s', data_source_url, self.provider_name)
            return True
        return False

    def get_links(self, event: Event) -> list[Resource]:
        ret = []
        try:
            controller = helper.get_request_controller(event.extra_param('cookies', self.cookie))
            resp = controller.get(event.source, timeout=30).content
        except Exception as err:
            logging.warning('MagicSourceProvider get links error:%s', err)
            return ret

        # decode html content, default utf-8, config in source_provider.yaml
        dom = etree.HTML(resp.decode(self.charset, 'ignore'))

        links = []
        # $URL is a builtin value, used to represent the original url
        if '$URL' == self.link_selector:
            links = [event.source]
        else:
            # Some website's link is not always at the same place.
            # So if not, you can define multiple selectors
            if isinstance(self.link_selector, list):
                for selector in self.link_selector:
                    links.extend([i.strip() for i in dom.xpath(selector)])
            else:
                links = [i.strip() for i in dom.xpath(self.link_selector)]

        links = self.filter_links(event, links)

        if self.link_type == types.LinkType.torrent:
            links = self.pre_download_file(event, links)

        if len(links) < 1:
            logging.info("MagicSourceProvider get no links for %s", event.source)
            return ret

        if self.title_selector:
            titles = dom.xpath(self.title_selector)
            if len(titles) < 1:
                path = ''
            else:
                path = titles[0].strip()
        else:
            path = ''

        for link in links:
            logging.info('MagicSourceProvider find %s', helper.format_long_string(link))
            ret.append(Resource(
                url=link,
                path=path,
                file_type=self.file_type,
                link_type=self.link_type,
            ))
        return ret

    def update_config(self, event: Event) -> None:
        pass

    def load_config(self) -> None:
        pass

    def pre_download_file(self, event: Event, links: list) -> list:
        ret = []
        controller = helper.get_request_controller(event.extra_param('cookies', self.cookie))
        for link in links:
            file = helper.download_torrent_file(link, controller)
            if file is not None:
                ret.append(file)

        return ret

    def filter_links(self, event: Event, links: list) -> list:
        ret = []
        controller = helper.get_request_controller(event.extra_param('cookies', self.cookie))
        for link in links:
            # For this situation(the href is "text.torrent"), we need to construct the link
            link_current = link
            if not link.startswith('magnet:') and not link.startswith('http'):
                url_data = urlparse(event.source)
                link_current = os.path.join(url_data.scheme + "://" + url_data.netloc, link_current)

            link_type = helper.get_link_type(link_current, controller)
            if link_type != self.link_type:
                logging.info('MagicSourceProvider skip %s, the link type does not match',
                             helper.format_long_string(link_current))
                continue
            ret.append(link_current)

        return ret
