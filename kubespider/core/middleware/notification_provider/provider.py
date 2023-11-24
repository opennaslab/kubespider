import abc
import inspect

from utils.config_reader import AbsConfigReader
from utils.helper import extract_doc, parse_func_doc
from utils.types import ParamsType, ProviderType


class NotificationProvider(metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        self.name = name
        self.config_reader = config_reader

    @classmethod
    def spec(cls) -> dict:
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
            "provider_type": ProviderType.notification_provider,
            "desc": extract_doc(cls),
            "instance_params": params
        }

    @abc.abstractmethod
    def push(self, title: str, **kwargs) -> bool:
        # push message
        pass

    @abc.abstractmethod
    def format_message(self, title, **kwargs) -> str:
        pass
