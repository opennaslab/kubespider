import os
import abc
import threading

from utils import helper

download_provider_file_lock = threading.Lock()


class DownloadProvider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def get_provider_name(self):
        pass

    @abc.abstractmethod
    def provider_enabled(self):
        pass

    @abc.abstractmethod
    def provide_priority(self):
        pass

    @abc.abstractmethod
    def get_defective_task(self):
        # This will be call every 1m, should return the list downloads
        # with none process or failed tasks, and then remove the download tasks
        # The return is a list of map, the map should be {'path': 'download', 'url': 'url', 'linkType': 'link_type'}
        pass

    @abc.abstractmethod
    def send_torrent_task(self, torrent_file_path, download_path):
        pass

    @abc.abstractmethod
    def send_magnet_task(self, url, path):
        pass

    @abc.abstractmethod
    def send_general_task(self, url, path):
        pass

    @abc.abstractmethod
    def load_config(self):
        pass


def load_download_provider_config(provider_name):
    config_path = os.path.join(os.getenv('HOME'), '.config/download_provider.cfg')
    cfg = helper.load_json_config(config_path, download_provider_file_lock)
    return cfg[provider_name]
