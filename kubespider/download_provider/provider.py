import abc

from utils.config_reader import AbsConfigReader
from api.values import Task


class DownloadProvider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        self.provider_name = name
        self.config_reader = config_reader

    def get_provider_name(self) -> str:
        return self.provider_name

    @abc.abstractmethod
    def get_provider_type(self) -> str:
        # type of downloader
        pass

    @abc.abstractmethod
    def provider_enabled(self) -> bool:
        pass

    @abc.abstractmethod
    def provide_priority(self) -> int:
        pass

    @abc.abstractmethod
    def get_defective_task(self) -> list[Task]:
        # This will be call every 1m, should return the list downloads
        # with none process or failed tasks, and then remove the download tasks
        # The return is a list of Task(url, path, link_type)
        pass

    @abc.abstractmethod
    def send_torrent_task(self, task: Task) -> [Task, Exception]:
        pass

    @abc.abstractmethod
    def send_magnet_task(self, task: Task) -> [Task, Exception]:
        pass

    @abc.abstractmethod
    def send_general_task(self, task: Task) -> [Task, Exception]:
        pass

    @abc.abstractmethod
    def remove_tasks(self, tasks: list[Task]) -> list[Task]:
        pass

    @abc.abstractmethod
    def remove_all_tasks(self) -> bool:
        pass

    @abc.abstractmethod
    def load_config(self) -> TypeError:
        pass
