import abc

from utils.config_reader import AbsConfigReader

# Each PT site is built on a certain framework
# So providers are classified according to the framework.
class PTProvider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, config_reader: AbsConfigReader) -> None:
        pass

    @abc.abstractmethod
    def get_provider_name(self) -> str:
        # name of source provider defined in config
        pass

    @abc.abstractmethod
    def provider_enabled(self) -> bool:
        pass

    @abc.abstractmethod
    def get_links(self) -> list:
        # links list, return in following format
        #  list of {'size': size, 'torrent': file, 'free': is_free}
        pass

    @abc.abstractmethod
    def go_attendance(self) -> None:
        # listen type of provider, disposable or periodly
        pass

    @abc.abstractmethod
    def get_download_provider(self) -> str:
        pass

    @abc.abstractmethod
    def get_cost_sum_size(self) -> float:
        pass

    @abc.abstractmethod
    def get_max_sum_size(self) -> float:
        pass

    @abc.abstractmethod
    def get_keeping_time(self) -> int:
        pass
