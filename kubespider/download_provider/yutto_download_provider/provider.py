import logging
import json

from download_provider.provider import DownloadProvider
from utils import types
from utils.helper import get_request_controller
from utils.values import Task


class YuttoDownloadProvider(DownloadProvider):
    """Yutto downloader"""

    def __init__(self, name: str, http_endpoint_host: str, http_endpoint_port: int, use_proxy: bool = False,
                 priority: int = 10) -> None:
        """
        :param name: unique instance name
        :param http_endpoint_host: http endpoint host
        :param http_endpoint_port: http endpoint port
        :param use_proxy: whether you use proxy
        :param priority: priority
        """
        super().__init__(
            name=name,
            supported_link_types=[types.LinkType.general],
            priority=priority
        )

        self.http_endpoint_host = http_endpoint_host
        self.http_endpoint_port = http_endpoint_port
        self.request_handler = get_request_controller(use_proxy=use_proxy)

    @property
    def is_alive(self) -> bool:
        # TODO implement
        return True

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

        if not task.url.startswith('https://www.bilibili.com'):
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
