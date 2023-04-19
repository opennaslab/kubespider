import logging
import os

from urllib.parse import urlparse
from download_provider import provider
from transmission_rpc import Client


class TransmissionProvider(
    provider.DownloadProvider  # pylint length
):
    def __init__(self, name: str) -> None:
        self.provider_name = name
        self.provider_type = 'transmission_download_provider'
        self.client = None
        self.download_base_path = ''

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
            self.client.add_torrent(torrent=torrent_file_path, download_dir=download_path)
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

    def load_config(self) -> TypeError:
        cfg = provider.load_download_provider_config(self.provider_name)
        self.download_base_path = cfg['download_base_path']
        http_endpoint = cfg['http_endpoint']
        username = cfg['username']
        password = cfg['password']

        parse_result = urlparse(http_endpoint)

        self.client = Client(
            protocol=parse_result.scheme,
            host=parse_result.hostname,
            port=parse_result.port,
            path=parse_result.path,
            username=username,
            password=password,
        )
