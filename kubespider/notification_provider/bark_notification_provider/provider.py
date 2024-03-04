from urllib.parse import urljoin
import logging

from notification_provider import provider
from utils.helper import get_request_controller


class BarkNotificationProvider(provider.NotificationProvider):
    """bark notification"""

    def __init__(self, host: str, device_token: str) -> None:
        """
        :param host: bark`s host
        :param device_token: bark`s device token
        """
        self.host = host
        self.device_token = device_token
        self.request_handler = get_request_controller()

    def push(self, title, **kwargs) -> bool:
        message = self.format_message(title, **kwargs)
        url = urljoin(self.host, "/push")
        headers = {
            'Content-Type': 'application/json; charset=utf-8'
        }
        data = {
            "body": message,
            "title": "Webhook: start download",
            "group": "kubespider",
            "icon": "https://ghproxy.com/https://raw.githubusercontent.com/opennaslab/kubespider/main/docs/images/logo.png",
            "device_key": self.device_token
        }
        response = self.request_handler.post(url, json=data, timeout=5, headers=headers).json()
        if response['code'] != 200:
            logging.error("Bark push failed : %s", response['message'])
            return False
        return True

    def format_message(self, title, **kwargs) -> str:
        message = []
        for key, value in kwargs.items():
            message.append(f"{key}: {value}")
        return "\n".join(message)
