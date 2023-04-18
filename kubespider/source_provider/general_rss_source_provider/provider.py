# -*- coding: utf-8 -*-

"""
@author: ijwstl
@software: PyCharm
@file: provider.py
@time: 2023/4/12 19:45
"""

import logging
import feedparser
from api import types
from source_provider import provider

class GeneralRssSourceProvider(provider.SourceProvider):
    """
    Description: general rss source provider
    """
    def __init__(self, name) -> None:
        """
        Description: init class of GeneralRssSourceProvider
                    provider_type: general_rss_source_provider
                    rss_name: a name for the configuration, just like 美剧天堂
                    rss_link：the URL of rss hub resource
                    webhook_enable: cannot be triggered by request
                    rss_tpye: this type is used to categorize the rss later in web
                    file_type: this type is resource type
                    link_type: this type is resource url type
                    provider_listen_type: disposable or period
                    decs: this is description of rss
                    exec_time: is used to exec timed tasks
                    check_time: is used to exec timed tasks
                    provider_name: provider_name of config
        Args:
            rss_config: config member of rss config, file is ./config/general_rss.json
        """
        self.rss_name = None
        self.rss_link = None
        self.webhook_enable = False
        self.rss_tpye = None
        self.file_type = None
        self.link_type = types.LINK_TYPE_MAGNET
        self.provider_listen_type = types.SOURCE_PROVIDER_PERIOD_TYPE
        self.decs = None
        self.exec_time = None
        self.check_time = None
        self.provider_type = "general_rss_source_provider"
        self.provider_name = name
        self.load_config()

    def get_provider_name(self) -> str:
        return self.provider_name

    def get_provider_type(self) -> str:
        return self.provider_type

    def get_file_type(self) -> str:
        return self.file_type

    def get_download_provider(self) -> None:
        return None

    def get_link_type(self) -> str:
        return self.link_type

    def get_download_path(self) -> None:
        pass

    def get_download_param(self) -> None:
        pass

    def get_download_provider_type(self) -> None:
        pass

    def get_prefer_download_provider(self) -> None:
        pass

    def get_provider_listen_type(self) -> str:
        return self.provider_listen_type

    def provider_enabled(self) -> bool:
        cfg = provider.load_source_provide_config(self.provider_name)
        return cfg.get('enable', True)

    def is_webhook_enable(self) -> bool:
        return self.webhook_enable

    def should_handle(self, data_source_url: str) -> None:
        pass

    def get_rss_link(self) -> str:
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
        if rss_oschina.get('entries'):
            logging.warning("sorry, Not found source, please check the url of rsshub")

        for entry in rss_oschina['entries']:
            if not entry['links']:
                logging.warning("%s, No links were found to download yet ", entry['title'])
                continue
            link_exist = False
            for link_info in entry['links']:
                if link_info["type"] == "application/x-bittorrent" or link_info["href"].startswith("magnet:?xt"):
                    link_exist = True
                    links.append({"link": link_info["href"], "file_type": self.file_type, "path": "/"}, )
                    break
            if not link_exist:
                logging.warning("%s, No magnetic links were found to download yet", entry['title'])
        return links

    def update_config(self, req_para: str) -> None:
        pass

    def load_config(self) -> None:
        cfg = provider.load_source_provide_config(self.provider_name)
        self.rss_name = cfg.get("rss_name")
        self.rss_link = cfg.get("rss_link")
        self.rss_tpye = cfg.get("rss_type")
        self.file_type = cfg.get("flag") if cfg.get(
            "flag") in types.file_type_to_path.keys() else types.FILE_TYPE_COMMON
        self.decs = cfg.get("decs")
        self.exec_time = cfg.get("exec_time")
        self.check_time = cfg.get("check_time")
