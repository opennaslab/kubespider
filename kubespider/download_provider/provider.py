import abc
import inspect
import typing
from utils.definition import ArgumentsFiled, Definition
from utils.helper import parse_func_doc, extract_doc
from utils.values import Task


class DownloadProvider(metaclass=abc.ABCMeta):

    def __init__(self, name: str, supported_link_types: list, priority: int = 10):
        self.name = name
        self.supported_link_types = supported_link_types
        self.priority = priority

    def __repr__(self):
        return f"<{self.__class__.__name__}:{self.name}>"

    @property
    @abc.abstractmethod
    def is_alive(self) -> bool:
        pass

    @classmethod
    def definitions(cls) -> dict:
        init_func = getattr(cls, '__init__')
        signature = inspect.signature(init_func)
        arguments = {}
        iter_items = iter(signature.parameters.items())
        params_doc = parse_func_doc(init_func)
        # skip self
        next(iter_items, None)
        for param_name, param in iter_items:
            _type = ArgumentsFiled.type_to_string(param.annotation) or ArgumentsFiled.type_to_string(
                typing.get_origin(param.annotation))
            spec = {
                "description": params_doc.get(param_name, ""),
                "type": _type,
                "required": param.default == inspect.Parameter.empty
            }
            if _type == "array":
                element_type = typing.get_args(param.annotation)
                if len(element_type) != 1:
                    raise ValueError("Unexpected children field type length")
                spec["items"] = {"type": ArgumentsFiled.type_to_string(element_type[0])}
            arguments[param_name] = spec
        definition = Definition.init_from_dict(**{
            "type": cls.__name__,
            "description": extract_doc(cls),
            # "logo": get_img_b64(getattr(cls, 'LOGO', "")),
            "logo": "",
            "arguments": arguments
        })
        return definition

    def get_provider_type(self) -> str:
        return str(self.__class__)

    @abc.abstractmethod
    def get_defective_task(self) -> list[Task]:
        # This will be call every 1m, should return the list downloads
        # with none process or failed tasks, and then remove the download tasks
        # The return is a list of Task(url, path, link_type)
        pass

    @abc.abstractmethod
    def send_torrent_task(self, task: Task) -> TypeError:
        pass

    @abc.abstractmethod
    def send_magnet_task(self, task: Task) -> TypeError:
        pass

    @abc.abstractmethod
    def send_general_task(self, task: Task) -> TypeError:
        pass

    @abc.abstractmethod
    def remove_tasks(self, tasks: list[Task]):
        pass
