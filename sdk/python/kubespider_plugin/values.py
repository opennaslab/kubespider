from .utils import get_unique_hash


class Resource:
    def __init__(self, url: str, path: str = "", link_type: str = None, file_type: str = None, uid: str = None,
                 title: str = None, subtitle: str = None, desc: str = None, poster: list[str] = None, size: str = None,
                 publish_time: str = None, discover: str = None, plugin: str = None, **kwargs):
        """
        Resource, used to describe the resource to be downloaded, result of the source provider
        """
        self.url = url
        self.path = path
        self.link_type = link_type
        self.file_type = file_type
        self.uid = uid if uid else get_unique_hash(url)
        self.title = title
        self.subtitle = subtitle
        self.desc = desc
        self.poster = poster
        self.size = size
        self.publish_time = publish_time
        self.discover_time = discover
        self.plugin = plugin
        self._kwargs = kwargs

    @property
    def data(self):
        data = self._kwargs
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


class LinkType:
    general = "general"
    magnet = "magnet"
    torrent = "torrent"

    @classmethod
    def types(cls) -> list:
        return [cls.general, cls.magnet, cls.torrent]


class FileType:
    common = "common"
    general = "general"
    tv = "tv"
    movie = "movie"
    video_mixed = "video_mixed"
    video_9kg = "video_9kg"
    music = "music"
    picture = "picture"
    document = "document"

    @classmethod
    def types(cls) -> list:
        return [
            cls.common, cls.general, cls.tv, cls.movie, cls.video_mixed,
            cls.video_9kg, cls.music, cls.picture, cls.document
        ]


class KubespiderContext:
    proxy: str
    plugin_name: str
    plugin_port: str

    def __init__(self, **kwargs):
        self.proxy = kwargs.get("proxy", "")
        self.plugin_name = kwargs.get("name", "")
        self.plugin_port = kwargs.get("port", "")
