from notification_provider.provider import NotificationProvider
from notification_provider.bark_notification_provider.provider import BarkNotificationProvider
from notification_provider.pushdeer_notification_provider.provider import PushdeerNotificationProvider
from notification_provider.qq_notification_provider.provider import QQNotificationProvider
from notification_provider.telegram_notification_provider.provider import TelegramNotificationProvider

providers = [
    BarkNotificationProvider,
    PushdeerNotificationProvider,
    QQNotificationProvider,
    TelegramNotificationProvider,
]
__all__ = [
    'providers',
    'NotificationProvider',
    *map(lambda x: x.__name__, providers)
]
