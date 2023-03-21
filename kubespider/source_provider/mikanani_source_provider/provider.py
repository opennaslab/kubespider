# This works for: https://mikanani.me
# Function: download anime you subscribe
# encoding:utf-8
import logging

import xml.etree.ElementTree as ET
import requests
from bs4 import BeautifulSoup

from source_provider import provider
from api import types
from utils import helper


class MikananiSourceProvider(provider.SourceProvider):
    def __init__(self) -> None:
        self.provider_type = types.SOURCE_PROVIDER_PERIOD_TYPE
        self.link_type = types.LINK_TYPE_TORRENT
        self.webhook_enable = False
        self.provider_name = 'mikanani_source_provider'
        self.rss_link = ''
        self.tmp_file_path = '/tmp/'

    def get_provider_name(self) -> str:
        return self.provider_name

    def get_provider_type(self) -> str:
        return self.provider_type

    def get_download_provider(self) -> str:
        return None

    def get_link_type(self) -> str:
        return self.link_type

    def provider_enabled(self) -> bool:
        cfg = provider.load_source_provide_config(self.provider_name)
        return cfg['enable']

    def is_webhook_enable(self) -> bool:
        return self.webhook_enable

    def should_handle(self, data_source_url: str) -> bool:
        return False

    def get_links(self, data_source_url: str) -> dict:
        try:
            req = requests.get(self.rss_link, timeout=30)
        except Exception as err:
            logging.info('mikanani get links error:%s', err)
            return []
        tmp_xml = helper.get_tmp_file_name('') + '.xml'
        with open(tmp_xml, 'wb') as cfg_file:
            cfg_file.write(req.content)
            cfg_file.close()

        try:
            xml_parse = ET.parse(tmp_xml)
            items = xml_parse.findall('.//item')
            ret = []
            for i in items:
                anime_name = i.find('./guid').text
                title = self.get_file_title(i.find('./link').text)
                logging.info('mikanani find %s', helper.format_long_string(anime_name))
                url = i.find('./enclosure').attrib['url']
                ret.append({'path': title, 'link': url, 'file_type': types.FILE_TYPE_VIDEO_TV})
            return ret
        except Exception as err:
            logging.info('parse rss xml error:%s', err)
            return []

    def update_config(self, req_para: str) -> None:
        pass

    def load_config(self) -> None:
        cfg = provider.load_source_provide_config(self.provider_name)
        logging.info('mikanani rss link is:%s', cfg['rss_link'])
        self.rss_link = cfg['rss_link']

    def get_file_title(self, link: str) -> str:
        # example: https://mikanani.me/Home/Episode/5350b283db7d8e4665a08dda24d0d0c66259fc71
        try:
            req = requests.get(link, timeout=30)
        except Exception as err:
            logging.info('mikanani get anime title error:%s', err)
            return ""
        dom = BeautifulSoup(req.content, 'html.parser')
        titles = dom.find_all('a', ['class', 'w-other-c'])
        if len(titles) == 0:
            logging.error('mikanani get anime title empty:%s', link)
            return ""
        title = titles[0].text.strip()
        logging.info('mikanani get anime title:%s', title)
        return title
