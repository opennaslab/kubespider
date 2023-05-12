# -*- coding: utf-8 -*-

"""
@author: ijwstl
@software: PyCharm
@file: config_handler.py
@time: 2023/5/13 11:45
"""
import logging
import os
import signal
from watchdog.events import FileSystemEventHandler


class FileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if str(event.src_path).endswith("state.yaml") or str(event.src_path).endswith(".config"):
            return
        logging.info("config file has be changed, the kubspider will reboot, %s", event.src_path)
        os.kill(os.getpid(), signal.SIGKILL)
