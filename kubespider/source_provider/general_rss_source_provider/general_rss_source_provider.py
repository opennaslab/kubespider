# -*- coding: utf-8 -*-

"""
@author: ijwstl
@software: PyCharm
@file: general_rss_source_provider.py
@time: 2023/4/12 19:45
"""

from source_provider import provider
import feedparser
import logging
from api import types


class GeneralRssSourceProvider(provider.SourceProvider):
    def __init__(self, rss_config) -> None:
        """
        Description: init class of GeneralRssSourceProvider
                    id: Unique identification of rss config
                    provider_type: disposable or period
                    rss_name: a name for the configuration, just like 美剧天堂
                    rss_hub_link：the URL of rss hub resource
                    webhook_enable: cannot be triggered by request
                    provider_enabled: open/close -> True/False
                    rss_tpye: this type is used to categorize the rss later in web
                    file_type: this type is resource type
                    link_type: this type is resource url type
                    decs: this is description of rss
                    exec_time: is used to exec timed tasks
                    check_time: is used to exec timed tasks
                    provider_name: provider_name

        Args:
            rss_config: config member of rss config, file is ./config/general_rss.json
        """
        self.id = rss_config.get("id")
        self.provider_type = rss_config.get("provider_type")
        self.rss_name = rss_config.get("rss_name")
        self.rss_hub_link = rss_config.get("rss_url")
        self.webhook_enable = False
        self.provider_enabled = True if rss_config.get("provider_enabled") == "open" else False
        self.rss_tpye = rss_config.get("type")
        self.file_type = rss_config.get("flag") if rss_config.get("flag") in types.file_type_to_path.keys() else types.FILE_TYPE_COMMON
        self.link_type = types.LINK_TYPE_MAGNET
        self.decs = rss_config.get("decs")
        self.exec_time = rss_config.get("exec_time")
        self.check_time = rss_config.get("check_time")
        self.provider_name = 'general_rss_source_provide'

    def get_provider_name(self):
        return self.provider_name

    def get_provider_type(self):
        return None

    def get_file_type(self):
        return self.file_type

    def get_download_provider(self):
        return None

    def get_link_type(self):
        return None

    def get_download_path(self):
        return self.download_path

    def provider_enabled(self):
        return self.provider_enabled

    def is_webhook_enable(self):
        return self.is_webhook_enable

    def should_handle(self, dataSourceUrl):
        pass

    def get_links(self, dataSourceUrl=""):
        """
        Description: get rss resource link for download

        Args:
            dataSourceUrl:

        Returns:

        """
        links = []
        rss_oschina = feedparser.parse(self.rss_hub_link)
        if rss_oschina.get('entries'):
            logging.warning("sorry, Not found source, please check the url of rsshub")

        for entry in rss_oschina['entries']:
            if not entry['links']:
                logging.warning("{}, No links were found to download yet ".format(entry['title']))
                continue
            link_exist = False
            for link_info in entry['links']:
                if link_info["type"] == "application/x-bittorrent" or link_info["href"].startswith("magnet:?xt"):
                    link_exist = True
                    links.append({"link": link_info["href"], "file_type": self.file_type, "path": "/"}, )
                    break
            if not link_exist:
                logging.warning("{}, No magnetic links were found to download yet".format(entry['title']))
        return links

    def update_config(self, reqPara):
        pass

    def load_config(self):
        pass

    def get_config(self):
        return {
            "id": self.id,
            "rss_name": self.rss_name,
            "rss_url": self.rss_hub_link,
            "type": self.rss_tpye,
            "provider_enabled": self.provider_enabled,
            "decs": self.decs,
            "provider_type": self.provider_type,
            "exec_time": self.exec_time,
            "check_time": self.check_time
        }

    def get_close_config(self):
        return {
            "id": self.id,
            "rss_name": self.rss_name,
            "rss_url": self.rss_hub_link,
            "type": self.rss_tpye,
            "provider_enabled": "close",
            "decs": self.decs,
            "provider_type": self.provider_type,
            "exec_time": self.exec_time,
            "check_time": self.check_time
        }

    def get_next_config(self):
        return {
            "id": self.id,
            "rss_name": self.rss_name,
            "rss_url": self.rss_hub_link,
            "type": self.rss_tpye,
            "provider_enabled": self.provider_enabled,
            "decs": self.decs,
            "provider_type": self.provider_type,
            "exec_time": self.exec_time,
            "check_time": self.check_time + 1
        }