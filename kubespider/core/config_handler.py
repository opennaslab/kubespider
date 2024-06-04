# -*- coding: utf-8 -*-

"""
@author: ijwstl
@software: PyCharm
@file: config_handler.py
@time: 2023/5/18 21:14
"""

import logging
import os
import time
from multiprocessing import Process
import shutil
from watchdog.events import FileSystemEventHandler, FileModifiedEvent

from api.values import Config
from api import values
from utils.config_reader import YamlFileSectionConfigReader, YamlFileConfigReader
from utils import helper

import source_provider.mikanani_source_provider.provider as mikanani_source_provider
import source_provider.btbtt12_disposable_source_provider.provider as btbtt12_disposable_source_provider
import source_provider.meijutt_source_provider.provider as meijutt_source_provider
import source_provider.bilibili_source_provider.provider as bilibili_source_provider
import source_provider.youtube_source_provider.provider as youtube_source_provider
import source_provider.general_rss_source_provider.provider as general_rss_source_provider
import source_provider.magic_source_provider.provider as magic_source_provider
import source_provider.tiktok_source_provider.provider as tiktok_source_provider
import source_provider.bilibili_vlogger_subscribe_source_provider.provider as bilibili_vlogger_subscribe_source_provider
import source_provider.alist_source_provider.provider as alist_source_provider
import source_provider.ani_source_provider.provider as ani_source_provider
import download_provider.aria2_download_provider.provider as aria2_download_provider
import download_provider.xunlei_download_provider.provider as xunlei_download_provider
import download_provider.qbittorrent_download_provider.provider as qbittorrent_download_provider
import download_provider.youget_download_provider.provider as youget_download_provider
import download_provider.ytdlp_download_provider.provider as ytdlp_download_provider
import download_provider.transmission_download_provider.provider as transmission_download_provider
import download_provider.tiktok_dlp_download_provider.provider as tiktok_dlp_download_provider
import download_provider.yutto_download_provider.provider as yutto_download_provider

import pt_provider.nexusphp_pt_provider.provider as nexusphp_pt_provider

import notification_provider.pushdeer_notification_provider.provider as pushdeer_notification_provider
import notification_provider.telegram_notification_provider.provider as telegram_notification_provider
import notification_provider.qq_notification_provider.provider as qq_notification_provider
import notification_provider.bark_notification_provider.provider as bark_notification_provider
import notification_provider.slack_notification_provider.provider as slack_notification_provider

# Source provider init related
source_provider_init_func = {
    'bilibili_source_provider': bilibili_source_provider.BilibiliSourceProvider,
    'btbtt12_disposable_source_provider': btbtt12_disposable_source_provider.Btbtt12DisposableSourceProvider,
    'meijutt_source_provider': meijutt_source_provider.MeijuttSourceProvider,
    'mikanani_source_provider': mikanani_source_provider.MikananiSourceProvider,
    'youtube_source_provider': youtube_source_provider.YouTubeSourceProvider,
    'general_rss_source_provider': general_rss_source_provider.GeneralRssSourceProvider,
    'magic_source_provider': magic_source_provider.MagicSourceProvider,
    'tiktok_source_provider': tiktok_source_provider.TiktokSourceProvider,
    'bilibili_vlogger_subscribe_source_provider': bilibili_vlogger_subscribe_source_provider.BilibiliVloggerSubscribeSourceProvider,
    'alist_source_provider': alist_source_provider.AlistSourceProvider,
    'ani_source_provider': ani_source_provider.AniSourceProvider,
}

# Download provider init related
downloader_provider_init_func = {
    'aria2_download_provider': aria2_download_provider.Aria2DownloadProvider,
    'qbittorrent_download_provider': qbittorrent_download_provider.QbittorrentDownloadProvider,
    'xunlei_download_provider': xunlei_download_provider.XunleiDownloadProvider,
    'youget_download_provider': youget_download_provider.YougetDownloadProvider,
    'ytdlp_download_provider': ytdlp_download_provider.YTDlpDownloadProvider,
    'transmission_download_provider': transmission_download_provider.TransmissionProvider,
    'tiktok_download_provider': tiktok_dlp_download_provider.TiktokDownloadProvider,
    'yutto_download_provider': yutto_download_provider.YuttoDownloadProvider,
}

# PT provider init related
pt_provider_init_func = {
    'nexusphp_pt_provider': nexusphp_pt_provider.NexuPHPPTProvider,
}

notification_provider_init_func = {
    'pushdeer_notification_provider': pushdeer_notification_provider.PushDeerNotificationProvider,
    'telegram_notification_provider': telegram_notification_provider.TelegramNotificationProvider,
    'qq_notification_provider': qq_notification_provider.QQNotificationProvider,
    'bark_notification_provider': bark_notification_provider.BarkNotificationProvider,
    'slack_notification_provider': slack_notification_provider.SlackNotificationProvider
}


