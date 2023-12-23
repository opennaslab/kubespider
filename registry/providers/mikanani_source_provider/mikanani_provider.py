# This works for: https://mikanani.me
# Function: download anime you subscribe
# encoding:utf-8
import logging

import xml.etree.ElementTree as ET
import re
from re import Pattern
from bs4 import BeautifulSoup
from kubespider_source_provider import Manager
from kubespider_source_provider.data_types import ProviderInstanceType, HttpApi, LinkType, FileType
from kubespider_source_provider.tools import format_long_string
from kubespider_source_provider.values import Resource

manager = Manager(provider_instance_type=ProviderInstanceType.single)


@manager
class MikananiSourceProvider:
    def __init__(self, name: str, rss_link: str, pattern: str = None, auto_download: bool = False, **kwargs) -> None:
        self.name = name
        self.rss_link = rss_link
        self.pattern = pattern
        self.auto_download = auto_download
        self.request_handler = kwargs.get("request_handler")()
        self.link_type = LinkType.torrent

    @manager.registry(HttpApi.schedule)
    def get_links(self) -> list[Resource]:
        try:
            content = self.request_handler.get(self.rss_link, timeout=30).text
        except Exception as err:
            logging.info('[MikananiSourceProvider:%s] get links error: %s', self.name, err)
            return []
        return self.get_links_from_xml(content, self.pattern)

    def get_links_from_xml(self, content, pattern: str) -> list[Resource]:
        if pattern is not None:
            reg = re.compile(pattern)
        else:
            reg = None
        try:
            xml_parse = ET.fromstring(content)
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
                logging.info(
                    '[MikananiSourceProvider:%s] find %s',
                    self.name, format_long_string(anime_name)
                )
                url = i.find('./enclosure').attrib['url']
                if path is not None and item_title is not None:
                    ret.append(Resource(
                        url=url,
                        path=path,
                        title=item_title,
                        file_type=FileType.tv,
                        link_type=self.link_type,
                        auto_download=self.auto_download
                    ).data)
                else:
                    logging.warning("[MikananiSourceProvider:%s] Skip %s, %s", anime_name, item_title)
            return ret
        except Exception as err:
            logging.info('[MikananiSourceProvider:%s] parse rss xml error:%s', err)
            return []

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

    def get_file_title(self, link: str) -> str:
        # example: https://mikanani.me/Home/Episode/5350b283db7d8e4665a08dda24d0d0c66259fc71
        try:
            data = self.request_handler.get(link, timeout=30).content
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


if __name__ == '__main__':
    manager.run()
