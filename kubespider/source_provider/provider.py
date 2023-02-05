import os
import abc
import threading

from utils import helper

source_provider_file_lock = threading.Lock()


class SourceProvider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def get_provider_name(self):
        pass

    @abc.abstractmethod
    def get_provider_type(self):
        pass

    @abc.abstractmethod
    def get_link_type(self):
        pass

    @abc.abstractmethod
    def provider_enabled(self):
        pass

    @abc.abstractmethod
    def is_webhook_enable(self):
        pass

    @abc.abstractmethod
    def should_handle(self, data_source_url: str):
        pass

    # Return the download links for the source provider, the return struct should be format like:
    # {'path': 'file_path', 'link': 'download_link', 'file_type': 'file type'}
    @abc.abstractmethod
    def get_links(self, data_source_url: str):
        pass

    @abc.abstractmethod
    def update_config(self, req_para: str):
        pass

    @abc.abstractmethod
    def load_config(self):
        pass


def load_source_provide_config(provider_name):
    config_path = os.path.join(os.getenv('HOME'), '.kubespider/source_provider.cfg')
    cfg = helper.load_json_config(config_path, source_provider_file_lock)
    return cfg[provider_name]

def save_source_provider_config(provider_name, provider_cfg):
    config_path = os.path.join(os.getenv('HOME'), '.kubespider/source_provider.cfg')
    cfg = helper.load_json_config(config_path, source_provider_file_lock)
    cfg[provider_name] = provider_cfg
    helper.dump_json_config(config_path, cfg, source_provider_file_lock)