class ConfigHandler(FileSystemEventHandler):

    def __init__(self, run):
        self.run = run
        self.p_run = Process(target=run)
        self.p_run.start()

    def on_modified(self, event: FileModifiedEvent):
        filepath = os.path.basename(event.src_path)

        monitor_files = [
            str(Config.DOWNLOAD_PROVIDER),
            str(Config.KUBESPIDER_CONFIG),
            str(Config.PT_PROVIDER),
            str(Config.SOURCE_PROVIDER),
            str(Config.NOTIFICATION_PROVIDER),
        ]
        if filepath not in monitor_files:
            return
        logging.info("%s file has be changed, the kubespider will reboot", event.src_path)

        # wait some file handling process finish, to avoid config getting empty
        time.sleep(3)
        self.p_run.terminate()

        if self.p_run.is_alive():
            self.p_run.kill()

        new_p_run = Process(target=self.run)
        new_p_run.start()
        self.p_run = new_p_run


def get_source_provider(provider_name: str, config: dict):
    provider_type = config['type']
    try:
        return source_provider_init_func[provider_type](provider_name, YamlFileSectionConfigReader(
            Config.SOURCE_PROVIDER.config_path(), provider_name))
    except Exception as exc:
        raise Exception(str('unknown source provider type %s', provider_type)) from exc


def get_download_provider(provider_name: str, config: dict):
    provider_type = config['type']
    try:
        return downloader_provider_init_func[provider_type](provider_name, YamlFileSectionConfigReader(
            Config.DOWNLOAD_PROVIDER.config_path(), provider_name))
    except Exception as exc:
        raise Exception(str('unknown download provider type %s', provider_type)) from exc


def get_pt_provider(provider_name: str, config: dict):
    provider_type = config['type']
    try:
        return pt_provider_init_func[provider_type](provider_name,
                                                    YamlFileSectionConfigReader(Config.PT_PROVIDER.config_path(),
                                                                                provider_name))
    except Exception as exc:
        raise Exception(str('unknown pt provider type %s', provider_type)) from exc


def get_notification_provider(provider_name: str, config: dict):
    provider_type = config['type']
    try:
        return notification_provider_init_func[provider_type](
            provider_name,
            YamlFileSectionConfigReader(Config.NOTIFICATION_PROVIDER.config_path(), provider_name)
        )
    except Exception as exc:
        raise Exception(str('unknown notification provider type %s', provider_type)) from exc


def init_source_config():
    init_source_providers = []
    source_config = YamlFileConfigReader(values.Config.SOURCE_PROVIDER.config_path()).read()
    for name in source_config:
        init_source_providers.append(get_source_provider(name, source_config[name]))
    return init_source_providers


def init_download_config():
    init_download_providers = []
    download_config = YamlFileConfigReader(values.Config.DOWNLOAD_PROVIDER.config_path()).read()
    for name in download_config:
        init_download_providers.append(get_download_provider(name, download_config[name]))
    return init_download_providers


def init_pt_config():
    init_pt_providers = []
    pt_config = YamlFileConfigReader(values.Config.PT_PROVIDER.config_path()).read()
    for name in pt_config:
        init_pt_providers.append(get_pt_provider(name, pt_config[name]))
    return init_pt_providers


def init_notification_config():
    init_notification_providers = []
    notification_config = YamlFileConfigReader(values.Config.NOTIFICATION_PROVIDER.config_path()).read()
    for name, conf in notification_config.items():
        init_notification_providers.append(get_notification_provider(name, conf))
    return init_notification_providers


def prepare_config() -> None:
    miss_cfg = []
    confs = [
        values.Config.SOURCE_PROVIDER,
        values.Config.DOWNLOAD_PROVIDER,
        values.Config.PT_PROVIDER,
        values.Config.KUBESPIDER_CONFIG,
        values.Config.DEPENDENCIES_CONFIG,
        values.Config.NOTIFICATION_PROVIDER
    ]
    for conf in confs:
        if not os.path.exists(conf.config_path()):
            miss_cfg.append(conf)
    if len(miss_cfg) == 0:
        return

    logging.info("Config files(%s) miss, try to init them", ','.join(miss_cfg))

    # local run, make sure the current working directory like this {repo_root}/kubespider/kubespider
    if not helper.is_running_in_docker():
        if not os.path.exists(values.CFG_BASE_PATH):
            os.makedirs(values.CFG_BASE_PATH)
        values.CFG_TEMPLATE_PATH = os.path.join(os.path.dirname(os.getcwd()), '.config/')

    for cfg in miss_cfg:
        template_cfg = values.CFG_TEMPLATE_PATH + cfg
        target_cfg = values.CFG_BASE_PATH + cfg
        try:
            if os.path.isdir(template_cfg):
                shutil.copytree(template_cfg, target_cfg)
            else:
                shutil.copy(template_cfg, target_cfg)
        except Exception as err:
            raise Exception(str('failed to copy %s to %s:%s', template_cfg, target_cfg)) from err
