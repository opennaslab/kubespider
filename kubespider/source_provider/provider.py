import abc

from utils.values import Resource, Event
from utils.config_reader import AbsConfigReader


class SourceProvider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, config_reader: AbsConfigReader) -> None:
        self.config_reader = config_reader

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
        # listen type of provider, disposable or period
        pass

    @abc.abstractmethod
    def get_download_provider_type(self) -> str:
        # in general, if this source provider needs to work with specific download
        # provider, return the TYPE of the download provider
        pass

    @abc.abstractmethod
    def get_prefer_download_provider(self) -> list:
        # if the provider is confined to use some specified download providers,
        # return them here in a list
        pass

    @abc.abstractmethod
    def get_download_param(self) -> dict:
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
    def should_handle(self, event: Event) -> bool:
        pass

    # Return the download resources for the source provider
    @abc.abstractmethod
    def get_links(self, event: Event) -> list[Resource]:
        pass

    @abc.abstractmethod
    def update_config(self, event: Event) -> None:
        pass

    @abc.abstractmethod
    def load_config(self) -> None:
        pass
