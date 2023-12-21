import os
from datetime import datetime
from flask_sqlalchemy import SQLAlchemy

from utils.config_reader import YamlFileConfigReader
from utils.helper import get_provider_conf_base_path
from utils.types import FileType, ProviderType
from utils.values import Resource as DownloadResource

db = SQLAlchemy()


class BaseModel(object):
    """base model，supplement create time and update time for models"""
    create_time = db.Column(db.DateTime, default=datetime.now)
    update_time = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)


class Resource(BaseModel, db.Model):
    __tablename__ = 'resource'

    uuid = db.Column(db.String(64), primary_key=True)
    finder = db.Column(db.String(64))
    size = db.Column(db.String(32))  # GB
    title = db.Column(db.String(64), nullable=False, default="")
    url = db.Column(db.String(64), nullable=False)
    resource_type = db.Column(db.Enum(*FileType.types()))
    display = db.Column(db.Boolean, default=True)
    is_download = db.Column(db.Boolean, default=False)
    download_path = db.Column(db.String(120), nullable=True)
    download_task_id = db.Column(db.String(120), nullable=True)
    desc = db.Column(db.Text)

    def to_dict(self):
        resp_dict = {
            "uuid": self.uuid,
            "finder": self.finder,
            "size": self.size,
            "title": self.title,
            "source": self.source,
            "is_read": self.is_read,
            "is_download": self.is_download,
            "download_path": self.download_path,
            "download_task_id": self.download_task_id,
            "desc": self.desc,
        }
        return resp_dict

    @classmethod
    def init_model(cls, **kwargs):
        model = cls()
        model.uuid = DownloadResource.get_uuid(kwargs.get('url'))
        model.finder = kwargs.get("finder")
        model.size = kwargs.get("size")
        model.title = kwargs.get("title")
        model.url = kwargs.get("url")
        model.resource_type = kwargs.get("resource_type")
        model.desc = kwargs.get("desc")
        return model


class ProviderInstance(BaseModel, db.Model):
    __tablename__ = 'provider_instance'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(32), nullable=False, unique=True)
    provider_name = db.Column(db.String(32), nullable=False)
    provider_type = db.Column(db.Enum(*ProviderType.provider_types()))
    enable = db.Column(db.Boolean, default=True)
    conf_file = db.Column(db.String(64), nullable=False)

    def to_dict(self):
        base_path = get_provider_conf_base_path(self.provider_type)
        conf = YamlFileConfigReader(
            os.path.join(base_path, self.conf_file)).read()
        resp_dict = {
            "id": self.id,
            "instance_name": self.name,
            "enable": self.enable,
            "conf_file": self.conf_file,
            "conf": conf,
        }
        return resp_dict


class ResourceStateMachine(BaseModel, db.Model):
    __tablename__ = 'resource_state_machine'

    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey("resource.uuid"))
    state = db.Column(db.String(32), nullable=False)
    flow = db.Column(db.Text)


class DownloadTasks(BaseModel, db.Model):
    __tablename__ = 'download_tasks'
    id = db.Column(db.Integer, primary_key=True)
    resource_id = db.Column(db.Integer, db.ForeignKey("resource.uuid"))
    provider_id = db.Column(db.Integer, db.ForeignKey("provider_instance.id"))
    task_id = db.Column(db.String(32), nullable=False)
