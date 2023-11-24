import hashlib
from io import BytesIO


class Resource:
    def __init__(self, **kwargs):
        self._uuid = kwargs.get("uuid")
        self.url = kwargs.get("url")
        self.path = kwargs.get("path")
        self.name = kwargs.get("name")
        self.file_type = kwargs.get("file_type")
        self.link_type = kwargs.get("link_type")
        self.content = kwargs.get("content")
        self.auto_download = kwargs.get("auto_download", False)

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

    @property
    def data(self):
        return {
            "uuid": self.uuid,
            "url": self.url,
            "path": self.path,
            "name": self.name,
            "file_type": self.file_type,
            "link_type": self.link_type,
            "auto_download": self.auto_download,
        }

    def __repr__(self):
        return f"<Resource {self.uuid} {self.name or ''}>"
