import os
import os.path as osp
from enum import Enum

import yaml

from utils.config_reader import YamlFileConfigReader, StructConfig

CFG_BASE_PATH = os.getenv('KUBESPIDER_HOME', '/data/kubespider')

default_yaml = """
---
log:
  level: 'INFO'
proxy: ""
webapi:
  server_port: 3080
  auth_token: ""
  secret_key: iECgbYWReMNxkRprrzMo5KAQYnb2UeZ3bwvReTSt+VSESW0OB8zbglT+6rEcDW9X
statemachine:
  task_queue_size: 100
  event_queue_size: 100
download:
  base_path: /downloads
"""

class PathConfig(str, Enum):
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


def get_global_config() -> YamlFileConfigReader:
    if not osp.exists(PathConfig.KUBESPIDER_CONFIG.config_path()):
        os.makedirs(CFG_BASE_PATH, exist_ok=True)
        os.makedirs(PathConfig.SOURCE_PROVIDERS_BIN.config_path(), exist_ok=True)
        data = yaml.safe_load(default_yaml)
        with open(PathConfig.KUBESPIDER_CONFIG.config_path(), 'w') as file:
            yaml.safe_dump(data, file)
    return YamlFileConfigReader(PathConfig.KUBESPIDER_CONFIG.config_path())

cfg: StructConfig = get_global_config().read()

class Config(object):
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{osp.join(CFG_BASE_PATH, 'kubespider.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SESSION_USE_SIGNER = True
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = 86400 * 2
    
    LOG_LEVEL = cfg.log.level
    PROXY = cfg.proxy
    
    SERVER_PORT = cfg.webapi.server_port
    AUTH_TOKEN = cfg.webapi.auth_token
    SECRET_KEY = cfg.webapi.secret_key
    
    DOWNLOAD_BASE_PATH = cfg.download.base_path
