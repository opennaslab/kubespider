import threading
import os
from abc import ABC, abstractmethod

import yaml


class AbsConfigReader(ABC):
    """
    Abstract class for config reader
    """

    @abstractmethod
    def read(self) -> dict:
        """
        Reads config from s specific store, like file or memory dict
        Each call of this function will read the latest data from the store
        """

    @abstractmethod
    def save(self, new_data: dict):
        """
        Saves new data to the store
        """


class FileConfigReader(AbsConfigReader):
    """
    Basic definition of file config loader
    """

    def __init__(self, file_path: str):
        self.file_path = file_path

    def read_file(self) -> str:
        if not os.path.exists(self.file_path):
            return ''
        with open(self.file_path, 'r', encoding='utf-8') as file:
            return file.read()

    def write_file(self, data_str: str):
        with open(self.file_path, 'w', encoding='utf-8') as file:
            file.write(data_str)


file_locks = {}


class YamlFileConfigReader(FileConfigReader):
    """
    A config reader that reads from a single yaml file, 
    or create one on first save call if not exists
    """

    def __init__(self, file_path: str):
        super().__init__(file_path)
        self.file_lock = file_locks.get(file_path, threading.Lock())
        file_locks[file_path] = self.file_lock

    def read(self) -> dict:
        self.file_lock.acquire()
        try:
            return self.read_data_from_file()
        finally:
            self.file_lock.release()

    def save(self, new_data: dict):
        self.file_lock.acquire()
        try:
            self.write_data_to_file(new_data)
        finally:
            self.file_lock.release()

    def parcial_update(self, update):
        self.file_lock.acquire()
        try:
            data = self.read_data_from_file()
            update(data)
            self.write_data_to_file(data)
        finally:
            self.file_lock.release()

    def read_data_from_file(self) -> dict:
        conf = yaml.safe_load(self.read_file())
        if conf is None:
            conf = {}
        return conf

    def write_data_to_file(self, data: dict):
        self.write_file(yaml.dump(data, allow_unicode=True, sort_keys=False))


class YamlFileSectionConfigReader(YamlFileConfigReader):
    """
    A config reader that reads from a section of yaml file
    """

    def __init__(self, file_path: str, section: str):
        super().__init__(file_path)
        self.section = section

    def read(self) -> dict:
        return super().read().get(self.section, {})

    def save(self, new_data: dict):
        super().parcial_update(lambda data: data.update({self.section: new_data}))
