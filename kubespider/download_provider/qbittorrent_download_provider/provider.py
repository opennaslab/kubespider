import logging
import os

import qbittorrentapi
from qbittorrentapi.definitions import TorrentStates

from utils.config_reader import AbsConfigReader
from download_provider.provider import DownloadProvider
from api import types
from api.values import Task


class QbittorrentDownloadProvider(DownloadProvider):
    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        super().__init__(name, config_reader)
        self.provider_name = name
        self.provider_type = 'qbittorrent_download_provider'
        self.http_endpoint_host = ''
        self.http_endpoint_port = 0
        self.client: qbittorrentapi.Client = None
        self.username = ''
        self.password = ''
        self.download_base_path = ''
        self.verify_webui_certificate = False
        self.download_tags = ['']
        self.download_category = ''
        self.use_auto_torrent_management = False

    def get_provider_type(self) -> str:
        return self.provider_type

    def provider_enabled(self) -> bool:
        return self.config_reader.read()['enable']

    def provide_priority(self) -> int:
        return self.config_reader.read()['priority']

    def get_defective_task(self) -> list[Task]:
        torrents_info = self.client.torrents_info()
        defective_tasks = []
        for single_torrent in torrents_info:
            if single_torrent.state_enum == TorrentStates.ERROR:
                fail_task = Task(
                    url=single_torrent.magnet_uri,
                    path=single_torrent.save_path.removeprefix(self.download_base_path),
                    link_type=types.LINK_TYPE_MAGNET,
                )
                defective_tasks.append(fail_task)
                single_torrent.delete(delete_files=True)
                continue
            if single_torrent.state_enum == TorrentStates.METADATA_DOWNLOAD or \
                    single_torrent.state_enum == TorrentStates.STALLED_DOWNLOAD:
                if single_torrent.downloaded <= 0.0:
                    pending_task = Task(
                        url=single_torrent.magnet_uri,
                        path=single_torrent.save_path.removeprefix(self.download_base_path),
                        link_type=types.LINK_TYPE_MAGNET,
                    )
                    defective_tasks.append(pending_task)
                    single_torrent.delete(delete_files=True)
                    continue
        return defective_tasks

    def send_torrent_task(self, task: Task) -> TypeError:
        download_path = os.path.join(self.download_base_path, task.path)
        logging.info('Start torrent download:%s, path:%s', task.url, download_path)
        tags = task.extra_param('tags', self.download_tags)
        category = task.extra_param('category', self.download_category)
        use_auto_torrent_management = task.extra_param('use_auto_torrent_management', self.use_auto_torrent_management)
        if not category:
            use_auto_torrent_management = False
        try:
            logging.info('Create download task category:%s, tags:%s', category, tags)
            ret = self.client.torrents_add(torrent_files=task.url, save_path=download_path, category=category,
                                           tags=tags, use_auto_torrent_management=use_auto_torrent_management)
            logging.info('Create download task results:%s', ret)
            return None
        except Exception as err:
            logging.warning('Please ensure your qbittorrent server or your config are ok:%s', err)
            return err
        return None

    def send_magnet_task(self, task: Task) -> TypeError:
        logging.info('Start magent download:%s, path:%s', task.url, task.path)
        download_path = os.path.join(self.download_base_path, task.path)
        tags = task.extra_param('tags', self.download_tags)
        category = task.extra_param('category', self.download_category)
        use_auto_torrent_management = task.extra_param('use_auto_torrent_management', self.use_auto_torrent_management)
        if not category:
            use_auto_torrent_management = False
        try:
            logging.info('Create download task category:%s, tags:%s', category, tags)
            ret = self.client.torrents_add(urls=task.url, save_path=download_path, category=category, tags=tags, use_auto_torrent_management=use_auto_torrent_management)
            logging.info('Create download task results:%s', ret)
            return None
        except Exception as err:
            logging.warning('Please ensure your qbittorrent server or your config are ok:%s', err)
            return err
        return None

    def send_general_task(self, task: Task) -> TypeError:
        logging.warning('qbittorrent not support general task download! Please use aria2 or else download provider')
        return TypeError('qbittorrent not support general task download')

    def remove_tasks(self, tasks: list[Task]):
        try:
            self.client.torrents_delete(torrent_hashes='all', delete_files=True)
        except Exception as err:
            logging.warning('qbittorrent remove all tasks error:%s', err)

    def load_config(self) -> TypeError:
        cfg = self.config_reader.read()
        self.http_endpoint_host = cfg['http_endpoint_host']
        self.http_endpoint_port = cfg['http_endpoint_port']
        self.download_base_path = cfg['download_base_path']
        self.username = cfg['username']
        self.password = cfg['password']
        self.verify_webui_certificate = cfg['verify_webui_certificate']
        self.download_tags = cfg.get('tags', [])
        self.download_category = cfg.get('category')
        self.use_auto_torrent_management = cfg['use_auto_torrent_management']
        self.client = qbittorrentapi.Client(
            self.http_endpoint_host,
            self.http_endpoint_port,
            self.username,
            self.password,
            VERIFY_WEBUI_CERTIFICATE=self.verify_webui_certificate,
        )
        try:
            self.client.auth_log_in()
            return None
        except qbittorrentapi.LoginFailed as err:
            logging.warning('Auth into qbittorrent error:%s', err)
            return err
        return None
