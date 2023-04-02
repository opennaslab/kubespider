import logging
import json

import requests

from download_provider import provider


class YougetDownloadProvider(
        provider.DownloadProvider # pylint length
    ):
    def __init__(self) -> None:
        self.provider_name = 'youget_download_provider'
        self.http_endpoint_host = ''
        self.http_endpoint_port = 0

    def get_provider_name(self) -> str:
        return self.provider_name

    def provider_enabled(self) -> bool:
        cfg = provider.load_download_provider_config(self.provider_name)
        return cfg['enable']

    def provide_priority(self) -> int:
        cfg = provider.load_download_provider_config(self.provider_name)
        return cfg['priority']

    def get_defective_task(self) -> dict:
        # These tasks is special, other download software could not handle
        return {}

    def send_torrent_task(self, torrent_file_path, download_path) -> TypeError:
        return TypeError("youget doesn't support torrent task")

    def send_magnet_task(self, url: str, path: str) -> TypeError:
        return TypeError("youget doesn't support magnet task")

    def send_general_task(self, url: str, path: str) -> TypeError:
        headers = {'Content-Type': 'application/json'}
        data = {'dataSource': url, 'path': path}
        logging.info('Send general task:%s', json.dumps(data))

        # This downloading tasks is special, other download software could not handle
        # So just return None
        try:
            path = self.http_endpoint_host + ":" + self.http_endpoint_port + '/api/v1/download'
            req = requests.post(path, headers=headers, data=json.dumps(data), timeout=30)
            if req.status_code != 200:
                logging.error("Send general task error:%s", req.status_code)
        except Exception as err:
            logging.error("Send general task error:%s", err)
            return None
        return None

    def load_config(self) -> TypeError:
        cfg = provider.load_download_provider_config(self.provider_name)
        self.http_endpoint_host = cfg['http_endpoint_host']
        self.http_endpoint_port = cfg['http_endpoint_port']
