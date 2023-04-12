# -*- coding: utf-8 -*-

"""
@author: ijwstl
@software: PyCharm
@file: general_period_server.py
@time: 2023/4/12 20:33
"""
import json
import logging
import os
import sys

from source_provider.general_rss_source_provider.general_rss_source_provider import GeneralRssSourceProvider
from core.kubespider_flask.controller.kubespider_controller.kubespider_server import download_links_with_provider

config_file_path = os.path.join(os.path.dirname(os.path.dirname(sys.argv[0])), ".config/general_rss.json")


def rss_period_server(rss_config):
    general_rss_source_provider = GeneralRssSourceProvider(rss_config)
    if general_rss_source_provider.rss_name == "test":
        return
    if not general_rss_source_provider.provider_enabled:
        return general_rss_source_provider.get_config()
    if general_rss_source_provider.provider_type == "disposable":
        download_links_with_provider("", general_rss_source_provider)
        return general_rss_source_provider.get_close_config()


def main_rss_period_server():
    if not os.path.exists(config_file_path):
        logging.error("rss config file error")
        return
    config_list = []
    with open(config_file_path, "r") as file:
        try:
            rss_configs = json.load(file)
        except Exception:
            logging.error("rss config file error")

    for rss_config in rss_configs.get("rss"):
        config_list.append(rss_period_server(rss_config))

    with open(config_file_path, "w") as file:
        try:
            json.dump({"rss": config_list}, file, indent=4, ensure_ascii=False)
        except Exception:
            logging.error("rss config file error")
