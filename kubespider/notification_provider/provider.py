import abc

from utils.config_reader import AbsConfigReader


class NotificationProvider(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        self.name = name
        self.config_reader = config_reader

    @abc.abstractmethod
    def push(self, *args, **kwargs) -> bool:
        # push message
        pass

    @abc.abstractmethod
    def get_provider_name(self) -> str:
        # name of notifications provider
        pass

    @abc.abstractmethod
    def provider_enabled(self) -> bool:
        pass
