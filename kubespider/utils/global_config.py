from utils.config_reader import YamlFileConfigReader
from api import values

def get_global_config() -> YamlFileConfigReader:
    return YamlFileConfigReader(values.Config.KUBESPIDER_CONFIG.config_path())

def get_auth_token() -> str:
    cfg = get_global_config().read()
    if cfg is not None:
        return cfg.get('auth_token', None)
    return None

def get_proxy() -> str:
    cfg = get_global_config().read()
    if cfg is not None:
        return cfg.get('proxy', None)
    return None

def get_server_port() -> int:
    cfg = get_global_config().read()
    if cfg is not None:
        return cfg.get('server_port', 3080)
    return 3080
