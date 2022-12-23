# This works for: https://mikanani.me
# Function: download anime you subscribe
import logging

import xml.etree.ElementTree as ET
import requests

from source_provider import provider
from api import types
from utils import helper


class MikananiSourceProvider(provider.SourceProvider):
    def __init__(self) -> None:
        self.provider_type = types.SOURCE_PROVIDER_PERIOD_TYPE
        self.file_type = 'torrent'
        self.webhook_enable = False
        self.provider_name = 'mikanani_source_provider'
        self.rss_link = ''
        self.download_path = ''
        self.tmp_file_path = '/tmp/'

    def get_provider_name(self):
        return self.provider_name

    def get_provider_type(self):
        return self.provider_type

    def get_file_type(self):
        return self.file_type

    def get_download_path(self):
        return self.download_path

    def provider_enabled(self):
        cfg = provider.load_source_provide_config(self.provider_name)
        return cfg['ENABLE'] == 'true'

    def is_webhook_enable(self):
        return self.webhook_enable

    def should_handle(self, data_source_url: str):
        return False

    def get_links(self, data_source_url: str):
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
                logging.info('mikanani find %s', anime_name)
                url = i.find('./enclosure').attrib['url']
                ret.append(url)
            return ret
        except Exception as err:
            logging.info('parse rss xml error:%s', err)
            return []

    def update_config(self, req_para: str):
        pass

    def load_config(self):
        cfg = provider.load_source_provide_config(self.provider_name)
        logging.info('mikanani rss link is:%s', cfg['RSS_LINK'])
        self.rss_link = cfg['RSS_LINK']
        self.download_path = cfg['DOWNLOAD_PATH']
