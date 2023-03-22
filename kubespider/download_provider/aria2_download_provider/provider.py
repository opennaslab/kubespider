import logging
import os

import aria2p

from download_provider import provider
from api import types


class Aria2DownloadProvider(provider.DownloadProvider):
    def __init__(self) -> None:
        self.provider_name = 'aria2_download_provider'
        self.rpc_endpoint_host = ''
        self.rpc_endpoint_port = 0
        self.download_base_path = ''
        self.aria2 = None
        self.secret = ''

    def get_provider_name(self) -> str:
        return self.provider_name

    def provider_enabled(self) -> bool:
        cfg = provider.load_download_provider_config(self.provider_name)
        return cfg['enable']

    def provide_priority(self) -> int:
        cfg = provider.load_download_provider_config(self.provider_name)
        return cfg['priority']

    def get_defective_task(self) -> dict:
        defective_tasks = []
        downloads = self.aria2.get_downloads()
        for single_download in downloads:
            if single_download.is_waiting:
                # The task queue length is limited, so the status maybe be waiting
                continue
            # in general, we only return the bt pending tasks
            if single_download.progress <= 0.0 and single_download.is_torrent:
                file_type = types.LINK_TYPE_MAGNET
                url = 'magnet:?xt=urn:btih:'+single_download.info_hash

                # now remove the tasks
                self.aria2.remove([single_download], force=True)

                pending_task = {
                    'path': str(single_download.dir).removeprefix(self.download_base_path),
                    'url': url,
                    'linkType': file_type
                }
                defective_tasks.append(pending_task)

        return defective_tasks

    def send_torrent_task(self, torrent_file_path: str, download_path: str) -> TypeError:
        logging.info('Start torrent download:%s', torrent_file_path)
        download_path = os.path.join(self.download_base_path, download_path)
        try:
            ret = self.aria2.add_torrent(torrent_file_path, options={'dir': download_path})
            logging.info('Create download task result:%s', ret)
            return None
        except Exception as err:
            logging.warning('Please ensure your aria2 server is ok:%s', err)
            return err
        return None

    def send_magnet_task(self, url: str, path: str) -> TypeError:
        logging.info('Start magnet download:%s', url)
        download_path = os.path.join(self.download_base_path, path)
        try:
            ret = self.aria2.add_magnet(url, options={'dir': download_path})
            logging.info('Create download task result:%s', ret)
            return None
        except Exception as err:
            logging.warning('Please ensure your aria2 server is ok:%s', err)
            return err

    def send_general_task(self, url: str, path: str) -> TypeError:
        logging.info('Start general file download:%s', url)

        if not url.startswith('http'):
            return TypeError("Aria2 do not support:"+url)

        download_path = os.path.join(self.download_base_path, path)
        try:
            ret = self.aria2.add(url, options={'dir': download_path})
            logging.info('Create download task result:%s', ret)
            return None
        except Exception as err:
            logging.warning('Please ensure your aria2-type download server is ok:%s', err)
            return err

    def load_config(self) -> TypeError:
        cfg = provider.load_download_provider_config(self.provider_name)
        self.rpc_endpoint_host = cfg['rpc_endpoint_host']
        self.rpc_endpoint_port = cfg['rpc_endpoint_port']
        self.download_base_path = cfg['download_base_path']
        self.secret = cfg['secret']
        self.aria2 = aria2p.API(
            aria2p.Client(
                host=self.rpc_endpoint_host,
                port=self.rpc_endpoint_port,
                secret=self.secret
            )
        )
