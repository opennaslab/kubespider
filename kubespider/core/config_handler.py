# -*- coding: utf-8 -*-

"""
@author: ijwstl
@software: PyCharm
@file: config_handler.py
@time: 2023/5/18 21:14
"""

import logging
import os
from multiprocessing import Process
from watchdog.events import FileSystemEventHandler, FileModifiedEvent
from api.values import Config

class ConfigHandler(FileSystemEventHandler):

    def __init__(self, run):
        self.run = run
        self.p_run = Process(target=run)
        self.p_run.start()

    def on_modified(self,  event: FileModifiedEvent):
        filepath = os.path.basename(event.src_path)
        if filepath not in [i.value for i in Config.__members__.values() if i.value != "state.yaml"]:
            return
        logging.info("%s file has be changed, the kubspider will reboot", event.src_path)
        self.p_run.terminate()

        if self.p_run.is_alive():
            self.p_run.kill()

        new_p_run = Process(target=self.run)
        new_p_run.start()
        self.p_run = new_p_run
