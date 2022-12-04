# This works for: https://mikanani.me
# Function: download anime you subscribe
import logging
from urllib.parse import urlparse

import requests
import xml.etree.cElementTree as ET

from source_provider import provider
from api import types
from utils import helper

class MikananiSourceProvider(provider.SourceProvider):
    def __init__(self) -> None:
        self.provider_type = types.SOURCE_PROVIDER_PERIOD_TYPE
        self.file_type = 'torrent'
        self.webhook_enable = True
        self.provider_name = 'mikanani_source_provider'
        self.rss_link = ''
        self.download_path = ''
        self.tmp_file_path='/tmp/'

    def should_handle(self, dataSourceUrl):
        parse_url = urlparse(dataSourceUrl)
        if parse_url.hostname == 'mikanani.me' and parse_url.path == '/RSS/MyBangumi':
            logging.info(f'{dataSourceUrl} belongs to MikananiSourceProvider')
            return True
        return False

    def is_webhook_enable(self):
        return self.webhook_enable

    def get_provider_type(self):
        return self.provider_type
    
    def get_file_type(self):
        return self.file_type

    def get_provider_name(self):
        return self.provider_name
    
    def load_config(self):
        cfg = provider.load_source_provide_config()
        logging.info(cfg.get('mikanani_source_provider', 'RSS_LINK'))
        self.rss_link = cfg.get(self.provider_name, 'RSS_LINK')
        self.download_path = cfg.get(self.provider_name, 'DOWNLOAD_PATH')

    def provider_enabled(self):
        cfg = provider.load_source_provide_config()
        return cfg.get(self.provider_name, 'ENABLE') == 'true'

    def get_links(self, dataSourceUrl):
        try:
            req = requests.get(self.rss_link)
        except:
            return []
        tmp_xml = helper.get_tmp_file_name('') + '.xml'
        with open(tmp_xml, 'wb') as f:
            f.write(req.content)
            f.close()

        xml_parse = ET.parse(tmp_xml)
        items = xml_parse.findall('.//item')
        ret = []
        for i in items:
            anime_name = i.find('./guid').text
            logging.info(f'mikanani find {anime_name}')
            url = i.find('./enclosure').attrib['url']
            ret.append(url)
        return ret

    def get_download_path(self):
        return self.download_path
