import abc

from utils import helper
from utils.helper import Config
from utils.config_reader import AbsConfigReader


class SourceProvider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, config_reader: AbsConfigReader) -> None:
        self.config_reader = config_reader
        pass

    @abc.abstractmethod
    def get_provider_name(self) -> str:
        # name of source provider defined in config
        pass

    @abc.abstractmethod
    def get_provider_type(self) -> str:
        # type of provider
        pass

    @abc.abstractmethod
    def get_provider_listen_type(self) -> str:
        # listen type of provider, disposable or periodly
        pass

    @abc.abstractmethod
    def get_download_provider_type(self) -> str:
        # in general, if this source provider needs to work with specific downlad
        # provider, return the TYPE of the download provider
        pass

    @abc.abstractmethod
    def get_prefer_download_provider(self) -> list:
        # if the provider is configed to use some specified download providers,
        # return them here in a list
        pass

    @abc.abstractmethod
    def get_download_param(self) -> list:
        # get the specific params for downloader
        pass

    @abc.abstractmethod
    def get_link_type(self) -> str:
        pass

    @abc.abstractmethod
    def provider_enabled(self) -> bool:
        pass

    @abc.abstractmethod
    def is_webhook_enable(self) -> bool:
        pass

    @abc.abstractmethod
    def should_handle(self, data_source_url: str) -> bool:
        pass

    # Return the download links for the source provider, the return struct should be format like:
    # {'path': 'file_path', 'link': 'download_link', 'file_type': 'file type'}
    @abc.abstractmethod
    def get_links(self, data_source_url: str) -> dict:
        pass

    @abc.abstractmethod
    def update_config(self, req_para: str) -> None:
        pass

    @abc.abstractmethod
    def load_config(self) -> None:
        pass
