from .utils import get_unique_hash


class ProviderType:
    _registry = {}

    def __init__(self, name: str, api_list: list[str]) -> None:
        self.name = name
        self.api_list = api_list
        ProviderType._registry[name] = self

    @staticmethod
    def get_provider_type(name: str):
        return ProviderType._registry.get(name, None)


class Resource:
    def __init__(self, **kwargs):
        self._uuid = kwargs.pop("uuid", None)
        self.url = kwargs.pop("url", "")
        self.path = kwargs.pop("path", "")
        self.title = kwargs.pop("title", "")
        self.file_type = kwargs.pop("file_type", "")
        self.link_type = kwargs.pop("link_type", "")
        self.auto_download = kwargs.pop("auto_download", False)
        self.kwargs = kwargs

    @property
    def uuid(self):
        if not self._uuid:
            if self.url:
                self._uuid = get_unique_hash(self.url)
            else:
                raise ValueError(f"Invalid resource: {self}")
        return self._uuid

    @property
    def data(self):
        data = self.kwargs
        data.update({
            "uuid": self.uuid,
            "url": self.url,
            "path": self.path,
            "title": self.title,
            "file_type": self.file_type,
            "link_type": self.link_type,
            "auto_download": self.auto_download,
        })
        return data

    def __repr__(self):
        return f"<Resource {self.title or ''} {self.uuid}>"


class LinkType:
    general = "general"
    magnet = "magnet"
    torrent = "torrent"


class FileType:
    common = "common"
    general = "general"
    tv = "tv"
    movie = "movie"
    video_mixed = "video_mixed"
    music = "music"
    picture = "picture"
    pt = "pt"
    document = "document"


ProviderType.parser = ProviderType("parser", ["get_links", "should_handle"])
ProviderType.search = ProviderType("search", ["search"])
