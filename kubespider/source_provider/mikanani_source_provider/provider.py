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
        self.webhook_enable = False
        self.provider_name = 'mikanani_source_provider'
        self.rss_link = ''
        self.download_path = ''
        self.tmp_file_path='/tmp/'

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

    def should_handle(self, dataSourceUrl):
        return False
    
    def get_links(self, dataSourceUrl):
        try:
            req = requests.get(self.rss_link)
        except Exception as e:
            logging.info(f'mikanani get links error:{str(e)}')
            return []
        tmp_xml = helper.get_tmp_file_name('') + '.xml'
        with open(tmp_xml, 'wb') as f:
            f.write(req.content)
            f.close()

        try:
            xml_parse = ET.parse(tmp_xml)
            items = xml_parse.findall('.//item')
            ret = []
            for i in items:
                anime_name = i.find('./guid').text
                logging.info(f'mikanani find {anime_name}')
                url = i.find('./enclosure').attrib['url']
                ret.append(url)
            return ret
        except Exception as e:
            logging.info(f'parse rss xml error:{str(e)}')
            return []

    def update_config(self, reqPara):
        pass

    def load_config(self):
        cfg = provider.load_source_provide_config(self.provider_name)
        logging.info('mikanani rss link is:' + cfg['RSS_LINK'])
        self.rss_link = cfg['RSS_LINK']
        self.download_path = cfg['DOWNLOAD_PATH']