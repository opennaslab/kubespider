import abc

class DownloadProvider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self) -> None:
        pass

    @abc.abstractmethod
    def get_provider_name(self):
        pass

    @abc.abstractmethod
    def send_task(self):
        pass

    @abc.abstractmethod
    def load_config(self, config):
        pass