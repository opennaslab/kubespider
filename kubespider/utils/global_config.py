import logging
from utils import values
from utils.config_reader import YamlFileConfigReader
from utils.values import CFG_BASE_PATH


def get_global_config() -> YamlFileConfigReader:
    return YamlFileConfigReader(values.Config.KUBESPIDER_CONFIG.config_path())


cfg = get_global_config().read()


class Config(object):
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{CFG_BASE_PATH}kubespider.db"
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SECRET_KEY = "iECgbYWReMNxkRprrzMo5KAQYnb2UeZ3bwvReTSt+VSESW0OB8zbglT+6rEcDW9X"
    SESSION_USE_SIGNER = True
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = 86400 * 2
    LOG_LEVEL = logging.INFO
    AUTH_TOKEN = cfg.get('auth_token', None)
    PROXY = cfg.get('proxy', "")
    SERVER_PORT = cfg.get('server_port', 3080)
    DOWNLOAD_BASE_PATH = cfg.get("download", {}).get("base_path", "/downloads")
