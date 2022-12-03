import os
import abc
import configparser

class DownloadProvider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def get_provider_name(self):
        pass

    @abc.abstractmethod
    def send_torrent_task(self, torrent_file_path, download_path):
        pass

    @abc.abstractmethod
    def send_general_task(self, url, path):
        pass

    @abc.abstractmethod
    def load_config(self):
        pass

    @abc.abstractmethod
    def provider_enabled(self):
        pass

def load_download_provider_config():
    cfg = configparser.ConfigParser()
    config_path = os.path.join(os.getenv('HOME'), '.kubespider')
    cfg.read(os.path.join(config_path, 'download_provider.cfg'))
    return cfg