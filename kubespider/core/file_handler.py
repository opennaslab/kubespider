# -*- coding: utf-8 -*-

"""
@author: ijwstl
@software: PyCharm
@file: file_handler.py
@time: 2023/5/13 0:37
"""
import logging
import os
from watchdog.events import FileSystemEventHandler


class FileHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if str(event.src_path).endswith("state.yaml") or str(event.src_path).endswith(".config"):
            return
        logging.info("文件被修改了,{}".format(event.src_path))
        os.system("python3 {}".format(os.path.join(os.getenv('HOME'), 'start.sh')))
