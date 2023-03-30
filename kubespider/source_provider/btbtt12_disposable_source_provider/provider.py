# This works for: https://www.btbtt12.com
# Function: download single video link
# encoding:utf-8
import logging
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from source_provider import provider
from api import types


class Btbtt12DisposableSourceProvider(provider.SourceProvider):
    def __init__(self) -> None:
        self.provider_type = types.SOURCE_PROVIDER_DISPOSABLE_TYPE
        self.link_type = types.LINK_TYPE_TORRENT
        self.webhook_enable = True
        self.provider_name = 'btbtt12_disposable_source_provider'

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
        parse_url = urlparse(data_source_url)
        if parse_url.hostname == 'www.btbtt12.com' and 'attach-dialog-fid' in parse_url.path:
            logging.info('%s belongs to Btbtt12DisposableSourceProvider', data_source_url)
            return True
        return False

    def get_links(self, data_source_url: str) -> dict:
        parse_url = urlparse(data_source_url)
        rep_path = str.split(parse_url.path, '-')
        rep_path[1] = 'download'
        rep_path = '-'.join(rep_path)
        ret = parse_url.scheme + '://' + parse_url.netloc + rep_path
        logging.info('btbtt12_disposable_source_provider parse %s as %s', data_source_url, ret)
        file_type, title = self.get_file_type_and_title(data_source_url)
        if file_type == "" or title == "":
            return []
        return [{'path': title, 'link': ret, 'file_type': file_type}]

    def update_config(self, req_para: str) -> None:
        pass

    def load_config(self) -> None:
        pass

    def get_file_type_and_title(self, data_source_url: str) -> tuple[str, str]:
        try:
            req = requests.get(data_source_url, timeout=30)
        except Exception as err:
            logging.error('meijutt_source_provider get video title/type error:%s', err)
            return "", ""

        dom = BeautifulSoup(req.content, 'html.parser')
        ahrefs = dom.find_all('a', ['class', 'checked'])
        if len(ahrefs) == 0:
            logging.error('btbtt12_disposable_source_provider get video type empty:%s', data_source_url)
            return "", ""

        titles = dom.find_all('dd')
        if len(titles) == 0:
            logging.error('btbtt12_disposable_source_provider get video title empty')
            return "", ""
        title = titles[0].text.strip().replace('.torrent', '')

        if ahrefs[0].text.strip() == '剧集' or \
            ahrefs[0].text.strip() == '高清剧集' or \
                ahrefs[0].text.strip() == '动漫':
            return types.FILE_TYPE_VIDEO_TV, title

        if ahrefs[0].text.strip() == '电影' or ahrefs[0].text.strip() == '高清电影':
            return types.FILE_TYPE_VIDEO_MOVIE, title

        return "", ""
