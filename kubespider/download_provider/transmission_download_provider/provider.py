import logging
import os

from urllib.parse import urlparse
from transmission_rpc import Client
from download_provider.provider import DownloadProvider
from utils.types import LinkType

from utils.values import Task


class TransmissionDownloadProvider(DownloadProvider):
    """Transmission is a fast, easy, and free BitTorrent client."""

    def __init__(self, name: str, http_endpoint: str, username: str = "admin", password: str = "admin",
                 download_base_path: str = "", priority: int = 10) -> None:
        """
        :param name: unique instance name
        :param http_endpoint: http endpoint host
        :param username: username
        :param password: password
        :param download_base_path: download base path
        :param priority: priority
        """
        super().__init__(
            name=name,
            supported_link_types=[LinkType.torrent, LinkType.magnet],
            priority=priority
        )
        self.download_base_path = download_base_path
        self.http_endpoint = http_endpoint
        self.username = username
        self.password = password

        parse_result = urlparse(http_endpoint)
        self.client = Client(
            protocol=parse_result.scheme,
            host=parse_result.hostname,
            port=parse_result.port,
            path=parse_result.path,
            username=username,
            password=password,
        )

    @property
    def is_alive(self) -> bool:
        # TODO implement
        return True

    def get_defective_task(self) -> list[Task]:
        # Note: The definition of transmission state does not match this method, returning an empty list temporarily.
        # Transmission state definition is as follows:
        # 0: "stopped",
        # 1: "check pending",
        # 2: "checking",
        # 3: "download pending",
        # 4: "downloading",
        # 5: "seed pending",
        # 6: "seeding"
        return []

    def send_torrent_task(self, task: Task) -> TypeError:
        logging.info('Start torrent download:%s, path:%s', task.url, task.path)
        download_path = os.path.join(self.download_base_path, task.path)
        try:
            with open(task.url, 'rb') as torrent_file:
                self.client.add_torrent(torrent=torrent_file.read(), download_dir=download_path)
        except Exception as err:
            logging.error('Transmission torrent download err:%s', err)
            return err
        return None

    def send_magnet_task(self, task: Task) -> TypeError:
        logging.info('Start magnet download:%s, path:%s', task.url, task.path)
        download_path = os.path.join(self.download_base_path, task.path)
        try:
            self.client.add_torrent(torrent=task.url, download_dir=download_path)
        except Exception as err:
            logging.error('Transmission magnet download err:%s', err)
            return err
        return None

    def send_general_task(self, task: Task) -> TypeError:
        logging.warning('Transmission not support general task download! Please use aria2 or else download provider')
        return TypeError('Transmission not support general task download')

    def remove_tasks(self, tasks: list[Task]):
        logging.info('Start to remove all tasks...')
        try:
            torrents = self.client.get_torrents()
            task_ids = list(map(lambda torrent: torrent.id, torrents))
            if len(torrents) > 0:
                self.client.remove_torrent(ids=task_ids, delete_data=True)
        except Exception as err:
            logging.error('Transmission remove all tasks err:%s', err)
