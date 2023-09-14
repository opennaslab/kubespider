import abc
import io

from api.values import Task, Resource
from utils.config_reader import AbsConfigReader


# Each PT site is built on a certain framework
# So providers are classified according to the framework.
class PTUser(metaclass=abc.ABCMeta):
    @property
    @abc.abstractmethod
    def data(self) -> dict:
        # user info
        pass

    @abc.abstractmethod
    def __repr__(self) -> str:
        pass


class Torrent(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self):
        self.id = None  # Unique identification of torrent
        self.torrent_content = None

    @property
    @abc.abstractmethod
    def data(self) -> dict:
        # torrent attributes
        pass

    @abc.abstractmethod
    def to_download_task(self) -> Task:
        # This method is used to define how to merge the attributes of torrent
        pass

    @abc.abstractmethod
    def to_download_resource(self, torrent_content: io.BytesIO, download_path: str) -> Resource:
        # This method is used to define how to merge the attributes of torrent
        pass

    @abc.abstractmethod
    def __add__(self, other):
        # This method is used to define how to merge the attributes of torrent
        pass

    @classmethod
    @abc.abstractmethod
    def merge_torrents(cls, torrents: list) -> list:
        # This method is used to merge torrent attributes with the same identifier from different sources
        pass

    @property
    @abc.abstractmethod
    def is_effective_torrent(self) -> bool:
        # Determine whether the current torrent information is complete
        pass

    @abc.abstractmethod
    def update_property(self, *args, **kwargs) -> None:
        # When the torrent information is missing, call this method to supplement the information
        pass


class PTProvider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, config_reader: AbsConfigReader) -> None:
        pass

    @abc.abstractmethod
    def get_pt_user(self) -> PTUser:
        # name of source provider defined in config
        pass

    @abc.abstractmethod
    def need_delete_torrents(self, **kwargs) -> bool:
        pass

    @abc.abstractmethod
    def get_provider_name(self) -> str:
        # name of source provider defined in config
        pass

    @abc.abstractmethod
    def provider_enabled(self) -> bool:
        pass

    @abc.abstractmethod
    def get_torrents(self, user) -> list:
        # links list, return in following format
        #  list of Torrent
        pass

    @abc.abstractmethod
    def filter_torrents_for_deletion(self, user, max_sum_size, download_sum_size) -> list:
        # Obtain the torrents to be deleted
        pass

    @abc.abstractmethod
    def filter_torrents_for_download(self, user) -> list:
        pass

    @abc.abstractmethod
    def go_attendance(self, user) -> None:
        # listen type of provider, disposable or periodly
        pass

    @abc.abstractmethod
    def get_download_provider(self) -> str:
        pass

    @abc.abstractmethod
    def get_max_sum_size(self) -> float:
        pass

    @abc.abstractmethod
    def download_torrent_file(self, user: PTUser, torrent: Torrent) -> [io.BytesIO, None]:
        pass
