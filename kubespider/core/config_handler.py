# -*- coding: utf-8 -*-

"""
@author: ijwstl
@software: PyCharm
@file: config_handler.py
@time: 2023/5/18 21:14
"""

import logging
import os
import shutil

from utils.values import Config
from utils.config_reader import YamlFileSectionConfigReader, YamlFileConfigReader
from utils import helper, values

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


def get_source_provider(provider_name: str, config: dict):
    provider_type = config['type']
    try:
        return source_provider_init_func[provider_type](provider_name, YamlFileSectionConfigReader(
            Config.SOURCE_PROVIDER.config_path(), provider_name))
    except Exception as exc:
        raise Exception(str('unknown source provider type %s', provider_type)) from exc


def init_source_config():
    init_source_providers = []
    source_config = YamlFileConfigReader(values.Config.SOURCE_PROVIDER.config_path()).read()
    for name in source_config:
        init_source_providers.append(get_source_provider(name, source_config[name]))
    return init_source_providers


def prepare_config() -> None:
    # check configs
    miss_cfg = []
    confs = [
        values.Config.KUBESPIDER_CONFIG,
        values.Config.DEPENDENCIES_CONFIG,
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
