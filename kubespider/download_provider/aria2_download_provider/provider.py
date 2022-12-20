import logging
import os

import aria2p

from download_provider import provider


class Aria2DownloadProvider(provider.DownloadProvider):
    def __init__(self) -> None:
        self.provider_name = 'aria2_download_provider'
        self.rpc_endpoint_host = ''
        self.rpc_endpoint_port = 0
        self.download_base_path = ''
        self.aria2 = None
        self.secret = ''

    def get_provider_name(self):
        return self.provider_name

    def provider_enabled(self):
        cfg = provider.load_download_provider_config(self.provider_name)
        return cfg['ENABLE'] == 'true'

    def send_torrent_task(self, torrent_file_path, download_path):
        logging.info(f'Start torrent download:{torrent_file_path}')
        download_path = os.path.join(self.download_base_path, download_path)
        try:
            ret = self.aria2.add_torrent(torrent_file_path, options={'dir': download_path})
            logging.info(f'Create download task result:{ret}')
            return None
        except Exception as err:
            logging.warning(f'Please ensure your motrix server is ok:{str(err)}')
            return err
        return None
    
    def send_magnet_task(self, url, path):
        logging.info(f'Start magnet download:{url}')
        download_path = os.path.join(self.download_base_path, path)
        try:
            ret = self.aria2.add_magnet(url, options={'dir': download_path})
            logging.info(f'Create download task result:{ret}')
            return None
        except Exception as err:
            logging.warning(f'Please ensure your motrix server is ok:{str(err)}')
            return err

    def send_general_task(self, url, path):
        logging.info(f'Start general file download:{url}')
        download_path = os.path.join(self.download_base_path, path)
        try:
            ret = self.aria2.add(url, options={'dir': download_path})
            logging.info(f'Create download task result:{ret}')
            return True
        except Exception as err:
            logging.warning(f'Please ensure your motrix server is ok:{str(err)}')
            return err

    def load_config(self):
        cfg = provider.load_download_provider_config(self.provider_name)
        self.rpc_endpoint_host = cfg['RPC_ENDPOINT_HOST']
        self.rpc_endpoint_port = cfg['RPC_ENDPOINT_PORT']
        self.download_base_path = cfg['DOWNLOAD_BASE_PATH']
        self.secret = cfg['SECRET']
        self.aria2 = aria2p.API(
            aria2p.Client(
                host=self.rpc_endpoint_host,
                port=self.rpc_endpoint_port,
                secret=self.secret
            )
        )