import logging
import os
from utils.config_reader import YamlFileConfigReader
from utils import values
from utils.values import CFG_BASE_PATH
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore


def get_global_config() -> YamlFileConfigReader:
    return YamlFileConfigReader(values.Config.KUBESPIDER_CONFIG.config_path())


cfg = get_global_config().read()


def get_auth_token() -> [str, None]:
    if cfg is not None:
        return cfg.get('auth_token', None)
    return None


def get_proxy() -> [str, None]:
    if cfg is not None:
        return cfg.get('proxy', None)
    return None


def get_server_port() -> int:
    if cfg is not None:
        return cfg.get('server_port', 3080)
    return 3080


def auto_change_download_provider() -> bool:
    if cfg is not None:
        return bool(cfg.get('auto_change_download_provider', False))
    return False


def get_telegram_bot_token() -> [str, None]:
    if cfg is not None:
        return cfg.get('telegram_bot_token', None)
    return None


def get_telegram_username() -> [str, None]:
    if cfg is not None:
        return cfg.get('telegram_username', None)
    return None


class APPConfig:
    # database
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(CFG_BASE_PATH, 'kubespider.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # scheduler
    SCHEDULER_JOBSTORES = {
        'default': SQLAlchemyJobStore(url=f"sqlite:///{os.path.join(CFG_BASE_PATH, 'kubespider.db')}")
    }
    SCHEDULER_API_ENABLED = False

    LOG_LEVEL = cfg.get('log_level', logging.INFO)
    PROXY = cfg.get('proxy', "")

    SERVER_PORT = cfg.get("server_port", 3080)
    AUTH_TOKEN = cfg.get("auth_token")
    SECRET_KEY = cfg.get("secret_key")

    DOWNLOAD_BASE_PATH = cfg.get("download_base_path", "")
