from core.middleware.notification_provider.bark_notification_provider.provider import BarkNotificationProvider
from core.middleware.notification_provider.pushdeer_notification_provider.provider import PushDeerNotificationProvider
from core.middleware.notification_provider.qq_notification_provider.provider import QQNotificationProvider
from core.middleware.notification_provider.telegram_notification_provider.provider import TelegramNotificationProvider

providers = [
    BarkNotificationProvider,
    PushDeerNotificationProvider,
    QQNotificationProvider,
    TelegramNotificationProvider,
]
__all__ = (providers,)
