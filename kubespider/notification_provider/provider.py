import abc
import inspect
import typing

from utils.helper import parse_func_doc, extract_doc
from utils.definition import Definition, ArgumentsFiled


class NotificationProvider(metaclass=abc.ABCMeta):
    def __init__(self, name: str):
        self.name = name

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

    @abc.abstractmethod
    def push(self, title: str, **kwargs) -> bool:
        # push message
        pass

    @abc.abstractmethod
    def format_message(self, title, **kwargs) -> str:
        pass
