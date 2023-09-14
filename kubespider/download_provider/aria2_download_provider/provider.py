import logging
import os

import aria2p

from utils.config_reader import AbsConfigReader
from download_provider.provider import DownloadProvider
from api import types
from api.values import Task


class Aria2DownloadProvider(DownloadProvider):
    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        super().__init__(name, config_reader)
        self.provider_name = name
        self.provider_type = 'aria2_download_provider'
        self.rpc_endpoint_host = ''
        self.rpc_endpoint_port = 0
        self.download_base_path = ''
        self.aria2: aria2p.API = None
        self.secret = ''

    def get_provider_type(self) -> str:
        return self.provider_type

    def provider_enabled(self) -> bool:
        return self.config_reader.read()['enable']

    def provide_priority(self) -> int:
        return self.config_reader.read()['priority']

    def get_defective_task(self) -> list[Task]:
        defective_tasks = []
        downloads = self.aria2.get_downloads()
        for single_download in downloads:
            if single_download.is_waiting:
                # The task queue length is limited, so the status maybe be waiting
                continue
            # in general, we only return the bt pending tasks
            if single_download.progress <= 0.0 and single_download.is_torrent:
                # now remove the tasks
                self.aria2.remove([single_download], force=True)
                pending_task = Task(
                    url='magnet:?xt=urn:btih:' + single_download.info_hash,
                    file_type=types.LINK_TYPE_MAGNET,
                    path=str(single_download.dir).removeprefix(self.download_base_path)
                )
                defective_tasks.append(pending_task)

        return defective_tasks

    def send_torrent_task(self, task: Task) -> [Task, Exception]:
        logging.info('Start torrent download:%s', task.url)
        download_path = os.path.join(self.download_base_path, task.path)
        try:
            ret = self.aria2.add_torrent(task.url, options={'dir': download_path})
            logging.info('Create download task result:%s', ret)
            task.download_task_id = ret.gid
            return task
        except Exception as err:
            logging.warning('Please ensure your aria2 server is ok:%s', err)
            return err

    def send_magnet_task(self, task: Task) -> [Task, Exception]:
        logging.info('Start magnet download:%s', task.url)
        download_path = os.path.join(self.download_base_path, task.path)
        try:
            ret = self.aria2.add_magnet(task.url, options={'dir': download_path})
            logging.info('Create download task result:%s', ret)
            task.download_task_id = ret.gid
            return task
        except Exception as err:
            logging.warning('Please ensure your aria2 server is ok:%s', err)
            return err

    def send_general_task(self, task: Task) -> [Task, Exception]:
        logging.info('Start general file download:%s', task.url)

        if not task.url.startswith('http'):
            return TypeError("Aria2 do not support:" + task.url)

        download_path = os.path.join(self.download_base_path, task.path)
        try:
            ret = self.aria2.add(task.url, options={'dir': download_path})
            task.download_task_id = ret[0].gid
            logging.info('Create download task result:%s', ret)
            return task
        except Exception as err:
            logging.warning('Please ensure your aria2-type download server is ok:%s', err)
            return err

    def remove_all_tasks(self) -> bool:
        try:
            downloads = self.aria2.get_downloads()
            self.aria2.remove(downloads, force=True)
            logging.info('Aria2 remove all tasks success')
            return True
        except Exception as err:
            logging.error('Aria2 remove tasks error:%s', err)
            return False

    def remove_tasks(self, tasks: list[Task]) -> list[Task]:
        task_map = {task.download_task_id: task for task in tasks if task.download_task_id}
        try:
            download_tasks = self.aria2.get_downloads(list(task_map.keys()))
            result = self.aria2.remove(download_tasks, force=True)
            removed_task_names = []
            removed_tasks = []
            for index, success in enumerate(result):
                if success:
                    task_name = download_tasks[index].name
                    task_gid = download_tasks[index].gid
                    removed_task_names.append(task_name)
                    removed_tasks.append(task_map.get(task_gid))
            logging.info('Aria2 remove tasks:%s', ",".join(removed_task_names))
            return removed_tasks
        except Exception as err:
            logging.error('Aria2 remove tasks error:%s', err)
            return []

    def load_config(self) -> TypeError:
        cfg = self.config_reader.read()
        self.rpc_endpoint_host = cfg['rpc_endpoint_host']
        self.rpc_endpoint_port = cfg['rpc_endpoint_port']
        self.download_base_path = cfg['download_base_path']
        self.secret = cfg['secret']
        self.aria2 = aria2p.API(
            aria2p.Client(
                host=self.rpc_endpoint_host,
                port=self.rpc_endpoint_port,
                secret=self.secret
            )
        )
