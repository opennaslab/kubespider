# This works for: https://www.meijutt.tv/
# Function: download tv video once it's updated
# encoding:utf-8
from urllib.parse import urlparse
import logging
from bs4 import BeautifulSoup

from api import types
from api.values import Event, Resource
from source_provider import provider
from utils import helper
from utils.config_reader import AbsConfigReader
from utils.helper import get_request_controller


class MeijuttSourceProvider(provider.SourceProvider):

    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        super().__init__(config_reader)
        self.provider_listen_type = types.SOURCE_PROVIDER_PERIOD_TYPE
        self.link_type = types.LINK_TYPE_MAGNET
        self.webhook_enable = True
        self.provider_type = 'meijutt_source_provider'
        self.tv_links = []
        self.provider_name = name
        self.request_handler = get_request_controller()

    def get_provider_name(self) -> str:
        return self.provider_name

    def get_provider_type(self) -> str:
        return self.provider_type

    def get_provider_listen_type(self) -> str:
        return self.provider_listen_type

    def get_download_provider_type(self) -> str:
        return None

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
        return self.config_reader.read().get('enable', True)

    def is_webhook_enable(self) -> bool:
        return True

    def should_handle(self, event: Event) -> bool:
        parse_url = urlparse(event.source)
        # Issue: #357, the hostname may be None
        # The url is easy to change because of DNS, so we use the prefix to judge
        if parse_url.hostname and "www.meijutt" in parse_url.hostname and 'content' in parse_url.path:
            logging.info('%s belongs to MeijuttSourceProvider', event.source)
            return True
        return False

    def get_links(self, event: Event) -> list[Resource]:
        ret = []
        for tv_link in self.tv_links:
            try:
                resp = self.request_handler.get(tv_link['link'], timeout=30).content
            except Exception as err:
                logging.info('meijutt_source_provider get links error:%s', err)
                continue
            dom = BeautifulSoup(resp, 'html.parser')
            div_list = dom.find_all('div', ['class', 'tabs-list'])

            # filter link type
            if len(div_list) == 0:
                continue
            for div in div_list:
                links=div.find_all('input', ['class', 'down_url'])
                url = links[0].get('value')
                link_type = helper.get_link_type(url, self.request_handler)
                if link_type == self.link_type:
                    break

            links = div.find_all('input', ['class', 'down_url'])
            for link in links:
                url = link.get('value')
                link_type = helper.get_link_type(url, self.request_handler)
                if link_type != self.link_type:
                    continue
                logging.info('meijutt find %s', helper.format_long_string(url))
                ret.append(Resource(
                    url=url,
                    path=tv_link['tv_name'],
                    file_type=types.FILE_TYPE_VIDEO_TV,
                    link_type=link_type,
                ))
        return ret

    def update_config(self, event: Event) -> None:
        cfg = self.config_reader.read()
        tv_links = cfg['tv_links']
        urls = [i['link'] for i in tv_links]
        if event.source not in urls:
            tv_title = self.get_tv_title(event)
            if tv_title == "":
                return
            tv_info = {'tv_name': tv_title, 'link': event.source}
            tv_links.append(tv_info)
        cfg['tv_links'] = tv_links
        self.config_reader.save(cfg)

    def load_config(self) -> None:
        cfg = self.config_reader.read()
        tv_links = [i['link'] for i in cfg['tv_links']]
        logging.info('meijutt tv link is:%s', ','.join(tv_links))
        self.tv_links = cfg['tv_links']

    def get_tv_title(self, event: Event) -> str:
        # example link: https://www.meijutt.tv/content/meiju28277.html
        try:
            req = self.request_handler.get(event.source, timeout=30)
        except Exception as err:
            logging.info('meijutt_source_provider get tv title error:%s', err)
            return ""
        dom = BeautifulSoup(req.content, 'html.parser')
        div = dom.find_all('div', ['class', 'info-title'])
        if len(div) == 0:
            logging.info('meijutt_source_provider get tv title empty:%s', event.source)
            return ""
        h1_title = div[0].find_all('h1')
        tv_title = h1_title[0].text.strip()
        logging.info('meijutt_source_provider get tv title:%s,%s', tv_title, event.source)
        return tv_title
