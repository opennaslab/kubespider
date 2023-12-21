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

from utils import helper, values
from utils.values import Config


class ConfigHandler(FileSystemEventHandler):

    def __init__(self, run):
        self.run = run
        self.p_run = Process(target=run)
        self.p_run.start()

    def on_modified(self, event: FileModifiedEvent):
        filepath = os.path.basename(event.src_path)

        monitor_files = [
            str(Config.KUBESPIDER_CONFIG),
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


def prepare_config() -> None:
    miss_cfg = []
    confs = [
        values.Config.KUBESPIDER_CONFIG,
        values.Config.DEPENDENCIES_CONFIG,
        values.Config.SOURCE_PROVIDERS_BIN,
        values.Config.SOURCE_PROVIDERS_CONF,
        values.Config.DOWNLOAD_PROVIDERS_CONF,
        values.Config.NOTIFICATION_PROVIDERS_CONF,
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
            print(err)
            raise Exception(str('failed to copy %s to %s:%s', template_cfg, target_cfg)) from err

