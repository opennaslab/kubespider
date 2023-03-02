import logging
import os

import qbittorrentapi

from download_provider import provider

class QbittorrentDownloadProvider(provider.DownloadProvider):
    def __init__(self) -> None:
        self.provider_name = 'qbittorrent_download_provider'
        self.http_endpoint_host = ''
        self.http_endpoint_port = 0
        self.client = None
        self.username = ''
        self.password = ''
        self.download_base_path = ''
        self.verify_webui_certificate = False

    def get_provider_name(self):
        return self.provider_name

    def provider_enabled(self):
        cfg = provider.load_download_provider_config(self.provider_name)
        return cfg['enable']

    def send_torrent_task(self, torrent_file_path, download_path):
        download_path = os.path.join(self.download_base_path, download_path)
        logging.info('Start torrent download:%s, path:%s', torrent_file_path, download_path)
        try:
            ret = self.client.torrents_add(torrent_files=torrent_file_path, save_path=download_path)
            logging.info('Create download task results:%s', ret)
        except Exception as err:
            logging.warning('Please ensure your qbittorrent server or your config are ok:%s', err)
            return err

    def send_magnet_task(self, url, path):
        logging.info('Start magent download:%s, path:%s', url, path)
        download_path = os.path.join(self.download_base_path, path)
        try:
            ret = self.client.torrents_add(urls=url, save_path=download_path)
            logging.info('Create download task results:%s', ret)
        except Exception as err:
            logging.warning('Please ensure your qbittorrent server or your config are ok:%s', err)
            return err

    def send_general_task(self, url, path):
        logging.warning('qbittorrent not support generatl task download! Please use aria2 or else download provider')
        return TypeError('qbittorrent not support generate task download')


    def load_config(self):
        cfg = provider.load_download_provider_config(self.provider_name)
        self.http_endpoint_host = cfg['http_endpoint_host']
        self.http_endpoint_port = cfg['http_endpoint_port']
        self.download_base_path = cfg['download_base_path']
        self.username = cfg['username']
        self.password = cfg['password']
        self.verify_webui_certificate = cfg['verify_webui_certificate']
        self.client = qbittorrentapi.Client(
            self.http_endpoint_host,
            self.http_endpoint_port,
            self.username,
            self.password,
            VERIFY_WEBUI_CERTIFICATE=self.verify_webui_certificate,
        )
        try:
            self.client.auth_log_in()
        except qbittorrentapi.LoginFailed as err:
            logging.warning('Auth into qbittorrent error:%s', err)
            return err