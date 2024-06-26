# Used to define the general values used in the project

import os
from enum import Enum
import hashlib

from api import types

FILE_TYPE_TO_PATH = {
    types.FILE_TYPE_COMMON: "Common",
    types.FILE_TYPE_VIDEO_TV: "TV",
    types.FILE_TYPE_VIDEO_MOVIE: "Movie",
    types.FILE_TYPE_VIDEO_MIXED: "VideoMixed",
    types.FILE_TYPE_MUSIC: "Music",
    types.FILE_TYPE_PICTIRE: "Picture",
    types.FILE_TYPE_PT: "PT"
}

CFG_BASE_PATH = os.path.join(os.getenv('HOME'), '.config/')
CFG_TEMPLATE_PATH = os.path.join(os.getenv('HOME'), '.config_template/')


class Config(str, Enum):
    SOURCE_PROVIDER = 'source_provider.yaml'
    DOWNLOAD_PROVIDER = 'download_provider.yaml'
    PT_PROVIDER = 'pt_provider.yaml'
    NOTIFICATION_PROVIDER = 'notification_provider.yaml'
    KUBESPIDER_CONFIG = 'kubespider.yaml'
    DEPENDENCIES_CONFIG = 'dependencies/'
    STATE = 'state.yaml'

    def __str__(self) -> str:
        return str(self.value)

    def config_path(self) -> str:
        return os.path.join(CFG_BASE_PATH, self)


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


class Downloader(Extra):
    """
    Downloader, used to bind downloader to source provider
    """

    def __init__(self, download_provider_type: str = None, download_provider_names: list[str] = None, **kwargs):
        super().__init__(**kwargs)
        self.download_provider_type = download_provider_type
        self.download_provider_names = download_provider_names


class Resource(Extra):
    """
    Resource, used to describe the resource to be downloaded, result of the source provider
    """

    def __init__(self, url: str, path: str,
                 link_type: str = None, file_type: str = None, uid: str = None,
                 **kwargs):
        super().__init__(**kwargs)
        self.url = url
        self.path = path
        self.link_type = link_type
        self.file_type = file_type
        self.uid = uid if uid else hashlib.md5(url.encode('utf-8')).hexdigest()


class Task(Extra):
    """
    Task, used to describe the task to be downloaded, input of the download provider
    """

    def __init__(self, url: str, path: str, link_type: str = None, **kwargs) -> None:
        super().__init__(**kwargs)
        # url is the download url or torrent file path
        # For example: http://xxx.com/x.jpg or /tmp/a.torrent
        self.url = url
        # Path is the path to save the file, like /Movie
        self.path = path
        self.link_type = link_type
        self.uid = None
