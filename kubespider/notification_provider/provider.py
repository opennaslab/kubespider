import abc
import inspect
from utils.helper import parse_func_doc, extract_doc, get_img_b64
from utils.types import ParamsType


class NotificationProvider(metaclass=abc.ABCMeta):
    NAME = ""

    @classmethod
    def definitions(cls) -> dict:
        init_func = getattr(cls, '__init__')
        signature = inspect.signature(init_func)
        arguments = []
        iter_items = iter(signature.parameters.items())
        params_doc = parse_func_doc(init_func)
        # skip self
        next(iter_items, None)
        for param_name, param in iter_items:
            arguments.append({
                "name": param_name,
                "description": params_doc.get(param_name, ""),
                "placeholder": params_doc.get(param_name, ""),
                "type": ParamsType.type_to_string(param.annotation),
                "required": param.default == inspect.Parameter.empty,
                "default": ""
            })
        return {
            "type": cls.__name__,
            "description": extract_doc(cls),
            "logo": get_img_b64(getattr(cls, 'LOGO', "")),
            "arguments": arguments
        }

    @abc.abstractmethod
    def push(self, title: str, **kwargs) -> bool:
        # push message
        pass

    @abc.abstractmethod
    def format_message(self, title, **kwargs) -> str:
        pass
