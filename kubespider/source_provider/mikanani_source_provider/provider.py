# This works for: https://mikanani.me
# Function: download anime you subscribe
# encoding:utf-8
import logging

import xml.etree.ElementTree as ET
import re
from re import Pattern
from bs4 import BeautifulSoup

from source_provider import provider
from api import types
from api.values import Event, Resource
from utils import helper
from utils.config_reader import AbsConfigReader


class MikananiSourceProvider(provider.SourceProvider):
    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        super().__init__(config_reader)
        self.provider_listen_type = types.SOURCE_PROVIDER_PERIOD_TYPE
        self.link_type = types.LINK_TYPE_TORRENT
        self.webhook_enable = False
        self.provider_type = 'mikanani_source_provider'
        self.rss_link = ''
        self.tmp_file_path = '/tmp/'
        self.provider_name = name

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
        return self.config_reader.read().get('download_param', {})

    def get_link_type(self) -> str:
        return self.link_type

    def provider_enabled(self) -> bool:
        return self.config_reader.read().get('enable', True)

    def is_webhook_enable(self) -> bool:
        return self.webhook_enable

    def should_handle(self, event: Event) -> bool:
        return False

    def get_links(self, event: Event) -> list[Resource]:
        try:
            req = helper.get_request_controller()
            links_data = req.get(self.rss_link, timeout=30).content
        except Exception as err:
            logging.info('mikanani get links error:%s', err)
            return []
        tmp_xml = helper.get_tmp_file_name('') + '.xml'
        with open(tmp_xml, 'wb') as cfg_file:
            cfg_file.write(links_data)
            cfg_file.close()
        pattern = self.load_filter_config()
        return self.get_links_from_xml(tmp_xml, pattern)

    def get_links_from_xml(self, tmp_xml, pattern: str) -> list[Resource]:
        if pattern is not None:
            reg = re.compile(pattern)
        else:
            reg = None
        try:
            xml_parse = ET.parse(tmp_xml)
            items = xml_parse.findall('.//item')
            ret = []
            for i in items:
                anime_name = i.find('./guid').text
                path = None
                try_count = 0
                while path is None and try_count < 6:
                    path = self.get_anime_path(i)
                    try_count += 1
                item_title = self.get_anime_title(i, reg)
                logging.info('mikanani find %s', helper.format_long_string(anime_name))
                url = i.find('./enclosure').attrib['url']
                if path is not None and item_title is not None:
                    ret.append(Resource(
                        url=url,
                        path=path,
                        file_type=types.FILE_TYPE_VIDEO_TV,
                        link_type=self.get_link_type(),
                    ))
                else:
                    logging.warning("Skip %s, %s", anime_name, item_title)
            return ret
        except Exception as err:
            logging.info('parse rss xml error:%s', err)
            return []

    def load_filter_config(self) -> str:
        return self.config_reader.read().get('filter', None)

    def get_anime_path(self, element) -> str:
        # get the path of anime source, or None for invalid item
        return self.get_file_title(element.find('./link').text)

    def get_anime_title(self, element, pattern: Pattern) -> str:
        # get the episode name of anime source, or None for invalid item
        title = element.find('./title').text
        return self.check_anime_title(title, pattern)

    def check_anime_title(self, title, pattern: Pattern) -> str:
        logging.debug("Checking title %s with pattern %s", title, pattern)
        if pattern is None or pattern.match(title):
            return title
        logging.warning("Episode %s will not be downloaded, filtered by %s", title, pattern)
        return None

    def update_config(self, event: Event) -> None:
        pass

    def load_config(self) -> None:
        cfg = self.config_reader.read()
        logging.info('mikanani rss link is:%s', cfg['rss_link'])
        self.rss_link = cfg['rss_link']

    def get_file_title(self, link: str) -> str:
        # example: https://mikanani.me/Home/Episode/5350b283db7d8e4665a08dda24d0d0c66259fc71
        try:
            req = helper.get_request_controller()
            data = req.get(link, timeout=30).content
        except Exception as err:
            logging.info('mikanani get anime title error:%s', err)
            return None
        dom = BeautifulSoup(data, 'html.parser')
        titles = dom.find_all('a', ['class', 'w-other-c'])
        if len(titles) == 0:
            logging.error('mikanani get anime title empty:%s', link)
            return None
        title = titles[0].text.strip()
        logging.info('mikanani get anime title:%s', title)
        return title
