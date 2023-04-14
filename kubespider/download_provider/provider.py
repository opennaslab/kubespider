import abc

from utils import helper
from utils.helper import Config


class DownloadProvider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self) -> None:
        pass

    # 配置中声明的名字
    @abc.abstractmethod
    def get_provider_name(self) -> str:
        pass

    # 下载器类型
    @abc.abstractmethod
    def get_provider_type(self) -> str:
        pass

    @abc.abstractmethod
    def provider_enabled(self) -> bool:
        pass

    @abc.abstractmethod
    def provide_priority(self) -> int:
        pass

    @abc.abstractmethod
    def get_defective_task(self) -> dict:
        # This will be call every 1m, should return the list downloads
        # with none process or failed tasks, and then remove the download tasks
        # The return is a list of map, the map should be {'path': 'download', 'url': 'url', 'linkType': 'link_type'}
        pass

    @abc.abstractmethod
    def send_torrent_task(self, torrent_file_path, download_path, extra_param=None) -> TypeError:
        pass

    @abc.abstractmethod
    def send_magnet_task(self, url: str, path: str, extra_param=None) -> TypeError:
        pass

    @abc.abstractmethod
    def send_general_task(self, url: str, path: str, extra_param=None) -> TypeError:
        pass

    @abc.abstractmethod
    def load_config(self) -> TypeError:
        pass


def load_download_provider_config(provider_name: str) -> dict:
    cfg = helper.load_config(Config.DOWNLOAD_PROVIDER)
    return cfg[provider_name]
