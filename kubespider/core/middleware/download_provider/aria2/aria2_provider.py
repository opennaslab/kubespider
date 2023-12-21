import inspect
import logging
import traceback

import aria2p
from core.exceptions import UnSupportedMethod
from core.middleware.download_provider.provider import DownloadProvider
from utils.types import DownloadStates
from utils.values import DownloadTask


class Aria2Provider(DownloadProvider):
    """An open-source download tool aria2"""

    def __init__(self, name: str, host: str, port: int, secret: str):
        """
        :param name: provider instance name
        :param host: aria2`s host
        :param port: aria2`s port
        :param secret: aria2`s secret token
        """
        self.name = name
        self.host = host
        self.port = port
        self.secret = secret
        self.instance = self.load_instance()

    def load_instance(self):
        return aria2p.API(aria2p.Client(host=self.host, port=self.port, secret=self.secret))

    def is_alive(self) -> bool:
        try:
            self.instance.get_global_options()
            return True
        except Exception as err:
            logging.error("[%s] connect failed: %s", self.name, err)
            return False

    def global_rate_limit(self, download: int, upload: int = None) -> bool:
        try:
            options = {
                'max-overall-download-limit': f"{download}",
            }
            if upload:
                options['max-overall-upload-limit'] = f"{upload}"
            return self.instance.set_global_options(options)
        except Exception as err:
            logging.error("[%s] global rate limit set failed: %s", self.name, err)
            return False

    def cancel_rate_limit(self) -> bool:
        try:
            options = {
                'max-overall-download-limit': "0",
                'max-overall-upload-limit': "0",
            }
            return self.instance.set_global_options(options)
        except Exception as err:
            logging.error("[%s] global rate limit cancel failed: %s", self.name, err)
            return False

    def send_torrent_task(self, task: DownloadTask) -> DownloadTask:
        func_name = inspect.currentframe().f_code.co_name
        raise UnSupportedMethod(self, func_name)

    def send_magnet_task(self, task: DownloadTask) -> DownloadTask:
        func_name = inspect.currentframe().f_code.co_name
        raise UnSupportedMethod(self, func_name)

    def send_general_task(self, task: DownloadTask) -> DownloadTask:
        ret = self.instance.add(task.url, options={'dir': task.download_path})
        task.download_task_id = ret[0].gid
        task.set_status(self.status_translate(ret[0].status))
        task.files = ret[0].files
        task.size = ret[0].total_length
        return task

    @staticmethod
    def status_translate(status):
        status_map = {
            "active": DownloadStates.progress,
            "paused": DownloadStates.paused,
            "complete": DownloadStates.complete,
            "error": DownloadStates.fail,
        }
        return status_map.get(status)

    def create_task(self, task: DownloadTask) -> DownloadTask:
        if not task.url.startswith('http'):
            raise TypeError("Aria2 do not support:" + task.url)
        return self.send_general_task(task)

    def paused_tasks(self, tasks: list[DownloadTask]) -> list[DownloadTask]:
        gids = [t.download_task_id for t in tasks]
        ret = self.instance.get_downloads(gids)
        pause_ret = self.instance.pause(ret)
        for index, task in enumerate(tasks):
            if pause_ret[index] is True:
                task.set_status(DownloadStates.paused)
        return tasks

    def resume_tasks(self, tasks: list[DownloadTask]) -> list[DownloadTask]:
        gids = [t.download_task_id for t in tasks]
        ret = self.instance.get_downloads(gids)
        pause_ret = self.instance.resume(ret)
        for index, task in enumerate(tasks):
            if pause_ret[index] is True:
                task.set_status(DownloadStates.progress)
        return tasks

    def query_task(self, task: DownloadTask) -> DownloadTask:
        ret = self.instance.get_download(task.download_task_id)
        task.set_status(self.status_translate(ret.status))
        task.files = ret.files
        task.size = ret.total_length
        task.progress = ret.progress
        return task

    def query_all_tasks(self) -> list[DownloadTask]:
        rets = self.instance.get_downloads()
        tasks = []
        for ret in rets:
            task = DownloadTask()
            task.set_status(self.status_translate(ret.status))
            task.files = ret.files
            task.size = ret.total_length
            task.progress = ret.progress
            task.download_task_id = ret.gid
            tasks.append(task)
        return tasks

    def remove_tasks(self, tasks: list[DownloadTask], trash_data: bool = True) -> list[DownloadTask]:
        gids = [t.download_task_id for t in tasks]
        ret = self.instance.get_downloads(gids)
        delete_ret = self.instance.remove(ret, force=True, files=trash_data, clean=True)
        for index, task in enumerate(tasks):
            if delete_ret[index] is True:
                task.set_status(DownloadStates.cancel)
        return tasks

    def remove_all_tasks(self, trash_data: bool = True) -> bool:
        all_task = self.instance.get_downloads()
        self.instance.remove(all_task, force=True, files=trash_data, clean=True)
        return True


if __name__ == '__main__':
    insatnce = Aria2Provider('aria2', 'http://nas.evell.top', 6800, 'P3TERX')
    res = insatnce.send_general_task(DownloadTask(url='https://www.baidu.com', path='/downloads'))
    # print(dict(res.__dict__))
    # res = insatnce.query_task(DownloadTask(
    #     **{'id': '', 'path': '/downloads', 'url': 'https://www.baidu.com', 'content': None, 'status': 'active',
    #        'files': [], 'total_length': None, 'download_task_id': 'a24233d61b871c71', 'size': 0}))
    print(res)
    # print(insatnce.remove_all_tasks())
