from datetime import datetime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, String, JSON, Boolean, Enum, DateTime, Integer, ForeignKey, Text
from sqlalchemy.orm import relationship

from utils.types import FileType, LinkType

Base = declarative_base()


class BaseModel(object):
    """base model，supplement create time and update time for models"""
    create_time = Column(DateTime, default=datetime.now)
    update_time = Column(DateTime, default=datetime.now, onupdate=datetime.now)


class Download(BaseModel, Base):
    __tablename__ = 'download'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    type = Column(String(32), nullable=False)
    config = Column(JSON)
    enable = Column(Boolean, default=True)

    def serializer(self):
        resp_dict = {
            "id": self.id,
            "name": self.name,
            "enable": self.enable,
            "config": self.config,
        }
        return resp_dict


class Notification(BaseModel, Base):
    __tablename__ = 'notification'

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    type = Column(String(32), nullable=False)
    config = Column(JSON)
    enable = Column(Boolean, default=True)

    def serializer(self):
        resp_dict = {
            "id": self.id,
            "name": self.name,
            "enable": self.enable,
            "config": self.config,
        }
        return resp_dict


class Plugin(BaseModel, Base):
    __tablename__ = 'plugin'
    TYPE = ("parser", "search", "scheduler")

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    version = Column(String(32), nullable=False)
    author = Column(String(32))
    type = Column(Enum(*TYPE))
    description = Column(String(128))
    language = Column(String(16))
    logo = Column(String(128))
    binary = Column(String(128), nullable=False)
    arguments = Column(JSON)
    enable = Column(Boolean, default=False)

    bindings = relationship('Binding', backref='plugin', lazy=False)
    resources = relationship('Resource', backref='plugin', lazy=False)

    def serializer(self) -> dict:
        resp_dict = {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "author": self.author,
            "type": self.type,
            "description": self.description,
            "language": self.description,
            "logo": self.logo,
            "binary": self.binary,
            "arguments": self.arguments,
            "enable": self.enable,
        }
        return resp_dict


class Binding(BaseModel, Base):
    __tablename__ = 'binding'
    TYPE = ("parser", "search", "scheduler")

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(32), nullable=False, unique=True)
    type = Column(Enum(*TYPE))
    arguments = Column(JSON)
    plugin_id = Column(Integer, ForeignKey('plugin.id'), nullable=False)

    def serializer(self) -> dict:
        resp_dict = {
            "id": self.id,
            "name": self.name,
            "type": self.type,
            "arguments": self.arguments,
            "plugin_name": self.plugin.name,
        }
        return resp_dict


class PeriodTask(BaseModel, Base):
    __tablename__ = 'period_task'
    TASK_TYPE = ("search", "scheduler")
    TIGGER_TYPE = ("interval",)  # TODO ("date", "interval", "cron")

    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False, unique=True)
    task_type = Column(Enum(*TASK_TYPE))
    tigger_type = Column(Enum(*TIGGER_TYPE))
    tigger_config = Column(JSON)
    arguments = Column(JSON)
    binding_ids = Column(String(16), default="")
    enable = Column(Boolean, default=False)

    def serializer(self) -> dict:
        serializer = {
            "id": self.id,
            "name": self.name,
            "task_type": self.task_type,
            "tigger_type": self.tigger_type,
            "tigger_config": self.tigger_config,
            "arguments": self.arguments,
            "enable": self.enable
        }
        return serializer


class Resource(BaseModel, Base):
    __tablename__ = 'resource'

    uid = Column(String(64), primary_key=True)
    url = Column(String(128), nullable=False)
    path = Column(String(64), default="")
    link_type = Column(Enum(*FileType.types()))
    file_type = Column(Enum(*LinkType.types()))
    title = Column(String(128), default="")
    subtitle = Column(String(128), default="")
    desc = Column(Text)
    poster = Column(String(256))
    size = Column(String(32))
    publish_time = Column(DateTime)
    discover_time = Column(DateTime)
    plugin_id = Column(Integer, ForeignKey('plugin.id'), nullable=True)
    is_read = Column(Boolean, default=False)
    is_download = Column(Boolean, default=False)

    def serializer(self):
        serializer = {
            "uid": self.uid,
            "url": self.url,
            "path": self.path,
            "link_type": self.link_type,
            "file_type": self.file_type,
            "title": self.title,
            "subtitle": self.subtitle,
            "desc": self.desc,
            "poster": self.poster,
            "size": self.size,
            "publish_time": self.publish_time,
            "discover_time": self.discover_time,
            "plugin_id": self.plugin_id,
            "is_read": self.is_read,
            "is_download": self.is_download,
        }
        return serializer
