import queue
import time
import os
import logging
import _thread

from yt_dlp import YoutubeDL

import values


class DownloadTask:
    def __init__(self, url: str, path: str, count: int) -> None:
        self.path = path
        self.url = url
        self.fail_count = count


class YtDlpTasks:
    def __init__(self) -> None:
        self.paralel_num = 4
        self.fail_threshold = 3
        self.queue = queue.Queue()

    def run(self) -> None:
        for _ in range(self.paralel_num):
            _thread.start_new_thread(self.handle_tasks, ())
        while True:
            time.sleep(1)

    def handle_tasks(self) -> None:
        while True:
            time.sleep(1)

            task = self.queue.get()
            if task is None:
                continue

            logging.info("Start downloading task:%s", task.url)
            download_opts = {
                'outtmpl': os.path.join(task.path, '%(title)s.%(ext)s'),
                'noplaylist': True,
            }
            proxy = self.get_proxy()
            if proxy != '':
                download_opts['proxy'] = proxy

            try:
                with YoutubeDL(download_opts) as ydl:
                    ydl.download(task.url)
                    continue
            except Exception as err:
                logging.error("Download task(%s) error:%s", task.url, err)
                self.reput_task(task.url, task.path, task.fail_count + 1)

    def get_proxy(self) -> str:
        return values.config_map['youtube_proxy']

    def reput_task(self, url: str, path: str, fail_count: int) -> None:
        if fail_count > self.fail_threshold:
            logging.error("Fail threshold reached for:%s", url)
            return
        self.equeue(DownloadTask(url, path, fail_count+1))

    def equeue(self, tasks: list) -> None:
        self.queue.put(tasks)

yt_dlp_tasks = YtDlpTasks()
