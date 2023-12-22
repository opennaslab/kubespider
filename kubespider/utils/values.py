# Used to define the general values used in the project
import hashlib
import os
from enum import Enum
from io import BytesIO

from utils.config_reader import YamlFileConfigReader
from utils.types import FileType, DownloadStates

FILE_TYPE_TO_PATH = {
    FileType.common: "Common",
    FileType.tv: "TV",
    FileType.movie: "Movie",
    FileType.video_mixed: "VideoMixed",
    FileType.music: "Music",
    FileType.picture: "Picture",
    FileType.pt: "PT"
}

CFG_BASE_PATH = os.path.join(os.getenv('HOME'), '.config/')
CFG_TEMPLATE_PATH = os.path.join(os.getenv('HOME'), '.config_template/')


class Config(str, Enum):
    KUBESPIDER_CONFIG = 'kubespider.yaml'
    DEPENDENCIES_CONFIG = 'dependencies/'
    SOURCE_PROVIDERS_BIN = 'providers/source_bin'
    SOURCE_PROVIDERS_CONF = 'providers/source'
    DOWNLOAD_PROVIDERS_CONF = 'providers/download'
    NOTIFICATION_PROVIDERS_CONF = 'providers/notification'

    def __str__(self) -> str:
        return str(self.value)

    def config_path(self) -> str:
        return os.path.join(CFG_BASE_PATH, self)


class CallMode:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.support = kwargs.get("support")
        self.interval = kwargs.get("interval")


class InstanceParams:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name")
        self.value_type = kwargs.get("value_type")
        self.desc = kwargs.get("desc")
        self.nullable = kwargs.get("nullable")


class SourceProviderConf:
    def __init__(self, **kwargs):
        self.provider_name = kwargs.get("provider_name")
        self.provider_type = kwargs.get("provider_type")
        self.version = kwargs.get("version")
        self.language = kwargs.get("language")
        self.desc = kwargs.get("desc")
        self.logo = kwargs.get("logo")
        self.author = kwargs.get("author")
        self.call_mode = kwargs.get("call_mode")
        self.instance_params = kwargs.get("instance_params")

    def _gen_call_mode(self, modes):
        return [CallMode(**mode) for mode in modes]

    def _gen_instance_params(self, params):
        return [CallMode(**mode) for mode in params]


class Extra:

    def __init__(self, **kwargs) -> None:
        self.extra = {}
        self.extra.update(kwargs)

    def extra_param(self, key: str, default_value=None):
        return self.extra.get(key, default_value)

    def extra_params(self) -> dict:
        return self.extra

    def put_extra_params(self, extra: dict) -> None:
        if extra is None:
            return
        self.extra.update(extra)


class Event(Extra):
    """
    Download event, used to notify kubespider to download the resource
    """

    def __init__(self, source: str, path: str = None, **kwargs):
        super().__init__(**kwargs)
        self.source = source
        self.path = path


class Resource:
    def __init__(self, **kwargs):
        self._uuid = kwargs.get("uuid")
        self.url = kwargs.get("url")
        self.path = kwargs.get("path")
        self.name = kwargs.get("name")
        self.file_type = kwargs.get("file_type")
        self.content = kwargs.get("content")
        self.auto_download = kwargs.get("auto_download", False)
        self.download_provider_id = kwargs.get("download_provider_id")
        self.download_task = DownloadTask(
            url=self.url,
            path=self.path,
        )

    @property
    def uuid(self):
        if not self._uuid:
            if self.url:
                self._uuid = hashlib.md5(self.url.encode('utf-8')).hexdigest()
            elif self.content:
                self._uuid = hashlib.md5(self.content.read()).hexdigest()
            else:
                raise ValueError("Invalid resource")
        return self._uuid

    @staticmethod
    def get_uuid(url: str = None, content: BytesIO = None):
        if url:
            return hashlib.md5(url.encode('utf-8')).hexdigest()
        elif content:
            return hashlib.md5(content.read()).hexdigest()
        else:
            raise ValueError("Invalid params")

    def choose_download_provider(self, providers):
        return

    def __repr__(self):
        return f"<Resource {self.uuid} {self.name or ''}>"


class DownloadTask:
    """
    Task, used to describe the task to be downloaded, input of the download provider
    """

    def __init__(self, **kwargs):
        self.download_task_id = ""
        self.download_path = self._get_download_path(kwargs.get('path'))
        self.url = kwargs.get("url")
        self.content = None
        self._status = None  # DownloadStates
        self.files = []
        self.total_length = None

    def set_status(self, status):
        if status in DownloadStates.download_states:
            self._status = status
        else:
            raise ValueError("Invalid download status")

    @staticmethod
    def _get_download_path(path):
        cfg = YamlFileConfigReader(Config.KUBESPIDER_CONFIG.config_path()).read()
        download_base_path = cfg.get("download", {}).get("base_path", "/downloads")
        if path:
            if path.startswith('/'):
                return path
            else:
                return os.path.join(download_base_path, path)
        else:
            return download_base_path

    @property
    def status(self):
        return self._status


class ProviderApiSaveParams:
    def __init__(self, **kwargs):
        self.kwargs = kwargs
        self._data = None
        self.is_validate = None
        self.error = ""
        self.id = None
        self.instance_name = None
        self.provider_name = None
        self.provider_type = None

    def validate(self, manager) -> bool:
        if self.is_validate is None:
            self.id = self.kwargs.pop("id", None)
            if self.id:
                exist = manager.get_instance_confs(instance_id=self.id)
                if not exist:
                    self.error = "instance not exist"
                    self.is_validate = False
                    return self.is_validate
            self.provider_name = self.kwargs.get("provider_name")
            self.provider_type = self.kwargs.get("provider_type")
            instance_params = self.kwargs.get("instance_params", [])
            if not instance_params:
                self.error = "instance params missing"
                self.is_validate = False
                return self.is_validate
            for param in instance_params:
                if param.get("name") == "name":
                    self.instance_name = param.get("value")
            if not self.instance_name:
                self.error = "instance name missing"
                self.is_validate = False
                return self.is_validate
            if not self.id:
                conf = manager.get_instance_confs(instance_name=self.instance_name)
                if conf:
                    self.error = "instance name already exist"
                    self.is_validate = False
                    return self.is_validate
            self.is_validate = True
            return self.is_validate
        else:
            return self.is_validate

    @property
    def data(self):
        return self.kwargs


class SourceProviderApi:
    search = "search"
    schedule = "schedule"
    handler = "handler"
    document = "document"
    health = "health"

    @classmethod
    def get_apis(cls):
        return [cls.search, cls.schedule, cls.handler, cls.document]
