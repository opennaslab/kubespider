import queue
import time
import subprocess
import logging
import _thread

from core import values


class YouGetTasks:
    def __init__(self) -> None:
        self.paralel_num = 4
        self.queue = queue.Queue()

    def run(self) -> None:
        for _ in range(self.paralel_num):
            _thread.start_new_thread(self.handle_tasks, ())
        while True:
            time.sleep(1)

    def handle_tasks(self) -> None:
        while True:
            args = self.queue.get()
            if args is None:
                continue

            cookie_path = self.get_cookie_path(args[0])
            if cookie_path is not None:
                args.append('-c')
                args.append(cookie_path)

            quality = self.get_highest_quality(args)
            if quality is None:
                logging.warning("No quality found for:%s", args[0])
                continue

            args.append(quality)
            logging.info("Start downloading file:%s", args[0])
            result = subprocess.run(['you-get', *args], capture_output=True, check=True)

            if result.returncode == 0:
                logging.info("Download success for:%s", args[0])
            else:
                logging.warning("Download failed for:%s, %s", args[0], str(result.stderr))

            time.sleep(1)

    def get_cookie_path(self, url) -> str:
        if url.startswith('https://www.bilibili.com'):
            return values.cookie_map['bilibili']
        return None

    def get_highest_quality(self, args) -> str:
        resolve_args = ['-i']
        resolve_args.extend(args)
        result = subprocess.run(['you-get', *resolve_args], capture_output=True, check=True)
        out = str(result.stdout)
        if '1080P' in out:
            return '--format=dash-flv'
        if '720P' in out:
            return '--format=dash-flv720'
        if '480P' in out:
            return '--format=dash-flv480'
        if '360P' in out:
            return '--format=dash-flv360'
        return None

    def equeue(self, tasks: list) -> None:
        self.queue.put(tasks)

you_get_tasks = YouGetTasks()
