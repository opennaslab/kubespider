# Used to define the general values used in the project
import hashlib
import os
from enum import Enum

from utils import types

FILE_TYPE_TO_PATH = {
    types.FileType.common: "Common",
    types.FileType.tv: "TV",
    types.FileType.movie: "Movie",
    types.FileType.video_mixed: "VideoMixed",
    types.FileType.music: "Music",
    types.FileType.picture: "Picture",
}
CFG_BASE_PATH = os.path.join(os.getenv('HOME'), '.config/')
CFG_TEMPLATE_PATH = os.path.join(os.getenv('HOME'), '.config_template/')


class Config(str, Enum):
    SOURCE_PROVIDER = 'source_provider.yaml'
    DOWNLOAD_PROVIDER = 'download_provider.yaml'
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

    def __init__(self, source: str, path: str = None, force=True, **kwargs):
        super().__init__(**kwargs)
        self.source = source
        self.path = path
        self.force = force


class SearchEvent(Extra):
    def __init__(self, keyword: str, page: int, path: str = None, search_providers: list = None, force=True, **kwargs):
        super().__init__(**kwargs)
        self.keyword = keyword
        self.page = page
        self.path = path
        self.force = force
        self.search_providers = search_providers or []


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

    def __init__(self, url: str, path: str, link_type: str = None, file_type: str = None, uid: str = None,
                 title: str = None, subtitle: str = None, desc: str = None, poster: list[str] = None, size: str = None,
                 publish_time: str = None, discover: str = None, plugin: str = None, **kwargs):
        super().__init__(**kwargs)
        self.url = url
        self.path = path
        self.link_type = link_type
        self.file_type = file_type
        self.uid = uid if uid else hashlib.md5(url.encode('utf-8')).hexdigest()
        self.title = title
        self.subtitle = subtitle
        self.desc = desc
        self.poster = poster
        self.size = size
        self.publish_time = publish_time
        self.discover_time = discover
        self.plugin = plugin

    @property
    def data(self):
        data = self.extra_params()
        data.update({
            "uid": self.uid,
            "url": self.url,
            "path": self.path,
            "file_type": self.file_type,
            "link_type": self.link_type,
            "title": self.title,
            "subtitle": self.subtitle,
            "desc": self.desc,
            "poster": self.poster,
            "size": self.size,
            "publish_time": self.publish_time,
            "discover_time": self.discover_time,
            "plugin": self.plugin
        })
        return data

    def __repr__(self):
        return f"<Resource {self.uid}>"


class Task(Extra):
    """
    Task, used to describe the task to be downloaded, input of the download provider
    """

    def __init__(self, url: str, path: str, link_type: str = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.url = url
        self.path = path
        self.link_type = link_type
        self.uid = None
