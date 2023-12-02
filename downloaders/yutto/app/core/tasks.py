import queue
import time
import json
import subprocess
import shlex
import logging
import _thread

from core import values


BILIBILI_SESSDATA = "d8bc7493%2C2843925707%2C08c3e*81"

class DownloadTask:
    def __init__(self, args: list, count: int) -> None:
        self.download_args = args
        self.fail_count = count


class YouGetTasks:
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

            logging.info("Start downloading task:%s", task.download_args[0])
            original_args = list(task.download_args)
            download_args = task.download_args
            fail_count = task.fail_count

            config_args = self.get_authing_args(download_args[0])
            if config_args is not None:
                download_args.extend(config_args)

            download_args.extend(['--no-danmaku'])
            download_args.extend(['--no-subtitle'])

            try:
                process = subprocess.Popen(['yutto', *download_args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                # Read from the standard output and standard error streams in real time
                self.print_process(process)

                # Wait for the process to finish and get the return code
                return_code = process.wait()
                if return_code == 0:
                   logging.info("Download success for:%s", download_args[0])
                else:
                   logging.warning("Download failed for:%s", download_args[0])
                   self.reput_task(original_args, fail_count)
            except Exception as err:
                logging.error("Download failed for:%s, %s", download_args[0], str(err))
                self.reput_task(original_args, fail_count)

    def print_process(self, process: subprocess.Popen):
        time_current = int(time.time())
        for line in process.stdout:
            if int(time.time()) - time_current >= 1:
                logging.info(line.strip())
                time_current = int(time.time())

    def reput_task(self, args: list, fail_count: int) -> None:
        if fail_count > self.fail_threshold:
            logging.error("Fail threshold reached for:%s", args[0])
            return
        self.equeue(DownloadTask(args, fail_count+1))

    def get_authing_args(self, url) -> list:
        if url.startswith('https://www.bilibili.com'):
            if values.config_map['bilibili'] != "":
                return ['-c', values.config_map['bilibili']]
            return ['-c', 'BILIBILI_SESSDATA']
        return None

    def equeue(self, tasks: list) -> None:
        self.queue.put(tasks)

yutto_tasks = YouGetTasks()
