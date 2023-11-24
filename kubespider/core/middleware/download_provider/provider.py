import abc
import inspect

from utils.helper import parse_func_doc, extract_doc
from utils.types import ParamsType, ProviderType
from utils.values import DownloadTask


class DownloadProvider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, name: str) -> None:
        pass

    @classmethod
    def spec(cls) -> dict:
        # define which params need to front end before instance
        init_func = getattr(cls, '__init__')
        signature = inspect.signature(init_func)
        params = []
        iter_items = iter(signature.parameters.items())
        params_doc = parse_func_doc(init_func)
        # skip self
        next(iter_items, None)
        for param_name, param in iter_items:
            params.append({
                "name": param_name,
                "doc": params_doc.get(param_name, ""),
                "value_type": ParamsType.type_to_string(param.annotation),
                "nullable": False if param.default == inspect._empty else True
            })
        return {
            "provider_name": getattr(cls, 'PROVIDER_NAME', cls.__name__),
            "provider_type": ProviderType.download_provider,
            "desc": extract_doc(cls),
            "instance_params": params
        }

    @abc.abstractmethod
    def is_alive(self) -> bool:
        # provider instance is alive
        pass

    @abc.abstractmethod
    def global_rate_limit(self, download: int, upload: int = None) -> bool:
        # set the global rate limit size k
        pass

    @abc.abstractmethod
    def cancel_rate_limit(self) -> bool:
        # cancel the global rate limit
        pass

    @abc.abstractmethod
    def send_torrent_task(self, task: DownloadTask) -> [DownloadTask, Exception]:
        pass

    @abc.abstractmethod
    def send_magnet_task(self, task: DownloadTask) -> [DownloadTask, Exception]:
        pass

    @abc.abstractmethod
    def send_general_task(self, task: DownloadTask) -> [DownloadTask, Exception]:
        pass

    @abc.abstractmethod
    def create_task(self, task: DownloadTask) -> [DownloadTask, Exception]:
        pass

    @abc.abstractmethod
    def paused_tasks(self, task: list[DownloadTask]) -> list[DownloadTask]:
        pass

    @abc.abstractmethod
    def resume_tasks(self, task: list[DownloadTask]) -> list[DownloadTask]:
        pass

    @abc.abstractmethod
    def query_task(self, task: DownloadTask) -> DownloadTask:
        pass

    @abc.abstractmethod
    def query_all_tasks(self) -> list[DownloadTask]:
        pass

    @abc.abstractmethod
    def remove_tasks(self, tasks: list[DownloadTask], trash_data: bool = False) -> list[DownloadTask]:
        pass

    @abc.abstractmethod
    def remove_all_tasks(self) -> bool:
        pass
