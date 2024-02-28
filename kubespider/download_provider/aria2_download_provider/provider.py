import logging
import os
import aria2p

from download_provider.provider import DownloadProvider
from utils.config_reader import AbsConfigReader
from utils import types
from utils.values import Task


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

    def send_torrent_task(self, task: Task) -> TypeError:
        logging.info('Start torrent download:%s', task.url)
        download_path = os.path.join(self.download_base_path, task.path)
        try:
            ret = self.aria2.add_torrent(task.url, options={'dir': download_path})
            logging.info('Create download task result:%s', ret)
            task.task_id = ret.gid
            return None
        except Exception as err:
            logging.warning('Please ensure your aria2 server is ok:%s', err)
            return err
        return None

    def send_magnet_task(self, task: Task) -> TypeError:
        logging.info('Start magnet download:%s', task.url)
        download_path = os.path.join(self.download_base_path, task.path)
        try:
            ret = self.aria2.add_magnet(task.url, options={'dir': download_path})
            logging.info('Create download task result:%s', ret)
            task.task_id = ret.gid
            return None
        except Exception as err:
            logging.warning('Please ensure your aria2 server is ok:%s', err)
            return err

    def send_general_task(self, task: Task) -> TypeError:
        logging.info('Start general file download:%s', task.url)

        if not task.url.startswith('http'):
            return TypeError("Aria2 do not support:" + task.url)

        download_path = os.path.join(self.download_base_path, task.path)
        try:
            ret = self.aria2.add(task.url, options={'dir': download_path})
            task.task_id = ret[0].gid
            logging.info('Create download task result:%s', ret)
            return None
        except Exception as err:
            logging.warning('Please ensure your aria2-type download server is ok:%s', err)
            return err

    def remove_tasks(self, tasks: list[Task]):
        try:
            downloads = self.aria2.get_downloads()
            self.aria2.remove(downloads, force=True)
        except Exception as err:
            logging.warning('Aria2 remove tasks error:%s', err)

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
