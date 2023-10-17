import queue
import time
import os
import logging
import _thread

from yt_dlp import YoutubeDL


COOKIE_FILE_PATH = '/app/config/cookies.txt'

class DownloadTask:
    def __init__(self, para: dict, count: int) -> None:
        self.para = para
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

            logging.info("Start downloading task:%s", task.para['dataSource'])
            download_opts = {
                'outtmpl': os.path.join(task.para['path'], '%(title)s.%(ext)s'),
                'noplaylist': True,
                'cookiefile': COOKIE_FILE_PATH,
            }

            if bool(task.para['autoFormatConvert']):
                # Add 'recode-video' option to recode format to MP4
                download_opts['postprocessors'] = [{
                    'key': 'FFmpegVideoConvertor',
                    'preferedformat': task.para['targetFormat']
                }]

            if task.para['downloadProxy'] != '' and \
                task.para['downloadProxy'] is not None:
                logging.info("Download with proxy:%s", task.para['downloadProxy'])
                download_opts['proxy'] = task.para['downloadProxy']

            try:
                with YoutubeDL(download_opts) as ydl:
                    ydl.download(task.para['dataSource'])
                    continue
            except Exception as err:
                logging.error("Download task(%s) error:%s", task.para['dataSource'], err)
                self.reput_task(task.para, task.fail_count + 1)

    def reput_task(self, para: dict, fail_count: int) -> None:
        if fail_count > self.fail_threshold:
            logging.error("Fail threshold reached for:%s", para['dataSource'])
            return
        self.equeue(DownloadTask(para, fail_count+1))

    def equeue(self, tasks: list) -> None:
        self.queue.put(tasks)

yt_dlp_tasks = YtDlpTasks()
