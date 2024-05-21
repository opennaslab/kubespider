import logging
import os
import aria2p

from download_provider.provider import DownloadProvider
from utils import types
from utils.values import Task


class Aria2DownloadProvider(DownloadProvider):
    """
    aria2 is a lightweight, multi-protocol, and multi-source command-line download utility. It supports protocols
    such as HTTP, HTTPS, FTP, BitTorrent, and more. With features like resumable downloads and multiple connections,
    aria2 maximizes the utilization of network resources to enhance download speeds.
    """

    def __init__(self, name: str, rpc_endpoint_host: str, rpc_endpoint_port: int, secret: str,
                 download_base_path: str = "", priority: int = 10) -> None:
        """
        :param name: unique instance name
        :param rpc_endpoint_host: RPC endpoint host
        :param rpc_endpoint_port: RPC endpoint port
        :param secret: RPC secret
        :param download_base_path: download base path
        :param priority: download priority
        """
        super().__init__(
            name=name,
            supported_link_types=types.LinkType.types(),
            priority=priority
        )
        self.rpc_endpoint_host = rpc_endpoint_host
        self.rpc_endpoint_port = rpc_endpoint_port
        self.download_base_path = download_base_path
        self.secret = secret
        self.aria2 = aria2p.API(
            aria2p.Client(
                host=self.rpc_endpoint_host,
                port=self.rpc_endpoint_port,
                secret=self.secret
            )
        )

    @property
    def is_alive(self) -> bool:
        return True

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
                    file_type=types.LinkType.magnet,
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
