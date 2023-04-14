import logging
import os

import qbittorrentapi
from qbittorrentapi.definitions import TorrentStates

from download_provider import provider
from api import types


class QbittorrentDownloadProvider(
        provider.DownloadProvider # pylint length
    ):
    def __init__(self, name: str) -> None:
        self.provider_name = name
        self.provider_type = 'qbittorrent_download_provider'
        self.http_endpoint_host = ''
        self.http_endpoint_port = 0
        self.client = None
        self.username = ''
        self.password = ''
        self.download_base_path = ''
        self.verify_webui_certificate = False
        self.download_tags = ['']
        self.download_category = ''

    def get_provider_name(self) -> str:
        return self.provider_name
    
    def get_provider_type(self) -> str:
        return self.provider_type

    def provider_enabled(self) -> bool:
        cfg = provider.load_download_provider_config(self.provider_name)
        return cfg['enable']

    def provide_priority(self) -> int:
        cfg = provider.load_download_provider_config(self.provider_name)
        return cfg['priority']

    def get_defective_task(self) -> dict:
        torrents_info = self.client.torrents_info()
        defective_tasks = []
        for single_torrent in torrents_info:
            if single_torrent.state_enum == TorrentStates.ERROR:
                fail_task = {
                    'path': single_torrent.save_path.removeprefix(self.download_base_path),
                    'url': single_torrent.magnet_uri,
                    'linkType': types.LINK_TYPE_MAGNET
                }
                defective_tasks.append(fail_task)
                single_torrent.delete(delete_files=True)
                continue
            if single_torrent.state_enum == TorrentStates.METADATA_DOWNLOAD or \
                single_torrent.state_enum == TorrentStates.STALLED_DOWNLOAD:
                if single_torrent.downloaded <= 0.0:
                    pending_task = {
                        'path': single_torrent.save_path.removeprefix(self.download_base_path),
                        'url': single_torrent.magnet_uri,
                        'linkType': types.LINK_TYPE_MAGNET
                    }
                    defective_tasks.append(pending_task)
                    single_torrent.delete(delete_files=True)
                    continue
        return defective_tasks

    def send_torrent_task(self, torrent_file_path: str, download_path: str) -> TypeError:
        download_path = os.path.join(self.download_base_path, download_path)
        logging.info('Start torrent download:%s, path:%s', torrent_file_path, download_path)
        try:
            logging.info('Create download task category:%s, tags:%s', self.download_category, self.download_tags)
            ret = self.client.torrents_add(torrent_files=torrent_file_path, save_path=download_path, category=self.download_category, tags=self.download_tags)
            logging.info('Create download task results:%s', ret)
            return None
        except Exception as err:
            logging.warning('Please ensure your qbittorrent server or your config are ok:%s', err)
            return err
        return None

    def send_magnet_task(self, url: str, path: str) -> TypeError:
        logging.info('Start magent download:%s, path:%s', url, path)
        download_path = os.path.join(self.download_base_path, path)
        try:
            logging.info('Create download task category:%s, tags:%s', self.download_category, self.download_tags)
            ret = self.client.torrents_add(urls=url, save_path=download_path, category=self.download_category, tags=self.download_tags)
            logging.info('Create download task results:%s', ret)
            return None
        except Exception as err:
            logging.warning('Please ensure your qbittorrent server or your config are ok:%s', err)
            return err
        return None

    def send_general_task(self, url: str, path: str) -> TypeError:
        logging.warning('qbittorrent not support generatl task download! Please use aria2 or else download provider')
        return TypeError('qbittorrent not support generate task download')


    def load_config(self) -> TypeError:
        cfg = provider.load_download_provider_config(self.provider_name)
        self.http_endpoint_host = cfg['http_endpoint_host']
        self.http_endpoint_port = cfg['http_endpoint_port']
        self.download_base_path = cfg['download_base_path']
        self.username = cfg['username']
        self.password = cfg['password']
        self.verify_webui_certificate = cfg['verify_webui_certificate']
        self.download_tags = cfg.get('tags')
        self.download_category = cfg.get('category')
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
