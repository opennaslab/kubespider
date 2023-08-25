from urllib.parse import urljoin
import logging

from notification_provider import provider
from utils.config_reader import AbsConfigReader
from utils.helper import get_request_controller

class BarkNotificationProvider(provider.NotificationProvider):
    def __init__(self, name: str, config_reader: AbsConfigReader) -> None:
        super().__init__(name, config_reader)
        self.name = name
        self.enable, self.host, self.device_token = self._init_conf(config_reader)
        self.request_handler = get_request_controller()

    @staticmethod
    def _init_conf(config_reader: AbsConfigReader):
        conf = config_reader.read()
        return conf.get("enable", True), conf.get("host"), conf.get("device_token")

    def get_provider_name(self) -> str:
        return self.name

    def provider_enabled(self) -> bool:
        return self.enable

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
