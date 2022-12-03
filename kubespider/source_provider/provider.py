import os
import abc
import configparser
import logging

class SourceProvider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def should_handle(self, dataSourceUrl):
        pass

    @abc.abstractmethod
    def get_provider_type(self):
        pass
    
    @abc.abstractmethod
    def get_provider_name(self):
        pass
    
    @abc.abstractmethod
    def is_webhook_enable(self):
        pass

    @abc.abstractmethod
    def load_config(self):
        pass

    @abc.abstractmethod
    def provider_enabled(self):
        pass

    @abc.abstractmethod
    def get_file_type(self):
        return self.file_type
    
    @abc.abstractmethod
    def get_links(self, dataSourceUrl):
        pass

    @abc.abstractmethod
    def get_download_path(self):
        pass

def load_source_provide_config():
    cfg = configparser.ConfigParser()
    config_path = os.path.join(os.getenv('HOME'), '.kubespider')
    cfg.read(os.path.join(config_path, 'source_provider.cfg'))
    return cfg
