# -*- coding: utf-8 -*-

"""
@author: ijwstl
@software: PyCharm
@file: provider.py
@time: 2023/4/12 19:45
"""

import re
import logging
import feedparser
from api import types
from source_provider import provider
from utils.config_reader import AbsConfigReader
class GeneralRssSourceProvider(provider.SourceProvider):
    """
    Description: general rss source provider
    """
    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        """
        Description: init class of GeneralRssSourceProvider
                    provider_type: general_rss_source_provider
                    rss_name: a name for the configuration, just like 美剧天堂
                    rss_link：the URL of rss hub resource
                    file_type: this type is resource type
                    link_type: this type is resource url type
                    provider_listen_type: disposable or period
        Args:
            rss_config: config member of rss config, file is ./config/general_rss.json
        """
        super().__init__(config_reader)
        self.webhook_enable = False
        self.rss_name = None
        self.rss_link = None
        self.file_type = types.FILE_TYPE_COMMON
        self.link_type = types.LINK_TYPE_GENERAL
        self.provider_listen_type = types.SOURCE_PROVIDER_PERIOD_TYPE
        self.provider_type = "general_rss_source_provider"
        self.provider_name = name
        self.load_config()

    def get_provider_name(self) -> str:
        return self.provider_name

    def get_provider_type(self) -> str:
        return self.provider_type

    def get_link_type(self) -> str:
        return self.link_type

    def get_download_param(self) -> None:
        return self.config_reader.read().get('download_param')

    def get_download_provider_type(self) -> None:
        pass

    def get_prefer_download_provider(self) -> None:
        return self.config_reader.read().get('downloader')

    def get_provider_listen_type(self) -> str:
        return self.provider_listen_type

    def provider_enabled(self) -> bool:
        return self.config_reader.read().get('enable', True)

    def is_webhook_enable(self) -> bool:
        return self.webhook_enable

    def should_handle(self, data_source_url: str) -> None:
        pass

    def get_rss_link(self) -> str:
        """
        return the rss link 
        """
        return self.rss_link

    def get_links(self, data_source_url: str) -> list:
        """
        Description: get rss resource link for download
        Args:
            dataSourceUrl:
        Returns:
        """
        links = []
        rss_oschina = feedparser.parse(self.rss_link)
        if not rss_oschina.get('entries'):
            logging.warning("sorry, Not found source, please check the url of rsshub")

        for entry in rss_oschina['entries']:
            if not entry['links']:
                logging.warning("%s, No links were found to download yet ", entry['title'])
                continue
            # According to the RSS standard, media resources will be saved in the enclosure element
            # https://en.wikipedia.org/wiki/RSS_enclosure
            items = [x for x in entry['links'] if x["rel"] == "enclosure"]
            path = self.get_link_download_path(entry['title'])
            for link in items:
                url = link["href"]
                link_type = types.LINK_TYPE_GENERAL
                if url.startswith("magnet:?xt"):
                    link_type = types.LINK_TYPE_MAGNET
                elif url.endswith("torrent"):
                    link_type = types.LINK_TYPE_TORRENT
                links.append({
                    "link": url,
                    "file_type": link_type,
                    "path": path,
                })
        return links

    def get_link_download_path(self, title)->str:
        """
        get resource download path from the title
        default: rss_name
        """
        if self.title_parser is not None:
            titles = self.title_parser.findall(title)
            paths = []
            if len(titles) > 0:
                if isinstance(titles[0], (list, tuple)):
                    paths = list(titles[0]) # force tuple to list
                else:
                    paths.append(titles[0])
                # TODO: "/" to "\/" ?
                return r"/".join(paths)
        return self.rss_name

    def update_config(self, req_para: str) -> None:
        pass

    def load_config(self) -> None:
        cfg = self.config_reader.read()
        self.rss_name = cfg.get("rss_name", "")
        self.rss_link = cfg.get("rss_link")
        self.file_type = cfg.get("file_type", types.FILE_TYPE_COMMON)
        self.link_type = cfg.get("link_type", types.LINK_TYPE_GENERAL)
        title_pattern = cfg.get("title_pattern", None)
        if title_pattern is not None:
            try:
                self.title_parser = re.compile(title_pattern)
            except ValueError as err:
                logging.error("Invalid title pattern [%s]: %s", title_pattern, err)
        else:
            self.title_parser = None
