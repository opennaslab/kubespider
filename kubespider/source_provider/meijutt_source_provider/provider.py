# This works for: https://www.meijutt.tv/
# Function: download tv video once it's updated
from urllib.parse import urlparse
import requests
from bs4 import BeautifulSoup

import logging
from api import types
from source_provider import provider


class MeijuttSourceProvider(provider.SourceProvider):
    def __init__(self) -> None:
        self.provider_type = types.SOURCE_PROVIDER_PERIOD_TYPE
        self.file_type = 'magnet'
        self.webhook_enable = True
        self.provider_name = 'meijutt_source_provider'
        self.download_path = ''
        self.tv_links = []
    
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
        return True

    def should_handle(self, data_source_url: str):
        parse_url = urlparse(data_source_url)
        if parse_url.hostname == 'www.meijutt.tv' and 'content' in parse_url.path:
            logging.info('%s belongs to MeijuttSourceProvider', data_source_url)
            return True
        return False
    
    def get_links(self, data_source_url: str):
        ret = []
        for tv_link in self.tv_links:
            if len(tv_link) == 0:
                continue
            try:
                req = requests.get(tv_link)
            except Exception as err:
                logging.info('meijutt_source_provider get links error:%s', err)
                continue
            dom = BeautifulSoup(req.content, 'html.parser')
            div = dom.find_all("div", ['class', 'tabs-list current-tab'])
            if len(div) == 0:
                continue
            links = div[0].find_all('input', ['class', 'down_url'])
            for link in links:
                url = link.get('value')
                logging.info('meijutt find %s', url)
                ret.append(url)
        return ret

    def update_config(self, req_para: str):
        cfg = provider.load_source_provide_config(self.provider_name)
        links = cfg['TV_LINKS']
        links = str.split(links, ',')
        if req_para not in links:
            links.append(req_para)
        links = ','.join(links)
        cfg['TV_LINKS'] = links
        provider.save_source_provider_config(self.provider_name, cfg)

    def load_config(self):
        cfg = provider.load_source_provide_config(self.provider_name)
        logging.info('meijutt tv link is:' + cfg['TV_LINKS'])
        self.tv_links = str.split(cfg['TV_LINKS'], ',')
        self.download_path = cfg['DOWNLOAD_PATH']