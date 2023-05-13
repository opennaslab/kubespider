# -*- coding: utf-8 -*-

"""
@author: ijwstl
@software: PyCharm
@file: config_handler.py
@time: 2023/5/13 11:45
"""
import logging
import os
import sys
import time
from pathlib import Path
import psutil
from utils.helper import Config
from watchdog.events import FileSystemEventHandler, FileModifiedEvent


class FileHandler(FileSystemEventHandler):

    last_trigger_time = time.time()

    # Ref: https://github.com/gorakhargosh/watchdog/issues/346#issuecomment-864091647
    def on_modified(self, event: FileModifiedEvent):
        current_time = time.time()
        if event.src_path.find('~') == -1 and (current_time - self.last_trigger_time) > 1:
            self.last_trigger_time = current_time
            filepath = Path(event.src_path)
            if filepath.name not in [
                Config.DOWNLOAD_PROVIDER,
                Config.SOURCE_PROVIDER,
                Config.PT_PROVIDER,
                Config.KUBESPIDER_CONFIG]:
                return
            logging.info("config file has be changed, the kubspider will reboot, %s", filepath.name)

            # Ref: https://stackoverflow.com/a/33334183
            try:
                process = psutil.Process(os.getpid())
                for handler in process.open_files() + process.connections():
                    os.close(handler.fd)
            except Exception as err:
                logging.error(err)
            python = sys.executable
            os.execl(python, python, *sys.argv)
