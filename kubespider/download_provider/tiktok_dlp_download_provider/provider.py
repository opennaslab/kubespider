import logging
import json

from download_provider import provider
from utils import types
from utils.helper import get_request_controller
from utils.values import Task


class TiktokDownloadProvider(provider.DownloadProvider):
    """Tiktok downloader"""

    def __init__(self, name: str, http_endpoint_host: str = "http://127.0.0.1", http_endpoint_port: int = 3083,
                 cookie: str = "", use_proxy: bool = False, priority: int = 10) -> None:
        """
        :param name: unique instance name
        :param http_endpoint_host: http endpoint host
        :param http_endpoint_port: http endpoint port
        :param cookie: cookie
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
        self.cookie = cookie
        self.reqeust_handler = get_request_controller(use_proxy=use_proxy)

    @property
    def is_alive(self) -> bool:
        # TODO implement
        return True

    def get_defective_task(self) -> list[Task]:
        # These tasks are special, other download software could not handle
        return []

    def send_torrent_task(self, task: Task) -> TypeError:
        return TypeError("tiktok doesn't support torrent task")

    def send_magnet_task(self, task: Task) -> TypeError:
        return TypeError("tiktok doesn't support magnet task")

    def send_general_task(self, task: Task) -> TypeError:
        headers = {'Content-Type': 'application/json'}
        data = {'dataSource': task.url, 'path': task.path, 'cookie': self.cookie}
        logging.info('Send general task:%s', json.dumps(data))
        try:
            path = self.http_endpoint_host + ":" + str(self.http_endpoint_port) + '/api/v1/download'
            req = self.reqeust_handler.post(path, headers=headers, data=json.dumps(data), timeout=30)
            if req.status_code != 200:
                logging.error("Send general task error:%s", req.status_code)
        except Exception as err:
            logging.error("Send general task error:%s", err)
            return TypeError("Send general task error")

        return None

    def remove_tasks(self, tasks: list[Task]):
        pass
