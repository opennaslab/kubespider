import logging
import os

from urllib.parse import urlparse
from utils.config_reader import AbsConfigReader
from download_provider import provider
from transmission_rpc import Client


class TransmissionProvider(
    provider.DownloadProvider  # pylint length
):
    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        super().__init__(name, config_reader)
        self.provider_name = name
        self.provider_type = 'transmission_download_provider'
        self.client = None
        self.download_base_path = ''

    def get_provider_name(self) -> str:
        return self.provider_name

    def get_provider_type(self) -> str:
        return self.provider_type

    def provider_enabled(self) -> bool:
        return self.config_reader.read()['enable']

    def provide_priority(self) -> int:
        return self.config_reader.read()['priority']

    def get_defective_task(self) -> dict:
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

    def send_torrent_task(self, torrent_file_path, download_path, extra_param=None) -> TypeError:
        logging.info('Start torrent download:%s, path:%s', torrent_file_path, download_path)
        download_path = os.path.join(self.download_base_path, download_path)
        try:
            with open(torrent_file_path, 'rb') as torrent_file:
                self.client.add_torrent(torrent=torrent_file.read(), download_dir=download_path)
        except Exception as err:
            logging.error('Transmission torrent download err:%s', err)
            return err
        return None

    def send_magnet_task(self, url: str, path: str, extra_param=None) -> TypeError:
        logging.info('Start magnet download:%s, path:%s', url, path)
        download_path = os.path.join(self.download_base_path, path)
        try:
            self.client.add_torrent(torrent=url, download_dir=download_path)
        except Exception as err:
            logging.error('Transmission magnet download err:%s', err)
            return err
        return None

    def send_general_task(self, url: str, path: str, extra_param=None) -> TypeError:
        logging.warning('Transmission not support general task download! Please use aria2 or else download provider')
        return TypeError('Transmission not support general task download')

    def remove_tasks(self, para=None):
        if para is None:
            logging.info('Start to remove all tasks...')
            try:
                torrents = self.client.get_torrents()
                for torrent in torrents:
                    self.client.remove_torrent(ids=[torrent.id], delete_data=True)
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
