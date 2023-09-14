import logging
import json

from utils.config_reader import AbsConfigReader
from utils.helper import get_request_controller
from download_provider.provider import DownloadProvider
from api.values import Task


class YTDlpDownloadProvider(DownloadProvider):
    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        super().__init__(name, config_reader)
        self.provider_name = name
        self.provider_type = 'ytdlp_download_provider'
        self.http_endpoint_host = ''
        self.http_endpoint_port = 0
        self.auto_convert = False
        self.target_format = 'mp4'
        self.download_proxy = ''
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

    def send_torrent_task(self, task: Task) -> [Task, Exception]:
        return TypeError("yt-dlp doesn't support torrent task")

    def send_magnet_task(self, task: Task) -> [Task, Exception]:
        return TypeError("yt-dlp doesn't support magnet task")

    def send_general_task(self, task: Task) -> [Task, Exception]:
        # This downloading tasks is special, other download software could not handle
        # So just return None
        try:
            headers = {'Content-Type': 'application/json'}
            data = {
                'dataSource': task.url,
                'path': task.path,
                'autoFormatConvert': self.auto_convert,
                'targetFormat': self.target_format,
                'downloadProxy': self.download_proxy
            }
            logging.info('Send general task:%s', json.dumps(data))
            if not task.url.startswith('https://www.youtube.com/'):
                raise TypeError('yt-dlp only support specific resource')
            path = self.http_endpoint_host + ":" + str(self.http_endpoint_port) + '/api/v1/download'
            req = self.request_handler.post(path, headers=headers, data=json.dumps(data), timeout=30)
            if req.status_code != 200:
                raise Exception(f"status code {req.status_code}",)
            return task
        except Exception as err:
            logging.error("Send general task error:%s", err)
            return err

    def remove_tasks(self, tasks: list[Task]) -> list[Task]:
        # TODO: Implement it
        logging.warning("Ytdlp not support remove tasks")
        return []

    def remove_all_tasks(self) -> bool:
        # TODO: Implement it
        logging.warning("Ytdlp not support remove all tasks")
        return False

    def load_config(self) -> TypeError:
        cfg = self.config_reader.read()
        self.http_endpoint_host = cfg.get('http_endpoint_host', None)
        self.http_endpoint_port = cfg.get('http_endpoint_port', None)
        self.auto_convert = cfg.get('auto_format_convet', False)
        self.target_format = cfg.get('target_format', 'mp4')
        self.download_proxy = cfg.get('download_proxy', '')
