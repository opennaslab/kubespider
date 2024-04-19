from models import Download, Notification
from utils.helper import translate_provider_type
from utils.values import Config
from utils.config_reader import YamlFileConfigReader


def init_download_table(session):
    """init download provider to database if it doesn't exist"""
    download_config = YamlFileConfigReader(Config.DOWNLOAD_PROVIDER.config_path()).read()
    for key, config in download_config.items():
        download_type = config.pop('type', None)
        enable = config.pop('enable', None)
        name = config.get('name', None) or key
        download_provider = session.query(Download).filter_by(name=name).first()
        if not download_provider:
            download_provider = Download()
            download_provider.name = name
            download_provider.type = translate_provider_type(download_type)
            download_provider.config = config
            download_provider.enable = enable
            session.add(download_provider)
            session.commit()


def init_notification_table(session):
    """init notification provider to database if it doesn't exist"""
    notification_config = YamlFileConfigReader(Config.NOTIFICATION_PROVIDER.config_path()).read()

    for key, config in notification_config.items():
        notification_type = config.pop('type', None)
        enable = config.pop('enable', None)
        name = config.get('name', None) or key
        notification_provider = session.query(Notification).filter_by(name=name).first()
        if not notification_provider:
            notification_provider = Notification()
            notification_provider.name = name
            notification_provider.type = translate_provider_type(notification_type)
            notification_provider.config = config
            notification_provider.enable = enable
            session.add(notification_provider)
            session.commit()
