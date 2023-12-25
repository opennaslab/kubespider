import logging
import threading
import os
from abc import ABC, abstractmethod

import yaml

class StructConfig:
    """
    StructConfig is a warp struct for dict config.
    
    Example:
    
    dictionary = {
        'A': 123,
        'B': {
            'b': 22,
        },
    }

    cfg = StructConfig(dictionary)

    print(cfg.a)   # 123
    print(cfg.B.B) # 22

    StructConfig will replace the yaml value from env

    Example:

    export A = 456
    export B_FOO = 'World'

    dictionary = {
        'A': 123,
        'B': {
            'foo': 'test'
        }
    }

    cfg = StructConfig(dictionary)
    
    print(cfg.a)     # 456
    print(cfg.B.FOO) # World
    
    """
    def __init__(self, dictionary, path="", env_prefix=""):
        self._data = {}
        self._env_prefix = env_prefix
        for key, value in dictionary.items():
            normalized_key = key.lower()
            full_key = f"{path}_{normalized_key}" if path else normalized_key
            self._data[normalized_key] = self._wrap(value, full_key)

    def _wrap(self, value, path):
        if isinstance(value, (tuple, list, set, frozenset)):
            return type(value)([self._wrap(v, path) for v in value])
        elif isinstance(value, dict):
            return StructConfig(value, path, self._env_prefix)
        else:
            if self._env_prefix:
                path = f"{self._env_prefix}_{path}"
            ev = os.getenv(path.upper())
            if not ev: return value
            return self._convert(ev, value)

    def __getattr__(self, key):
        normalized_key = key.lower()
        try:
            return self._data[normalized_key]
        except KeyError:
            raise AttributeError(f"'{type(self).__name__}' object has no attribute '{key}'")

    def __setattr__(self, key, value):
        if key == "_data":
            super().__setattr__(key, value)
        else:
            self._data[key.lower()] = value
    def __getitem__(self, key):
        try:
            return self._data[key.lower()]
        except KeyError:
            raise KeyError(f"Key '{key.lower()}' not found")

    def __setitem__(self, key, value):
        self._data[key.lower()] = value

    def __delitem__(self, key):
        normalized_key = key.lower()
        try:
            del self._data[normalized_key]
        except KeyError:
            raise KeyError(f"Key '{key}' not found")

    def __str__(self) -> str:
        return str(self._data)

    @staticmethod
    def _convert(value, original_value):
        """
        Keep the environment variable type the same as the yaml value type
        """
        original_type = type(original_value)
        try:
            if original_type == int:
                return int(value)
            elif original_type == float:
                return float(value)
            elif original_type == bool:
                return value.lower() in ('yes', 'true', 't', '1')
            else:
                return value
        except ValueError:
            logging.error(f"Error: Cannot convert '{value}' to {original_type}, using yaml vaule {original_value}")
            return original_value

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

    def read_data_from_file(self) -> StructConfig:
        conf = yaml.safe_load(self.read_file())
        if conf is None:
            conf = {}
        return StructConfig(conf, env_prefix="KUBESPIDER")

    def write_data_to_file(self, data: dict):
        self.write_file(yaml.dump(data, allow_unicode=True, sort_keys=False))


class YamlFileSectionConfigReader(YamlFileConfigReader):
    """
    A config reader that reads from a section of yaml file
    """

    def __init__(self, file_path: str, section: str):
        super().__init__(file_path)
        self.section = section

    def read(self) -> StructConfig:
        data = super().read()
        for s in self.section.split('.'):
            data = data[s]
        return data

    def save(self, new_data: dict):
        super().parcial_update(lambda data: data.update({self.section: new_data}))
