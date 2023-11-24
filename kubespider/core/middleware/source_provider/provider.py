import abc
import datetime
import inspect
import subprocess
import time


class SourceProvider(metaclass=abc.ABCMeta):
    @abc.abstractmethod
    def __init__(self, name: str) -> None:
        self.name = name
        self.is_active = False

    def is_alive(self):
        pass

    @staticmethod
    def spec():
        pass

    @abc.abstractmethod
    def search(self, keyword: str, sync=False, **kwargs) -> list:
        pass

    @abc.abstractmethod
    def schedule(self, sync=False, **kwargs) -> bool:
        pass

    @abc.abstractmethod
    def handler(self, sync=True, **kwargs) -> list:
        pass

    @abc.abstractmethod
    def document(self, sync=True, **kwargs) -> dict:
        pass

    def __repr__(self):
        return f"<SourceProvider {self.name}>"
