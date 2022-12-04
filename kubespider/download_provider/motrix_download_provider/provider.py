import logging
import os

import aria2p

from download_provider import provider

class MotrixDownloadProvider(provider.DownloadProvider):
    def __init__(self) -> None:
        self.provider_name = 'motrix_download_provider'
        self.rpc_endpoint_host = ''
        self.rpc_endpoint_port = 0
        self.download_base_path = ''
        pass

    def get_provider_name(self):
        return self.provider_name

    def send_torrent_task(self, torrent_file_path, download_path):
        logging.info(f'{torrent_file_path}')
        self.load_config()

        aria2 = aria2p.API(
            aria2p.Client(
                host=self.rpc_endpoint_host,
                port=self.rpc_endpoint_port,
                secret=""
            )
        )
        download_path = os.path.join(self.download_base_path, download_path)
        try:
            ret = aria2.add_torrent(torrent_file_path, options={'dir': download_path})
            logging.info(f'Create download task result:{ret}')
            return True
        except:
            logging.warning("Please ensure your motrix server is ok")
            return False

    def send_general_task(self, url, path):
        self.load_config()
        aria2 = aria2p.API(
            aria2p.Client(
                host=self.rpc_endpoint_host,
                port=self.rpc_endpoint_port,
                secret=""
            )
        )
        download_path = os.path.join(self.download_base_path, "general/"+path)
        try:
            ret = aria2.add(url, options={'dir': download_path})
            logging.info(f'Create download task result:{ret}')
            return True
        except:
            logging.warning("Please ensure your motrix server is ok")
            return False

    def provider_enabled(self):
        cfg = provider.load_download_provider_config()
        if cfg.get(self.provider_name, 'ENABLE') == 'true':
            return True
        return False

    def load_config(self):
        cfg = provider.load_download_provider_config()
        self.rpc_endpoint_host = cfg.get(self.provider_name, 'RPC_ENDPOINT_HOST')
        self.rpc_endpoint_port = cfg.get(self.provider_name, 'RPC_ENDPOINT_PORT')
        self.download_base_path = cfg.get(self.provider_name, 'DOWNLOAD_BASE_PATH')
