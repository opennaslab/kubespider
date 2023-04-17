import queue
import time
import json
import subprocess
import logging
import _thread

import values


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

            quality = self.get_highest_quality(download_args)
            if quality is None:
                logging.warning("No quality found for:%s", download_args[0])
                self.reput_task(original_args, fail_count)
                continue

            download_args.append(quality)
            try:
                process = subprocess.Popen(['you-get', *download_args], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
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
        return None

    def get_highest_quality(self, args: list) -> str:
        resolve_args = list(args)
        resolve_args.extend(['--json'])

        command_execute = 'you-get ' + ' '.join(resolve_args)
        try:
            result = subprocess.run(['you-get', *resolve_args], capture_output=True, check=True)
            if result.returncode != 0:
                logging.error("Resolve quality with none-zero exit:%s, execute command:%s", str(result.stdout), command_execute)
                return None
        except Exception as err:
            logging.warning("Resolve quality error:%s, execute command:%s", str(err), command_execute)
            return None

        try:
            video_list = json.loads(result.stdout)
            max_size = 0
            max_size_format = ""
            for video_format in video_list['streams'].keys():
                video = video_list['streams'][video_format]
                if 'size' not in video.keys():
                    continue
                if video['size'] > max_size:
                    max_size = video['size']
                    max_size_format = video_format

            return '--format='+max_size_format
        except Exception as err:
            logging.error("Resolve json error:%s", str(err))
            return None

    def equeue(self, tasks: list) -> None:
        self.queue.put(tasks)

you_get_tasks = YouGetTasks()
