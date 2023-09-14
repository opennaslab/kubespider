import logging
import os

from urllib.parse import urlparse
from transmission_rpc import Client

from utils.config_reader import AbsConfigReader
from download_provider.provider import DownloadProvider
from api.values import Task


class TransmissionProvider(DownloadProvider):
    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        super().__init__(name, config_reader)
        self.provider_name = name
        self.provider_type = 'transmission_download_provider'
        self.client: Client = None
        self.download_base_path = ''

    def get_provider_type(self) -> str:
        return self.provider_type

    def provider_enabled(self) -> bool:
        return self.config_reader.read()['enable']

    def provide_priority(self) -> int:
        return self.config_reader.read()['priority']

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

    def get_all_task(self) -> list:
        torrents = self.client.get_torrents()
        return torrents

    def send_torrent_task(self, task: Task) -> [Task, Exception]:
        logging.info('Start torrent download:%s, path:%s', task.url, task.path)
        download_path = os.path.join(self.download_base_path, task.path)
        try:
            torrent = self.client.add_torrent(torrent=task.torrent_content, download_dir=download_path)
            task.download_task_id = torrent.id
            return task
        except Exception as err:
            logging.error('Transmission torrent download err:%s', err)
            return err

    def send_magnet_task(self, task: Task) -> [Task, Exception]:
        logging.info('Start magnet download:%s, path:%s', task.url, task.path)
        download_path = os.path.join(self.download_base_path, task.path)
        try:
            torrent = self.client.add_torrent(torrent=task.url, download_dir=download_path)
            task.download_task_id = torrent.id
            return task
        except Exception as err:
            logging.error('Transmission magnet download err:%s', err)
            return err

    def send_general_task(self, task: Task) -> [Task, Exception]:
        logging.warning('Transmission not support general task download! Please use aria2 or else download provider')
        return TypeError('Transmission not support general task download')

    def remove_all_tasks(self) -> bool:
        try:
            torrents = self.client.get_torrents()
            if len(torrents) > 0:
                task_ids = list(map(lambda torrent: torrent.id, torrents))
                self.client.remove_torrent(ids=task_ids, delete_data=True)
            logging.info('Transmission removed all tasks...')
            return True
        except Exception as err:
            logging.error('Transmission remove all tasks err:%s', err)
            return False

    def remove_tasks(self, tasks: list[Task]) -> list[Task]:
        try:
            task_map = {int(task.download_task_id): task for task in tasks if task.download_task_id}
            task_ids = list(task_map.keys())
            if len(task_ids) > 0:
                self.client.remove_torrent(ids=task_ids, delete_data=True)
            logging.info('Transmission removed tasks:%s', ",".join(tasks))
            return tasks
        except Exception as err:
            logging.error('Transmission remove all tasks err:%s', err)

    def load_config(self) -> TypeError:
        cfg = self.config_reader.read()
        self.download_base_path = cfg['download_base_path']
        http_endpoint = cfg.get('http_endpoint')
        username = cfg.get('username', 'admin')
        password = cfg.get('password', 'admin')

        parse_result = urlparse(http_endpoint)

        try:
            self.client = Client(
                protocol=parse_result.scheme,
                host=parse_result.hostname,
                port=parse_result.port,
                path=parse_result.path,
                username=username,
                password=password,
            )
        except Exception as err:
            logging.error("Init client error:%s", err)
            return err
        return None
