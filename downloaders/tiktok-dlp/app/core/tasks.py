import queue
import time
import logging
import _thread

from apiproxy.douyin.douyin import Douyin
from apiproxy.douyin.download import Download
from apiproxy.douyin import douyin_headers


class DownloadTask:
    def __init__(self, para: dict, count: int) -> None:
        self.para = para
        self.fail_count = count


class TiktokDlpTasks:
    def __init__(self) -> None:
        self.paralel_num = 4
        self.fail_threshold = 3
        self.queue = queue.Queue()
        self.download = Download(music=False, cover=False,
                                 avatar=False, resjson=False,
                                 folderstyle=False)
        self.api = Douyin()

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
            if task.para.get('cookie') is not None and task.para['cookie'] != "":
                douyin_headers["Cookie"] = task.para['cookie']
            try:
                url = self.api.getShareLink(task.para['dataSource'])
                key_type, key = self.api.getKey(url)
                if key_type == "aweme":
                    data, _ = self.api.getAwemeInfo(aweme_id=key)
                    if data is not None and data != {}:
                        datalist = [data]
                        logging.info("Download task(%s) saved to %s", task.para['dataSource'], task.para['path'])
                        self.download.userDownload(awemeList=datalist, savePath=task.para['path'])
            except Exception as err:
                logging.error("Download task(%s) error:%s", task.para['dataSource'], err)
                self.re_input_task(task.para, task.fail_count + 1)

    def re_input_task(self, para: dict, fail_count: int) -> None:
        if fail_count > self.fail_threshold:
            logging.error("Fail threshold reached for:%s", para['dataSource'])
            return
        self.equeue([DownloadTask(para, fail_count + 1)])

    def equeue(self, tasks: list) -> None:
        self.queue.put(tasks)


tiktok_dlp_tasks = TiktokDlpTasks()
