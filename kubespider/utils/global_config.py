import logging

from utils.config_reader import YamlFileConfigReader
from utils import values


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
    SESSION_USE_SIGNER = True
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = 86400 * 2

    LOG_LEVEL = cfg.get('log_level', logging.INFO)
    PROXY = cfg.get('proxy', "")

    SERVER_PORT = cfg.get("server_port", 3080)
    AUTH_TOKEN = cfg.get("auth_token")
    SECRET_KEY = cfg.get("secret_key")

    DOWNLOAD_BASE_PATH = cfg.get("download_base_path", "")
