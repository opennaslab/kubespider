import logging
import json
import re
from utils.config_reader import AbsConfigReader
from utils.helper import get_request_controller
from download_provider.provider import DownloadProvider
from api.values import Task


class YuttoDownloadProvider(DownloadProvider):
    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        super().__init__(name, config_reader)
        self.provider_name = name
        self.provider_type = 'yutto_download_provider'
        self.http_endpoint_host = ''
        self.http_endpoint_port = 0
        self.request_handler = get_request_controller(use_proxy=False)

    def get_provider_type(self) -> str:
        return self.provider_type

    def provider_enabled(self) -> bool:
        return self.config_reader.read()['enable']

    def provide_priority(self) -> int:
        return self.config_reader.read()['priority']

    def get_defective_task(self) -> list[Task]:
        # These tasks are special, other download software could not handle
        return []

    def send_torrent_task(self, task: Task) -> TypeError:
        return TypeError("yutto doesn't support torrent task")

    def send_magnet_task(self, task: Task) -> TypeError:
        return TypeError("yutto doesn't support magnet task")

    def send_general_task(self, task: Task) -> TypeError:
        headers = {'Content-Type': 'application/json'}
        data = {'dataSource': task.url, 'path': task.path}
        logging.info('Send general task:%s', json.dumps(data))

        if not (task.url.startswith('https://www.bilibili.com') or task.url.startswith('https://b23.tv')):
            return TypeError('yutto only support specific resource')

        # This downloading tasks is special, other download software could not handle
        # So just return None
        try:
            path = self.http_endpoint_host + ":" + str(self.http_endpoint_port) + '/api/v1/download'
            req = self.request_handler.post(path, headers=headers, data=json.dumps(data), timeout=30)
            if req.status_code != 200:
                logging.error("Send general task error:%s", req.status_code)
        except Exception as err:
            logging.error("Send general task error:%s", err)
            return None
        return None

    def remove_tasks(self, tasks: list[Task]):
        # TODO: Implement it
        pass

    def load_config(self) -> TypeError:
        cfg = self.config_reader.read()
        self.http_endpoint_host = cfg['http_endpoint_host']
        self.http_endpoint_port = cfg['http_endpoint_port']
